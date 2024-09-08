from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .utils.genRes import generateResponse
from .utils.auth import validate_auth, get_user_public_id
from .utils.serializers import ChannelSerializer
from .models import Channel, Publisher
from .utils.paginator import paginate

# x = validate_auth("09eeaa7b4e7a5ee849f6fec0d61e3bc6a09c7392")
# y = get_user_public_id("09eeaa7b4e7a5ee849f6fec0d61e3bc6a09c7392")

# print(x)
# print(y)


class ChannelCRUD(APIView):
    """
    > This is the class responsible for all CRUD operations on the Channel
    > To access all the methods except GET requires the "token" header
    """

    def get(self, req):
        """
        > This is a method that returns all channels in the abscence of the "q" parameter in the url
        > The q parameter is the name of the channel
        > This method also take an optional parameter "page" which is use for pagination
        > The maximum quantity of channel return is 20
        """
        q = req.GET.get("q", None)
        page = int(req.GET.get("page", 1))
        if q:
            pass

        serialized_all_channels = ChannelSerializer(
            instance=Channel.objects.all(), many=True
        ).data
        paginated_result = paginate(serialized_all_channels, page, 20)
        return Response(generateResponse(paginated_result))

    def post(self, req):
        """
        > Required data:
            > name
            > description
        """
        name = req.data.get("name", None)
        description = req.data.get("description", None)
        if not name or not description:
            return Response(
                generateResponse(
                    err={"msg": "channel name and description must be provided"}
                )
            )
        # getting user public_id
        token = req.headers.get("Token", None)

        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        first = get_user_public_id(token)
        first_data = first["data"]
        first_err = first["err"]
        if first_err:
            return Response(first_err)
        user_public_id = first_data["msg"]
        # checking if user already created a channel before
        is_owner_exists = Channel.objects.filter(owner=user_public_id).exists()
        if is_owner_exists:
            return Response(generateResponse(err={"msg": "You already have a channel"}))
        # checking if channel name already exist
        is_channel_exist = Channel.objects.filter(name=name).exists()
        if is_channel_exist:
            return Response(
                generateResponse(
                    err={"msg": f"channel with the name {name} already exist"}
                )
            )
        # building channel creation data
        built_data = {"name": name, "description": description, "owner": user_public_id}
        ser = ChannelSerializer(data=built_data)
        if not ser.is_valid():
            return Response(generateResponse(err={"msg": "Something went wrong"}))
        ser.save()
        return Response(generateResponse({"msg": "channel created successsfully"}))

    def put(self, req):
        pass

    def delete(self, req):
        pass


class PublisherCRUD(APIView):
    """
    > This is the class responsible for all CRUD operations on the Publisher model
    > To access all the methods except GET requires the "token" header

    """

    def get(self, req):
        pass

    def post(self, req):
        pass

    def put(self, req):
        pass

    def delete(self, req):
        pass
