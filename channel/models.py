from django.db import models
from django.conf import settings
from supports.models import Timestamps
from shortuuid import uuid


# Create your models here.


class Channel(Timestamps):
    name = models.CharField(max_length=200)
    public_id = models.CharField(default=uuid(), max_length=50)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_channels",
    )
    avatar = models.JSONField(null=True)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="followed_channels"
    )
    description = models.TextField(null=True)
    collaborators = models.JSONField(null=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "channel"
        default_related_name = "channels"

    def __str__(self):
        return self.name
