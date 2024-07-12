from rest_framework.permissions import BasePermission
from channel.models import Publisher, Channel


class CanCRUDTag(BasePermission):
    """
    * This permission class allows the following user:
        > site admin
        > publisher
        > site owner
    """
    def has_permission(self, req, view):
        if not req.user:
            return False
        is_superuser = req.user.is_superuser
        is_channel_owner = Channel.objects.filter(owner=req.user).exists()
        is_publisher = Publisher.objects.filter(user=req.user).exists()
        if is_superuser or is_publisher or is_channel_owner:
            return True

        return False
