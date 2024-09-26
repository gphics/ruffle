from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from utils.genRes import generateResponse
from utils.auth import Authorize
from news.models import Post
from .models import Comment
from shortuuid import uuid
from utils.serializers import CommentSerializer


class CommentCRUD(APIView):
    """
    > This class is responsible for CRUD operations on the comment model
    > Currently only create and read method are written while the update and delete are left for future purposes
    """

    def get(self, req):
        """
        > This method is responsible for getting all comments related to a post
        > THis method does not require authentication
        > Required url param:
            > post (public_id)
        """
        post_public_id = req.GET.get("post", None)
        if not post_public_id:
            return Response(
                generateResponse(err={"msg": "post url param must be provided"})
            )
        post_filt = Post.objects.filter(public_id=post_public_id)
        if not post_filt.exists():
            return Response(generateResponse(err={"msg": "post does not exists"}))
        post = post_filt[0].pk
        comments = Comment.objects.filter(post=post)
        ser = CommentSerializer(instance=comments, many=True).data
        return Response(generateResponse({"msg": ser}))

    def post(self, req):
        """
        > This method is responsible for creating comment on a post
        > Reqired data:
            > content
            > author (auth user public_id which would be gotten from the auth user programmatically)
            > post (public_id)
        > This method requires authetication
        """
        # handling authentication
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        auth = Authorize(token)
        user_p_id = auth.get_user_public_id()
        data = user_p_id.get("data", None)
        err = user_p_id.get("err", None)
        if err:
            return Response(user_p_id)
        auth_public_id = data["msg"]
        # #####
        content = req.data.get("content", None)
        post = req.data.get("post", None)
        post_filt = Post.objects.filter(public_id=post)
        if not post_filt.exists():
            return Response(generateResponse(err={"msg": "post does not exists"}))
        post = post_filt[0]
        Comment.objects.create(
            post=post, content=content, author=auth_public_id, public_id=uuid()
        )
        return Response(generateResponse({"msg": "comment created"}))

    # def put(self, req):
    #     pass

    # def delete(self, req):
    #     pass
