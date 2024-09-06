from django.shortcuts import render
from rest_framework.response import Response
from .utils.main import CloudStorage
from rest_framework.views import APIView
from .utils.auth import validate_auth
from .models import StorageManager as Storage
from shortuuid import uuid
from .utils.serializers import ReadStorageSerializer

# Create your views here.


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
        folder = req.GET.get("folder", None)
        many = req.GET.get("many", False)
        if not folder:
            return Response({"data": None, "err": "folder must be provided"})

        media = req.FILES.get("media", None)
        if not media:
            return Response({"data": None, "err": "media must be provided"})
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
                return Response({"data": public_id, "err": None})
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
                return Response({"data": output, "err": None})

        except Exception as e:
            print(e)
            return Response({"data": None, "err": "something went wrong"})

    def put(self, req):
        """
        > This method require the public_id of the object to be updated as a url query param
        """
        media = req.FILES.get("media", None)
        public_id = req.GET.get("id", None)
        if not media:
            return Response({"data": None, "err": "media must be provided"})
        if not public_id:
            return Response({"data": None, "err": "public_id must be provided"})
        first = Storage.objects.filter(public_id=public_id)
        if not first.exists():
            return Response({"data": None, "err": "media object does not exist"})
        second = first[0]
        try:
            cloud = CloudStorage(second.folder)
            result = cloud.update(second.key, media)
            if not result:
                return Response({"data": None, "err": "something went wrong"})
            second.url = result["url"]
            second.content_type = result["content_type"]
            second.key = result["key"]
            second.save()
            return Response({"data": "media updated successfully", "err": None})

        except Exception as e:
            return Response({"data": None, "err": "something went wrong"})

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
        second = ReadStorageSerializer(instance=first[0])
        return Response({"data": second.data, "err": None})

    def delete(self, req):
        """
        > This method requires the public_id as "id" url query param
        """
        public_id = req.GET.get("id", None)
        if not public_id:
            return Response({"data": None, "err": "public_id must be provided"})
        first = Storage.objects.filter(public_id=public_id)
        if not first.exists():
            return Response({"data": None, "err": "media object does not exist"})
        try:
            cloud = CloudStorage()
            second = cloud.delete(first[0].key)
            if not second:
                return Response({"data": None, "err": "something went wrong"})
            first.delete()
            return Response({"data": "media deleted", "err": None})

        except Exception as e:
            return Response({"data": None, "err": "media object does not exist"})
