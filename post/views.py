from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from channel.permissions import IsSuperPermitted
from helpers.res import generateResponse
from channel.models import Channel, Publisher
from .serializers.main import NewsCreateSerializer
from .permissions import CRUDOpsPermission
from shortuuid import uuid
from helpers.cloud import Cloud

# Create your views here.
class CRUDView(APIView):
    permission_classes = [CRUDOpsPermission]
    """
    * A view class for performig CRUD ops on news
    """

    def post(self, req):
        """
        * Method for creating a news
        * Required data:
            > title
            > content
            > channel (public id)
        * Optional data:
            > tags
            > media (media)
        """
        title = req.data.get("title", None)
        content = req.data.get("content", None)
        tags = req.data.get("tags", [])
        channel_public_id = req.data.get("channel", None)

        if not title or not content:
            return Response(generateResponse(err="title and content are required"))
        channel_filt = Channel.objects.filter(public_id=channel_public_id)
        if not channel_filt:
            return Response(generateResponse(err="channel does not exist"))
        channel = channel_filt[0]
        publisher_filt = Publisher.objects.filter(user=req.user, channel=channel)
        if not publisher_filt:
            return Response(generateResponse(err="publisher does not exist"))
        publisher = publisher_filt[0]
        req_data = {
            "title": title,
            "publisher": publisher.pk,
            "channel": channel.pk,
            "tags": tags,
            "content": content,
        }

        ser_data = NewsCreateSerializer(data=req_data)
        if not ser_data.is_valid():
            tag_err = ser_data.errors.get("tags", None)
            if tag_err:
                return Response(
                    generateResponse(err="one of the provided tags does not exist")
                )

        #
        public_id = uuid()
        if req.FILES:
            try:
                media_list = req.FILES.getlist("media")
                cloud  = Cloud("news")
                res = cloud.multiple_upload(media_list)
                err = res.get("err", None)
                result = res.get("result", None)
                
                if err:
                    return Response(generateResponse(err=err))
                ser_data.save(public_id=public_id, media = result)
                return Response(generateResponse({"public_id": public_id}))
            except Exception as e:
                print(e)
                print(e.__dict__)
                return Response(generateResponse(err="something went wrong"))
            
        ser_data.save(public_id=public_id)
        # return Response(generateResponse("public_id: public_id"))
        return Response(generateResponse({"public_id": public_id}))
