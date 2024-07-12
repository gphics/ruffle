from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from helpers.res import generateResponse
from .models import Tag
from .permissions import CanCRUDTag
from shortuuid import uuid
from rest_framework.views import APIView
from .serializers.tag import TagReadSerializer

####
# Tag operations
# start
####
@api_view(["POST"])
@permission_classes([CanCRUDTag])
def create_tag(req):
    """
    * A view for creating tag
    * Required data:
        > title
    """
    title = req.data.get("title", None)
    if not title:
        return Response(generateResponse(err="title must be provided"))
    try:
        tag = Tag.objects.create(title=title, public_id=uuid())
        return Response(generateResponse("tag created"))

    except:
        return Response(generateResponse(err="tag with the same title already exist"))


@api_view(["PUT"])
@permission_classes([CanCRUDTag])
def update_tag(req):
    """
    * A view for updating a tag
    * Required url param:
        > tag (public id)
    * Required data:
        > new_title
    """
    tag_public_id = req.GET.get("tag", None)
    title = req.data.get("title", None)
    if not tag_public_id:
        return Response(generateResponse(err="tag public id must be provided"))
    if not title:
        return Response(generateResponse(err="new title must be provided"))
    is_exist = Tag.objects.filter(title=title).exists()
    if is_exist:
        return Response(generateResponse(err="tag with the same title already exist"))
    filt = Tag.objects.filter(public_id=tag_public_id).update(title=title)
    return Response(generateResponse("tag updated"))


@api_view(["DELETE"])
@permission_classes([CanCRUDTag])
def delete_tag(req):
    """
    * A view for deleting a tag
    * Required url param:
        > tag (public id)
    """
    tag_public_id = req.GET.get("tag", None)
    if not tag_public_id:
        return Response(generateResponse(err="tag public id must be provided"))

    filt = Tag.objects.filter(public_id=tag_public_id)
    if filt:
        filt.delete()
        return Response(generateResponse("tag deleted"))
    return Response(generateResponse(err="tag does not exist"))


class GetTags(APIView):
    permission_classes([AllowAny])

    def get(self, req):
        tags = TagReadSerializer(instance=Tag.objects.all(), many=True).data
        return Response(generateResponse(tags))

####
# Tag operations
# end
####
