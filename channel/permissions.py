from rest_framework.permissions import BasePermission
from channel.models import Publisher, Channel

# from account.models import Profile


# class IsMember(BasePermission):
# def has_permission(self, req):
#     channel_public_id = req.data.get("c_public_id", None)
#     channel = Channel.objects.get(public_id=channel_public_id)
#     if not channel:
#         return False
#     is_member = Publisher.objects.filter(user=req.user, channel=channel).exists()
#     return is_member


# class IsChannelAdmin(BasePermission):
# def has_permission(self, req):
#     channel_public_id = req.data.get("c_public_id", None)
#     channel = Channel.objects.get(public_id=channel_public_id)
#     if not channel:
#         return False
#     is_channel_admin = Publisher.objects.filter(user=req.user, channel=channel)[
#         0
#     ].is_channel_admin

#     return is_channel_admin


# class IsChannelOwner(BasePermission):
# def has_permission(self, req):
#     channel_public_id = req.GET.get("channel", None)
#     is_channel_owner = Channel.objects.filter(
#         public_id=channel_public_id, owner=req.user
#     ).exists()

#     return is_channel_owner


class HaveOwnershipRight(BasePermission):
    def has_permission(self, req, view):
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return False
        is_site_admin = req.user.is_superuser
        is_channel_owner = Channel.objects.filter(
            public_id=channel_public_id, owner=req.user
        ).exists()
        if is_channel_owner or is_site_admin:
            return True
        return False


class IsSuperPermitted(BasePermission):
    """
    Allowed users:
        > Site admin
        > Channel owner
        > Channel admin
    """

    def has_permission(self, req, view):
        if not req.user:
            return False
        channel_public_id = req.GET.get("channel", None)
        if not channel_public_id:
            return False
        filt = Channel.objects.filter(public_id=channel_public_id)
        if not filt:
            return True
        channel = filt[0]
        # checking if the request user is the site  admin
        is_superuser = req.user.is_superuser
        # checking if the request user is the channel owner
        is_channel_owner = channel.owner == req.user
        # checking if the request user is one of the channel admin publisher
        publishers = Publisher.objects.filter(user=req.user, channel=channel)
        is_channel_admin = False
        if publishers and publishers[0].is_channel_admin:
            is_channel_admin = True
        if is_channel_admin or is_channel_owner or is_superuser:
            return True
        else:
            return False
