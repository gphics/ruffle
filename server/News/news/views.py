from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from utils.genRes import generateResponse
from utils.serializers import TagSerializer, PostSerializer
from .models import Tag, Post
from utils.auth import Authorize
from shortuuid import uuid
import requests
import os
from utils.cloud import Cloud
from utils.paginator import paginate

# Create your views here.


class TagView(APIView):
    """
    > This view is responsible for all CRUD operations on the Tag model
    > The CUD operations is only open to publisher
    """

    def get(self, req):
        """
        > This method returns the tag objects
        > It does not requires neither authentication nor authorization
        > If the id url param is present, it is used for filtering
        > But if title param is present, it will be used instead of the public_id
        > But if neither of the two are present, it returns all the tags available
        """
        public_id = req.GET.get("id", None)
        title = req.GET.get("title", None)
        result = []
        if title:
            result = TagSerializer(
                instance=Tag.objects.filter(title__icontains=title), many=True
            ).data
        elif public_id:
            result = TagSerializer(
                instance=Tag.objects.filter(public_id=public_id), many=True
            ).data

        else:
            result = TagSerializer(instance=Tag.objects.all(), many=True).data
        return Response(generateResponse({"msg": result}))

    def post(self, req):
        """
        > This method is responsible for tag creation and it requires publisher level authorization
        """
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse({"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        auth_err = is_publisher["err"]
        if auth_err:
            return Response(is_publisher)
        title = req.data.get("title", None)
        if not title:
            return Response(generateResponse(err={"msg": "title must be provided"}))
        tag_exist = Tag.objects.filter(title=title).exists()
        if tag_exist:
            return Response(generateResponse(err={"msg": "tag already exist"}))
        Tag.objects.create(title=title, public_id=uuid())
        return Response(generateResponse({"msg": "tag created successfully"}))

    def put(self, req):
        """
        > This method is responsible for tag update
        > It requires publisher level authorization
        > Required param:
            > id (tag public_id)
        > Required data:
            > title
        """
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse({"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        auth_err = is_publisher["err"]
        if auth_err:
            return Response(is_publisher)
        title = req.data.get("title", None)
        if not title:
            return Response(generateResponse(err={"msg": "title must be provided"}))
        public_id = req.GET.get("id", None)
        if not public_id:
            return Response(
                generateResponse(err={"msg": "tag public id must be provided"})
            )
        tag_filt = Tag.objects.filter(public_id=public_id)
        if not tag_filt.exists():
            return Response(generateResponse(err={"msg": "tag does not exist"}))
        title = req.data.get("title", None)
        is_title_exist = Tag.objects.filter(title=title).exists()
        if is_title_exist:
            return Response(generateResponse(err={"msg": "tag already exist"}))
        tag = tag_filt[0]
        tag.title = title
        tag.save()
        return Response(generateResponse({"msg": "tag updated"}))

    def delete(self, req):
        """
        > This method is responsible for tag deletion
        > It requires publisher level authorization
        > Required param:
            > id (tag public_id)
        """

        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse({"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        auth_err = is_publisher["err"]
        if auth_err:
            return Response(is_publisher)
        public_id = req.GET.get("id", None)
        if not public_id:
            return Response(
                generateResponse(err={"msg": "tag public id must be provided"})
            )
        tag_filt = Tag.objects.filter(public_id=public_id)
        if not tag_filt.exists():
            return Response(generateResponse(err={"msg": "tag does not exist"}))
        tag = tag_filt[0]
        tag.delete()
        return Response(generateResponse({"msg": "tag deleted"}))


class PostView(APIView):
    def get(self, req):
        """
        > A method responsible for retrieving posts
        > Optional url param:
            > title
            > id (post public_id)
            > channel (public_id)
            > page (default 1)
        > This method query the db with the param if provided else returns all post
        > This method does not require auth
        """
        title = req.GET.get("title", None)
        id = req.GET.get("id", None)
        channel = req.GET.get("channel", None)
        page = int(req.GET.get("page", 1))
        results = []
        cloud = Cloud()
        if title:
            first = Post.objects.filter(title__icontains=title)
            if not first.exists():
                return Response(generateResponse(err={"msg": "post does not exists"}))
            ser = PostSerializer(instance=first, many=True).data
            results = ser
        elif id:
            first = Post.objects.filter(public_id=id)
            if not first.exists():
                return Response(generateResponse(err={"msg": "post does not exist"}))
            post = first[0]
            # updating the total views
            post.total_views = post.total_views + 1
            post.save()
            second = PostSerializer(instance=post).data
            third = second
            media_list = third["media"]
            result = second
            if media_list:
                media = cloud.batch_retrieve(media_list)
                err = media["err"]
                data = media["data"]
                if err:
                    return Response(media)
                result = {**third, "media": data["msg"]}
            return Response(generateResponse({"msg": result}))
        elif channel:
            first = Post.objects.filter(channel=channel)
            if not first.exists():
                return Response(generateResponse(err={"msg": "post does not exists"}))
            ser = PostSerializer(instance=first, many=True).data
            results = ser
        else:
            first = Post.objects.all()
            if not first.exists():
                return Response(generateResponse(err={"msg": "post does not exist"}))
            ser = PostSerializer(instance=first, many=True).data
            results = ser
        paginated_result = paginate(results, page)
        paginated_data = paginated_result["result"]
        total_pages = paginated_result["total_pages"]
        cur_page = paginated_result["cur_page"]
        final_result = []
        for post in paginated_data:
            media = post["media"]
            if not media:
                final_result.append(post)
            else:
                first = cloud.batch_retrieve(media)
                err = first["err"]
                data = first["data"]
                if err:
                    return Response(first)
                result = {**post, "media": data["msg"]}
                final_result.append(result)
        return Response(
            generateResponse(
                {
                    "msg": {
                        "cur_page": cur_page,
                        "total_pages": total_pages,
                        "posts": final_result,
                    }
                }
            )
        )

    def post(self, req):
        """
        > This method is responsible for creating the post
        > Required data:
            > title
            > channel (public_id)
            > content
        > Optional data:
            > media
            > tags ([tag (pk)])
        """
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        auth_err = is_publisher["err"]
        if auth_err:
            return Response(is_publisher)
        publisher_channel_pk = is_publisher["data"]["msg"]["channel"]["id"]
        # getting the data
        title = req.data.get("title", None)
        channel_public_id = req.data.get("channel", None)
        content = req.data.get("content", None)

        # validating the req.data
        if not title or not channel_public_id or not content:
            return Response(
                generateResponse(err={"msg": "All required data must be provided"})
            )
        try:
            # Trying to get channel details to verify if the auth user is a publisher of the channel
            platform_server_url = os.getenv("PLATFORM_SERVER_URL")
            first_req = requests.get(
                f"{platform_server_url}channel?id={ channel_public_id}"
            )
            first_res = first_req.json()
            first_data = first_res.get("data", None)
            first_detail = first_res.get("detail", None)
            first_err = first_res.get("err", None)
            if first_detail:

                return Response(generateResponse(err={"msg": first_detail}))
            if first_err:

                return Response(generateResponse(err=first_err))
            main_channel_data = first_data["msg"]
            # verifying the authenticity of the auth user channel and the provided channel
            is_channel_publisher = publisher_channel_pk == main_channel_data["id"]
            if not is_channel_publisher:
                return Response(
                    generateResponse(
                        err={"msg": "You are not a publisher of the channel provided"}
                    )
                )
            # creating the post object

            # checking if user provides a media file
            media_list = req.FILES.getlist("media")
            # creating the post
            post = Post(
                public_id=uuid(),
                title=title,
                channel=channel_public_id,
                content=content,
            )
            if media_list:
                result = []
                for media in media_list:
                    upload = Cloud().upload(media, token)
                    upload_data = upload.get("data", None)
                    upload_err = upload.get("err", None)
                    if upload_err:
                        return Response(upload)
                    p_id = upload_data["msg"]
                    result.append(p_id)
                post.media = result
            tags = req.data.get("tags", None)
            if tags:
                for pk in tags:
                    first = Tag.objects.filter(pk=pk)
                    if not first:
                        return Response(
                            generateResponse(err={"msg": "invalid tag public id"})
                        )
                    post.save()
                    post.tags.add(first[0].pk)
            post.save()
            return Response(generateResponse({"msg": "post created"}))
        except Exception as e:
            print(e)
            return Response(generateResponse(err={"msg": "something went wrong"}))

    def put(self, req):
        """
        > This method is responsible for updating the post details
        > data :
            > title
            > content
            > tags (?pk)
        > Required url param:
            > id (post public_id)
        > This method requires auth
        """
        id = req.GET.get("id", None)
        if not id:
            return Response(
                generateResponse(err={"msg": "post public id must be provided"})
            )
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        is_pub_err = is_publisher["err"]
        is_pub_data = is_publisher["data"]
        if is_pub_err:
            return Response(is_publisher)
        post_filt = Post.objects.filter(public_id=id)
        if not post_filt.exists():
            return Response(generateResponse(err={"msg": "post does not exist"}))
        title = req.data.get("title", None)
        content = req.data.get("content", None)
        # if not title and not content:
        #     return Response(
        #         generateResponse(err={"msg": "either title or content must be present"})
        #     )
        post = post_filt[0]
        pub_channel_id = is_pub_data["msg"]["channel"]["public_id"]
        if post.channel != pub_channel_id:
            return Response(generateResponse(err={"msg": "You are not authorized"}))
        post.title = title or post.title
        post.content = content or post.content
        # if tags are provided
        tags = req.data.get("tags", None)
        for tag in tags:
            # verifying the tag
            first = Tag.objects.filter(pk=tag)
            if not first.exists():
                return Response(
                    generateResponse(err={"msg": "invalid tag id provided"})
                )
            post.tags.add(tag)
        post.save()
        return Response(generateResponse({"msg": "post updated"}))

    def delete(self, req):
        """
        > This method is responsible for deleting post
        > Authentication and Authorization are required
        > Only a channel publisher can delete a post from his/her channel
        > Required url params:
            > id (post public_id)
        """
        id = req.GET.get("id", None)
        if not id:
            return Response(
                generateResponse(err={"msg": "post public id must be provided"})
            )
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        auth = Authorize(token)
        is_publisher = auth.is_publisher()
        is_pub_err = is_publisher["err"]
        is_pub_data = is_publisher["data"]
        if is_pub_err:
            return Response(is_publisher)
        post_filt = Post.objects.filter(public_id=id)
        if not post_filt.exists():
            return Response(generateResponse(err={"msg": "post does not exist"}))
        post = post_filt[0]
        pub_channel_id = is_pub_data["msg"]["channel"]["public_id"]
        if post.channel == pub_channel_id:
            cloud = Cloud()
            media_list = post.media
            if media_list:
                media_del_res = cloud.batch_delete(media_list, token)
                err = media_del_res["err"]
                if err:
                    return Response(media_del_res)
            post_filt.delete()
            return Response(generateResponse({"msg": "post deleted"}))
        return Response(generateResponse(err={"msg": "You are not authorized"}))


@api_view(["GET"])
def get_post_through_tag(req):
    """
    > This view is responsible for querying the post through the tag
    > Required url param:
        > tag (title)
    """
    tag = req.GET.get("tag", None)
    page = int(req.GET.get("page", 1))

    if not tag:
        return Response(generateResponse(err={"msg": "tag must be provided"}))

    first = Tag.objects.filter(title__icontains=tag)
    if not first.exists():
        return Response(generateResponse(err={"msg": "tag does not exist"}))
    second = first[0]
    post_filt = Post.objects.filter(tags__title__icontains=second.title)
    if not post_filt.exists():
        return Response(generateResponse(err={"msg": "post not found"}))
    ser = PostSerializer(instance=post_filt, many=True).data
    paginated_result = paginate(ser, page)
    result = paginated_result["result"]
    total_pages = paginated_result["total_pages"]
    cur_page = paginated_result["cur_page"]
    return Response(
        generateResponse(
            {
                "msg": {
                    "cur_page": cur_page,
                    "total_pages": total_pages,
                    "result": result,
                }
            }
        )
    )
