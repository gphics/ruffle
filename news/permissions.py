from rest_framework.permissions import BasePermission
from channel.models import Publisher, Channel


class CRUDOpsPermission(BasePermission):
    def has_permission(self, req, view):
        if not req.user:
            return False
        channel_filt = Channel.objects.filter(owner=req.user)
        if not channel_filt:
            return False

        channel = channel_filt[0]
        publisher_filt = Publisher.objects.filter(user=req.user, channel=channel)
        if not publisher_filt:
            return False
        is_publisher = publisher_filt[0]
        if is_publisher:
            return True
        return False
