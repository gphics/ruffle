from django.db import models
from django.conf import settings
from supports.models import MetaStamps
from shortuuid import uuid


# Create your models here.


class Channel(MetaStamps):
    name = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_channels",
    )
    avatar = models.JSONField(null=True, blank=True)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="followed_channels", blank=True
    )
    description = models.TextField(null=True)
    # collaborators = models.JSONField(null=True, blank=True)

    class Meta:
        # ordering = ["-created_at"]
        db_table = "channel"
        # default_related_name = "channels"

    def __str__(self):
        return self.name


class Publisher(MetaStamps):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="is_publisher"
    )
    channel = models.ForeignKey(
        Channel, related_name="publishers", on_delete=models.CASCADE
    )
    is_channel_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "publishers"

    def __str__(self):
        return f"Publisher: {self.user.username}"
