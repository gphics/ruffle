from django.shortcuts import render
from rest_framework.response import Response
from .utils.main import CloudStorage
from rest_framework.views import APIView
from .utils.auth import validate_auth
from .models import StorageManager as Storage
from shortuuid import uuid
from .utils.serializers import ReadStorageSerializer
from .utils.auth import validate_auth
from .utils.genRes import generateResponse


class Cloud(APIView):
    """
    > A class responsible for all CRUD operations on media storage
    > Each request requires an authorization header
    > Each request bears a sear param called "folder" which signifies where to place object in the bucket
    > All methods requires the authorization header except the GET method
    """

    def post(self, req):
        """
        > This method requires the auth token header
        """
        #####
        # Authentication start
        ####
        Token = req.headers.get("Token", None)
        if not Token:
            return Response(
                generateResponse(err={"msg": "Auth token must be provided"})
            )
        auth_res = validate_auth(Token)
        auth_err = auth_res.get("err", None)
        auth_err_detail = auth_res.get("detail", None)
        if auth_err:
            return Response(generateResponse(err={"msg": auth_err["msg"]}))
        if auth_err_detail:
            return Response(generateResponse(err={"msg": auth_err_detail}))
        #####
        # Authentication end
        ####
        folder = req.GET.get("folder", None)
        many = req.GET.get("many", False)
        if not folder:
            return Response(generateResponse(err={"msg": "folder must be provided"}))

        media = req.FILES.get("media", None)
        if not media:
            return Response(generateResponse(err={"msg": "media must be provided"}))
        try:
            cloud = CloudStorage(folder)
            if not many:
                obj = cloud.upload(media)
                key = obj["key"]
                url = obj["url"]
                content_type = obj["content_type"]
                public_id = uuid()
                Storage.objects.create(
                    key=key,
                    url=url,
                    content_type=content_type,
                    public_id=public_id,
                    folder=folder,
                )
                return Response(generateResponse({"msg": public_id}))
            else:
                media_list = req.FILES.getlist("media")
                result = cloud.multiple_upload(media_list)
                output = []
                for obj in result:
                    key = obj["key"]
                    url = obj["url"]
                    content_type = obj["content_type"]
                    public_id = uuid()
                    Storage.objects.create(
                        key=key,
                        url=url,
                        content_type=content_type,
                        public_id=public_id,
                        folder=folder,
                    )
                    output.append(public_id)
                return Response(generateResponse({"msg": output}))

        except Exception as e:
            print(e)
            return Response(generateResponse(err={"msg": "something went wrong"}))

    def put(self, req):
        """
        > This method require the public_id of the object to be updated as a url query param
        """
        #####
        # Authentication start
        ####
        Token = req.headers.get("Token", None)
        if not Token:
            return Response(
                generateResponse(err={"msg": "Auth token must be provided"})
            )
        auth_res = validate_auth(Token)
        auth_err = auth_res.get("err", None)
        auth_err_detail = auth_res.get("detail", None)
        if auth_err:
            return Response(generateResponse(err={"msg": auth_err["msg"]}))
        if auth_err_detail:
            return Response(generateResponse(err={"msg": auth_err_detail}))
        #####
        # Authentication end
        ####
        media = req.FILES.get("media", None)
        public_id = req.GET.get("id", None)
        if not media:
            return Response(generateResponse(err={"msg": "media must be provided"}))
        if not public_id:
            return Response(generateResponse(err={"msg": "public_id must be provided"}))
        first = Storage.objects.filter(public_id=public_id)
        if not first.exists():
            return Response(
                generateResponse(err={"msg": "media object does not exist"})
            )
        second = first[0]
        try:
            cloud = CloudStorage(second.folder)
            result = cloud.update(second.key, media)
            if not result:
                return Response(generateResponse(err={"msg": "something went wrong"}))
            second.url = result["url"]
            second.content_type = result["content_type"]
            second.key = result["key"]
            second.save()
            return Response(generateResponse({"msg": "media updated successfully"}))

        except Exception as e:
            return Response(generateResponse(err={"msg": "something went wrong"}))

    def get(self, req):
        """
        > This method requires the public_id as "id" url query param
        """

        public_id = req.GET.get("id", None)
        if not public_id:
            return Response({"data": None, "err": "public_id must be provided"})
        first = Storage.objects.filter(public_id=public_id)
        if not first.exists():
            return Response({"data": None, "err": "media object does not exist"})
        second = ReadStorageSerializer(instance=first[0]).data
        return Response(generateResponse({"msg":second}))

    def delete(self, req):
        """
        > This method requires the public_id as "id" url query param
        """
        #####
        # Authentication start
        ####
        Token = req.headers.get("Token", None)
        if not Token:
            return Response(
                generateResponse(err={"msg": "Auth token must be provided"})
            )
        auth_res = validate_auth(Token)
        auth_err = auth_res.get("err", None)
        auth_err_detail = auth_res.get("detail", None)
        if auth_err:
            return Response(generateResponse(err={"msg": auth_err["msg"]}))
        if auth_err_detail:
            return Response(generateResponse(err={"msg": auth_err_detail}))
        #####
        # Authentication end
        ####
        public_id = req.GET.get("id", None)
        if not public_id:
            return Response(generateResponse(err={"msg": "public_id must be provided"}))
        first = Storage.objects.filter(public_id=public_id)
        if not first.exists():
            return Response(
                generateResponse(err={"msg": "media object does not exists"})
            )
        try:
            cloud = CloudStorage()
            second = cloud.delete(first[0].key)
            if not second:
                return Response(generateResponse(err={"msg": "something went wrong"}))
            first.delete()
            return Response(generateResponse({"msg": "media deleted"}))

        except Exception as e:
            return Response(
                generateResponse(err={"msg": "media object does not exists"})
            )
