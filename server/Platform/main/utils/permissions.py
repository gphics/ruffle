from ..models import Publisher, Channel
from .genRes import generateResponse


class GrandPermissions:
    """
    > THis class returns a boolean
    """
    def __init__(self, user_public_id):
        self.user_public_id = user_public_id

    def is_basic(self):
        first = Publisher.objects.filter(user=self.user_public_id)
        if not first.exists():
            return False
        return True

    def is_channel_admin(self):
        first = Publisher.objects.filter(user=self.user_public_id)
        if not first.exists():
            return False
        second = first[0]

        if second.is_admin:
            return True
        return False
