from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Channel, Publisher
from .serializers.main import (
    ChannelCreateSerializer,
    ChannelReadSerializer,
    PublisherReadSerializer,
)
from helpers.res import generateResponse
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from account.models import Profile
from shortuuid import uuid
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import IsSuperPermitted, HaveOwnershipRight
from account.utils.serializers.user import profile_serializer
from helpers.bucket import CloudManager
from . import bot

# Basic CRUD Ops
class CrudView(APIView):

    def post(self, req):
        """
        Method for creating a channel
        """
        ser_data = ChannelCreateSerializer(data=req.data)
        if not ser_data.is_valid():
            return Response(
                generateResponse(err="channel name and description are required"), status=400
            )
        public_id = uuid()
        ser_data.save(owner=req.user, public_id=public_id)
        channel = Channel.objects.get(public_id=public_id)

        publisher = Publisher.objects.create(
            channel=channel, user=req.user, is_channel_admin=True
        )
        publisher.save()

        return Response(generateResponse("channel created successfully"), status=201)

    def get(self, req):
        """
        This method returns a channel if channel (public_id) is provided as a url params, otherwise;
        returns all channels owned and, followed and a member by the current user
        """
        channel_public_id = req.GET.get("channel", None)

        # if channel public id was provided
        if channel_public_id:
            raw_data = Channel.objects.filter(public_id=channel_public_id)
            if not raw_data[0]:
                return Response(generateResponse(err="channel does not exist"), status=404)
            serialized_data = ChannelReadSerializer(instance=raw_data[0]).data
            return Response(generateResponse(serialized_data))
        # if channel public_id was not provided
        owned_channels = ChannelReadSerializer(
            instance=Channel.objects.filter(owner=req.user).order_by("-created_at"),
            many=True,
        ).data

        # getting all followed channels
        channels = Channel.objects.all()
        all_channels = ChannelReadSerializer(instance=channels, many=True)
        followed_channels = []
        current_user = req.user.username

        def filt(user):
            if user["username"] == current_user:
                return True
            return False

        for channel in all_channels.data:
            followers = channel["followers"]
            exudate = len(list(filter(filt, followers)))
            if exudate:
                followed_channels.append(channel)
        # getting all channnel that the current user is a member of

        p = PublisherReadSerializer(
            instance=Publisher.objects.filter(user=req.user), many=True
        ).data
        membered_channels = []
        for publisher in p:
            membered_channels.append(publisher["channel"])
        # all_channels = ChannelReadSerializer(instance=Channel.objects.all(), many=True)
        result = {
            "owned": owned_channels,
            "membered_channels": membered_channels,
            "followed": followed_channels,
        }
        return Response(generateResponse(result), status=200)

    def put(self, req):
        """
        method for updating channel name and description
        update fields include:
            > name
            > description
        """
        public_id = req.GET.get("public_id", None)
        if not public_id:
            return Response(generateResponse(err="channel public_id must be provided"), status=400)
        channel = Channel.objects.get(public_id=public_id)
        if not channel:
            return Response(generateResponse(err="channel does not exist"), status=404)
        name = req.data.get("name", channel.name)
        description = req.data.get("name", channel.description)
        channel.name = name
        channel.description = description
        channel.save()
        return Response(generateResponse("channel updated"), status=200)

    def delete(self, req):
        """
        method for deleting a channel
        """
        public_id = req.GET.get("public_id", None)
        if not public_id:
            return Response(generateResponse(err="public_id must be provided"), status=400)
        channel = Channel.objects.filter(public_id=public_id)
        if not channel:
            return Response(generateResponse(err="channel does not exist"), status=404)
        c = channel[0]
        if c.avatar:
            cloud = Cloud("ll")
            cloud.destroy(c.avatar["public_id"])
        channel.delete()
        return Response(generateResponse("channel deleted"), status=200)


# Channel publisher ops
class PublisherView(APIView):
    """
    A class that is responsible for crud ops on the publisher
    * Permitted user:
            > Site superuser
            > Channel owner
            > Channel admin
    * Required query param:
        > channel (public_id)
    """

    permission_classes = [IsAuthenticated, IsSuperPermitted]

    def get(self, req):
        """
        * This method get all the publishers of a channel by default, but
        if p_public_id param is provided the method returns only the publisher that matches

        * Optional params:
            > user (public_id)
        """
        channel_public_id = req.GET.get("channel", None)
        publisher_public_id = req.GET.get("publisher", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        channel = Channel.objects.get(public_id=channel_public_id)
        if not channel:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        if not publisher_public_id:
            serialized = PublisherReadSerializer(instance=channel.publishers, many=True)
            return Response(generateResponse(serialized.data))
        publisher = Publisher.objects.get(
            public_id=publisher_public_id, channel=channel
        )
        if not publisher:
            return Response(generateResponse(err="publisher not found"),status=404)
        serialized = PublisherReadSerializer(instance=publisher).data
        return Response(generateResponse(serialized), status=200)

    def post(self, req):
        """
        * A method for creating and adding a publisher to a channel

        * Required data:
            > user (profile public id)

        * The method check if the user is already a publisher on the channel, if yes it respond with a messae saying user is already a publisher on the channel and if not it create and add the publisher to a channel
        """

        channel_public_id = req.GET.get("channel", None)
        user_public_id = req.data.get("user", None)
        #
        #
        # validations
        if not channel_public_id:
            return Response(
                generateResponse(err="channel public id param must be provided"), status=400
            )
        if not user_public_id:
            return Response(
                generateResponse(err="public id for user profile must be provided"), status=400
            )
        # fetching the profile and channel model instance
        profile = Profile.objects.filter(public_id=user_public_id)[0]
        channel = Channel.objects.filter(public_id=channel_public_id)[0]
        # validations ... against no profile and no channel
        if not profile:
            return Response(generateResponse(err="user profile public id not valid"), status=400)
        if not channel:
            return Response(generateResponse(err="channel public id not valid"), status=400)

        # check if the user is already a memeber of the channel
        is_member = Publisher.objects.filter(
            user=profile.user, channel=channel
        ).exists()

        if is_member:
            return Response(
                generateResponse(
                    err = f"{profile.user.username} is already a publisher on {channel.name} channel"
                ), status=400
            )
        Publisher.objects.create(channel=channel, user=profile.user)
        return Response(generateResponse("publisher added"), status=201)

    def put(self, req):
        """
        * A method for updating the publisher permission level
        * Required data:
            > p_public_id
            > is_channel_admin
        **  channel public id query not needed here
        """
        publisher_public_id = req.data.get("p_public_id", None)
        if not publisher_public_id:
            return Response(
                generateResponse(err="publisher public id must be provided"), status=400
            )
        is_channel_admin = req.data.get("is_channel_admin", False)
        publisher = Publisher.objects.get(public_id=publisher_public_id)
        if not publisher:
            return Response(generateResponse(err="invalid publisher public id"), status=400)
        publisher.is_channel_admin = is_channel_admin
        publisher.save()
        return Response(generateResponse("publisher permission level updated"), status=200)

    def delete(self, req):
        """
        * A method to delete a publisher from a channel
        * Required data:
            > publisher (public_id)
        """

        p_public_id = req.data.get("p_public_id", None)
        if not p_public_id:
            return Response(
                generateResponse(err="publisher public id must be provided"), status=400
            )

        publishers = Publisher.objects.filter(public_id=p_public_id)
        if len(publishers):
            publishers.delete()
            return Response(generateResponse("publisher deleted"), status=200)

        return Response(generateResponse(err="publisher does not exist"), status=404)


# changing ownership
class ChangeOwnershipView(APIView):
    """
    * A class responsible for the change of ownership of the channel
    * Required URL params:
        > channel (public_id)
    """

    permission_classes = [IsAuthenticated, HaveOwnershipRight]

    def put(self, req):
        """
        * The main method for this operation
        * Required data:
            > new_owner (profile public id)
        """
        channel_public_id = req.GET.get("channel", None)
        profile_public_id = req.data.get("new_owner", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        if not profile_public_id:
            return Response(generateResponse(err="profile public id must be provided"), status=400)

        c_filt = Channel.objects.filter(public_id=channel_public_id)
        p_filt = Profile.objects.filter(public_id=profile_public_id)

        if not c_filt[0]:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)

        if not p_filt[0]:
            return Response(generateResponse(err="invalid profile public id provided"), status=400)
        channel = c_filt[0]
        profile = p_filt[0]
        print(channel.owner)
        print(profile.user)
        if profile.user == channel.owner:
            return Response(
                generateResponse(
                    err="previous and the new channel owner must not be the same"
                ), status=400
            )

        channel.owner = profile.user
        channel.save()
        return Response(generateResponse("change of ownership successful"), status=200)


class GetChannelOwner(APIView):
    def get(self, req):
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        filt = Channel.objects.filter(public_id=channel_public_id)
        if not filt[0]:
            return Response(generateResponse(err="channel does not exist"), status=404)
        channel = filt[0]
        profile = profile_serializer(
            instance=Profile.objects.get(user=channel.owner)
        ).data
        return Response(generateResponse(profile), status=200)


# get all channels


class GetAllChannels(APIView):
    """
    > Route for getting all channels and it does not require aurhorization header
    """

    permission_classes = [AllowAny]

    def get(self, req):
        channels = ChannelReadSerializer(instance=Channel.objects.all(), many=True).data
        return Response(generateResponse(channels), status=200)


# un/following a channel
class FollowChannel(APIView):
    """
    * This class is responsible for following and unfollowing of channels by authenticated users
    * Required url param:
        > channel (public_id)
    """

    def get(self, req):
        """
        * A method for getting all channel followers
        """
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        filtrate = Channel.objects.filter(public_id=channel_public_id)
        if not filtrate:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        channel = ChannelReadSerializer(instance=filtrate[0]).data
        return Response(generateResponse(channel["followers"]), status=200)

    def put(self, req):
        """
        * A method for following a channel
        * Required data:
            > user (profile public id)
        """
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        profile_public_id = req.data.get("user", None)
        if not profile_public_id:
            return Response(generateResponse(err="user public id must be provided"), status=400)
        profile_filtrate = Profile.objects.filter(public_id=profile_public_id)
        channel_filtrate = Channel.objects.filter(public_id=channel_public_id)
        if not profile_filtrate:
            return Response(generateResponse(err="invalid user public id provided"), status=400)
        if not channel_filtrate:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        channel = channel_filtrate[0]
        profile = profile_filtrate[0]
        s_channel = ChannelReadSerializer(instance=channel).data
        if not len(s_channel["followers"]):
            channel.followers.add(profile.user)
            channel.save()
            return Response(
                generateResponse(f"You are now following the {channel.name} channel"), status=200
            )
        else:
            followed = False
            for x in s_channel["followers"]:
                if x["username"] == profile.user.username:
                    followed = True
            if followed:
                return Response(
                    generateResponse(err="You already followed this channel"), status=400
                )
            channel.followers.add(profile.user)
            channel.save()
            return Response(
                generateResponse(f"You are now following the {channel.name} channel"), status=200
            )

    def delete(self, req):
        """
        * A method for following a channel
        * Required data:
            > user (profile public id)
        """
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        profile_public_id = req.data.get("user", None)
        if not profile_public_id:
            return Response(generateResponse(err="user public id must be provided"), status=400)
        profile_filtrate = Profile.objects.filter(public_id=profile_public_id)
        channel_filtrate = Channel.objects.filter(public_id=channel_public_id)
        if not profile_filtrate:
            return Response(generateResponse(err="invalid user public id provided"), status=400)
        if not channel_filtrate:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        channel = channel_filtrate[0]
        profile = profile_filtrate[0]
        s_channel = ChannelReadSerializer(instance=channel).data
        if not len(s_channel["followers"]):
            return Response(
                generateResponse(err=f"{channel.name} channel have no follower"), status=400
            )
        else:
            followed = False
            for x in s_channel["followers"]:
                if x["username"] == profile.user.username:
                    followed = True
            if not followed:
                return Response(
                    generateResponse(
                        err=f"You are not a follower of the {channel.name} channel"
                    ), status=404
                )
            channel.followers.remove(profile.user)
            channel.save()
            return Response(
                generateResponse(f"You unfollowed the {channel.name} channel"), status=200
            )


# uploading channel avatar
class AvatarUpload(APIView):
    """
    * This class is for uploading and updating the channel avatar
    * Required URL Params:
        > channel (public id)
    * Permitted user:
        > site admin
        > channel owner
        > channel admin
    """

    permission_classes = [IsSuperPermitted]

    def get(self, req):
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        filt = Channel.objects.filter(public_id=channel_public_id)
        if not filt:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        channel = ChannelReadSerializer(instance=filt[0]).data
        return Response(generateResponse(channel["avatar"]), status=200)

    def post(self, req):
        """
        Method for uploading/updating channel avatar
        """
        cloud = CloudManager("ruffle", "channel")
        avatar = req.FILES.get("avatar", None)
        channel_public_id = req.GET.get("channel", None)
        if not avatar:
            return Response(generateResponse(err="avatar must be uploaded"), status=400)
        if not channel_public_id:
            return Response(generateResponse(err="channel public id must be provided"), status=400)
        filt = Channel.objects.filter(public_id=channel_public_id)
        if not filt:
            return Response(generateResponse(err="invalid channel public id provided"), status=400)
        size = cloud.validate_file_size(avatar.size)
        content_type = cloud.validate_img_type(avatar.content_type)
        if not content_type:
            return Response(generateResponse(err="content type not accepted"), status=400)
        if not size:
            return Response(generateResponse(err="file size too large"), status=400)
        channel = filt[0]
        try:
            if channel.avatar:
                cloud.delete(channel.avatar["key"])
            upload = cloud.upload(avatar)
            channel.avatar = upload
            channel.save()
            return Response(generateResponse("upload done"), status=200)
        except:
            return Response(generateResponse(err="something went wrong"), status=400)
