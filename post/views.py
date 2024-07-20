from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from channel.permissions import IsSuperPermitted
from helpers.res import generateResponse
from channel.models import Channel, Publisher
from .serializers.main import NewsCreateSerializer
from .permissions import NewsCreatePermission, NewsUpdatePermission
from shortuuid import uuid
from helpers.bucket import CloudManager
from .models import News
from supports.models import Tag
from django.template.defaultfilters import slugify


# Create your views here.
class NewsCreateView(APIView):
    permission_classes = [NewsCreatePermission]

    def post(self, req):
        """
        * Method for creating a news
        * Required data:
            > title
            > content
            > channel (public id)
        * Optional data:
            > tags (pk)
            > media (media)
        """
        title = req.data.get("title", None)
        content = req.data.get("content", None)
        tags = req.data.get("tags", [])
        channel_public_id = req.data.get("channel", None)

        if not title or not content:
            return Response(
                generateResponse(err="title and content are required"), status=400
            )
        channel_filt = Channel.objects.filter(public_id=channel_public_id)
        if not channel_filt:
            return Response(generateResponse(err="channel does not exist"), status=404)
        channel = channel_filt[0]
        publisher_filt = Publisher.objects.filter(user=req.user, channel=channel)
        if not publisher_filt:
            return Response(
                generateResponse(err="publisher does not exist"), status=404
            )
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
                    generateResponse(err="one of the provided tags does not exist"),
                    status=404,
                )
        public_id = uuid()
        if req.FILES:
            try:
                media_list = req.FILES.getlist("media")
                if not media_list or not len(media_list):
                    return Response(
                        generateResponse(err="the field name must be media"), status=400
                    )
                cloud = CloudManager("ruffle", "news")
                content_types = []
                for x in media_list:
                    content_types.append(x.content_type)
                is_valid = cloud.multiple_validate_allowed_types(content_types)
                if not is_valid:
                    return Response(
                        generateResponse(
                            err="invalid file format, check and try again"
                        ),
                        status=400,
                    )
                media = cloud.multiple_upload(media_list)
                ser_data.save(public_id=public_id, media=media)
                return Response(generateResponse({"public_id": public_id}))
            except Exception as e:
                print(e)
                return Response(
                    generateResponse(err="something went wrong"), status=400
                )

        ser_data.save(public_id=public_id)
        return Response(generateResponse({"public_id": public_id}), status=202)


class NewsUpdateView(APIView):
    permission_classes = [NewsUpdatePermission]

    def put(self, req):
        """
        * A method for updating a news
        * Required url query param:
            > news (public_id)
        * All data are optional but at least one data must be provided

        """
        news_public_id = req.GET.get("news", None)
        if not news_public_id:
            return Response(
                generateResponse(err="news public id must be provided"), status=400
            )
        # getting the news object
        filtrate = News.objects.filter(public_id=news_public_id)
        if not filtrate:
            return Response(generateResponse(err="news does not exist"), status=404)
        news = filtrate[0]
        # getting and setting the provided data
        title = req.data.get("title", news.title)
        content = req.data.get("content", news.content)
        slug = slugify(title)
        # [pk...]
        tags = req.data.get("tags", None)
        # validating the tags
        if tags:
            is_valid = True
            for t in tags:
                state = Tag.objects.filter(pk=t).exists()
                if not state:
                    is_valid = state
                    break
            if not is_valid:
                return Response(generateResponse(err="some tags not found"), status=404)
        else:
            tags = news.tags
        media = news.media or []
        # checking for media
        if req.FILES:
            cloud = CloudManager("ruffle", "news")
            media_list = req.FILES.getlist("media")
            if not media_list or not len(media_list):
                return Response(
                    generateResponse(err="the field name must be media"), status=400
                )
            # validating media type
            content_types = []
            for x in media_list:
                content_types.append(x.content_type)
            is_valid_type = cloud.multiple_validate_allowed_types(content_types)
            if not is_valid_type:
                return Response(
                    generateResponse(err="invalid file format present"), status=400
                )
            # uploading the media
            try:
                uploads = cloud.multiple_upload(media_list)
                for u in uploads:
                    media.append(u)
            except Exception as e:
                print(e)
                return Response(
                    generateResponse(err="something went wrong"), status=500
                )

        # updating and saving the news
        news.title = title
        news.content = content
        news.slug = slug
        news.media = media
        p_filterate = Publisher.objects.filter(user=req.user, channel=news.channel)
        publisher = p_filterate[0]
        news.updated_by = publisher
        news.save()
        return Response(generateResponse("news updated"), status=200)
