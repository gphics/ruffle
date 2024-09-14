from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .utils.genRes import generateResponse
from .utils.auth import validate_auth, get_user_public_id, verify_user
from .utils.serializers import ChannelSerializer, PublisherSerializer
from .models import Channel, Publisher
from .utils.paginator import paginate
from shortuuid import uuid
from .utils.permissions import GrandPermissions


class ChannelCRUD(APIView):
    """
    > This is the class responsible for all CRUD operations on the Channel
    > To access all the methods except GET requires the "token" header
    """

    def get(self, req):
        """
        > This method returns the channel with the public id provided as a url param
        > This method does not require authorization or authentication
        """
        id = req.GET.get("id", None)
        if not id:
            return Response(
                generateResponse({"msg": "channel public id must be provided"})
            )
        channel_filt = Channel.objects.filter(public_id=id)
        if not channel_filt.exists():
            return Response(generateResponse({"msg": "channel does not exist"}))
        channel = ChannelSerializer(instance=channel_filt[0]).data
        return Response(generateResponse({"msg": channel}))

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
        # checking if the user is already a publisher in a channel
        is_publisher = Publisher.objects.filter(user=user_public_id).exists()
        if is_publisher:
            return Response(
                generateResponse(err={"msg": "You are already a publisher"})
            )
        # building channel creation data
        built_data = {
            "name": name,
            "description": description,
            "owner": user_public_id,
            "public_id": uuid(),
        }
        ser = ChannelSerializer(data=built_data)
        if not ser.is_valid():
            return Response(generateResponse(err={"msg": "Something went wrong"}))
        channel = ser.save()
        Publisher.objects.create(
            channel=channel, user=user_public_id, public_id=uuid(), is_admin=True
        )
        return Response(generateResponse({"msg": "channel created successsfully"}))

    def put(self, req):
        """
        > This method is responsible for updating channel name and description
        > It can only be used by authenticated user which can only be publisher of the channel with admin level permission
        > Optional params:
            > name
            > description
        > The url must have the "id" query param which is channel public_id
        """
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        auth = get_user_public_id(token)
        auth_err = auth["err"]
        auth_data = auth["data"]
        if auth_err:
            return Response(generateResponse(err=auth_err))
        # user_public_id =
        channel_public_id = req.GET.get("id", None)
        if not channel_public_id:
            return Response(
                generateResponse(err={"msg": "channel public_id must be provided"})
            )
            # getting thr channel from the db
        first = Channel.objects.filter(public_id=channel_public_id)
        if not first.exists():
            return Response(generateResponse(err={"msg": "channel does not exist"}))

        # updating the channel
        channel = first[0]
        # validating authorization
        g_perm = GrandPermissions(auth_data["msg"])
        if not g_perm.is_channel_admin():
            return Response(
                generateResponse(
                    err={"msg": "You are not authorized to perform this opeation"}
                )
            )

        # geeting the request data
        name = req.data.get("name", None)

        if not name:
            name = channel.name
        else:
            is_channel_exist = Channel.objects.filter(name=name).exists()
            if is_channel_exist:
                return Response(
                    generateResponse(err={"msg": "Channel name already exist"})
                )

        description = req.data.get("description", channel.description)
        # updating the channel
        channel.name = name
        channel.description = description
        channel.save()
        return Response(generateResponse({"msg": "channel updated successfully"}))

    def delete(self, req):
        token = req.headers.get("Token", None)
        channel_public_id = req.GET.get("id", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        if not channel_public_id:
            return Response(
                generateResponse(err={"msg": "channel public id must be provided"})
            )
        auth = get_user_public_id(token)
        auth_data = auth["data"]
        auth_err = auth["err"]
        if auth_err:
            return Response(auth_err)
        user_public_id = auth_data["msg"]
        g_perm = GrandPermissions(user_public_id)
        if not g_perm.is_channel_admin():
            return Response(
                generateResponse(
                    err={"msg": "You are not authorized to delete the channel"}
                )
            )
        first = Channel.objects.filter(public_id=channel_public_id)
        if not first.exists():
            return Response(generateResponse(err={"msg": "Channel does not exist"}))
        first.delete()
        return Response(generateResponse({"msg": "channel deleted"}))


class PublisherCRUD(APIView):
    """
    > This is the class responsible for all CRUD operations on the Publisher model
    > To access all the methods except GET requires the "token" header

    """

    def get(self, req):
        c_public_id = req.GET.get("channel", None)
        if not c_public_id:
            return Response(
                generateResponse(err={"msg": "channel public id must be provided"})
            )

        channel_filt = Channel.objects.filter(public_id=c_public_id)
        if not channel_filt.exists():
            return Response(generateResponse(err={"msg": "channel does not exist"}))
        channel = channel_filt[0]
        publishers = PublisherSerializer(instance=channel.publishers, many=True).data
        return Response(generateResponse({"msg": publishers}))

    def post(self, req):
        """
        > This method requires a "channel" url query param which is a channel id
        > Required data:
            > user (public_id)
        > This method requires authentication and admin level authorization
        """
        # verifying authentication
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        # deep authentication verification
        first = get_user_public_id(token)
        first_err = first["err"]
        first_data = first["data"]
        if first_err:
            return Response(first)

        # checking auth user channel permission
        g_perm = GrandPermissions(first_data["msg"])
        if not g_perm.is_channel_admin():
            return Response(
                generateResponse(
                    err={"msg": "You are not authorize to perform this action"}
                )
            )
        # getting channel public_id
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(
                generateResponse(err={"msg": "channel public_id must be provided"})
            )
        channel = Channel.objects.filter(public_id=channel_public_id)
        if not channel.exists():
            return Response(generateResponse(err={"msg": "channel does not exist"}))
        # getting the user from data provided
        user_public_id = req.data.get("user", None)
        if not user_public_id:
            return Response(
                generateResponse(err={"msg": "user public_id must be provided"})
            )
        # verifying the user
        second = verify_user(user_public_id)
        second_err = second["err"]
        second_data = second["data"]
        if second_err:
            return Response(second)
        # checking if publisher already exist
        is_publisher = Publisher.objects.filter(user=user_public_id)
        if is_publisher.exists():
            return Response(
                generateResponse(err={"msg": "The user is already a publisher"})
            )

        # creating the publisher
        Publisher.objects.create(user=user_public_id, channel=channel[0])
        return Response(generateResponse({"msg": "publisher created successfully"}))

    def put(self, req):
        """
        > This method is responsible for updating the publisher admin state
        > Required data:
            > is_admin (Boolean)
        > Required url param:
            > id (publisher public id)
        > Only an admin publisher can perform this operation
        """
        # Authentication start
        token = req.headers.get("Token", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        # getting the auth user public id
        auth = get_user_public_id(token)
        auth_data = auth["data"]
        auth_err = auth["err"]
        # if an error occur
        if auth_err:
            return Response(auth)
        user_public_id = auth_data["msg"]
        admin_publisher_filt = Publisher.objects.filter(user=user_public_id)
        if not admin_publisher_filt.exists():
            return Response(generateResponse(err={"msg": "Invalid auth token"}))
        # Authetication end
        #
        #
        # Authorization start
        admin_publisher = admin_publisher_filt[0]
        if not admin_publisher.is_admin:
            return Response(generateResponse(err={"msg": "Unauthorized attempt"}))
        # Authorization end
        id = req.GET.get("id", None)
        is_admin = req.data.get("is_admin", None)
        if not id:
            return Response(
                generateResponse(err={"msg": "publisher public id must be provided"})
            )
        if id == admin_publisher.public_id:
            return Response(
                generateResponse(
                    err={"msg": "You cannot update your admin status yourself"}
                )
            )
        if is_admin == None:
            return Response(generateResponse(err={"msg": "is_admin must be provided"}))
        first = Publisher.objects.filter(public_id=id)
        if not first.exists():
            return Response(generateResponse(err={"msg": "publisher does not exist"}))
        publisher = first[0]
        publisher.is_admin = is_admin
        publisher.save()
        return Response(generateResponse({"msg": "publisher updated"}))

    def delete(self, req):
        """
        > A method responsible for deleting a publisher
        > The only authorized user is admin publisher
        > Only non admin publisher can be deleted
        """
        token = req.headers.get("Token", None)
        publisher_public_id = req.GET.get("id", None)
        if not token:
            return Response(generateResponse(err={"msg": "You are not authenticated"}))
        if not publisher_public_id:
            return Response(
                generateResponse(err={"msg": "publisher public id must be provided"})
            )
        auth_res = get_user_public_id(token)
        auth_err = auth_res["err"]
        auth_data = auth_res["data"]
        if auth_err:
            return Response(auth_res)
        is_admin = Publisher.objects.filter(
            user=auth_data["msg"], is_admin=True
        ).exists()
        if not is_admin:
            return Response(
                generateResponse(
                    err={"msg": "You are not authorize to perform this action"}
                )
            )
        publisher_filt = Publisher.objects.filter(public_id=publisher_public_id)
        if not publisher_filt.exists():
            return Response(generateResponse(err={"msg": "Publisher does not exist"}))
        publisher_filt.delete()
        return Response(generateResponse({"msg": "publisher deleted"}))


@api_view(["GET"])
def all_channels(req):
    """
    > This is a method that returns all channels in the abscence of the "name" parameter in the url
    > The name parameter is the name of the channel
    > This method also take an optional parameter "page" which is use for pagination
    > The maximum quantity of channel return per page is 20
    > This method does not rquires authentication
    """
    name = req.GET.get("name", None)
    page = int(req.GET.get("page", 1))
    # if query param is provided
    if name:
        query_result = Channel.objects.filter(name__icontains=name)
        ser = ChannelSerializer(instance=query_result, many=True).data
        if not len(ser):
            return Response(generateResponse(err={"msg": "Not found"}))
        return Response(generateResponse({"msg": ser}))
    # if query param is not provided
    serialized_all_channels = ChannelSerializer(
        instance=Channel.objects.all(), many=True
    ).data
    paginated_result = paginate(serialized_all_channels, page, 20)
    return Response(generateResponse({"msg": paginated_result}))
