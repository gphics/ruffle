from django.db import models
from supports.models import Timestamps
from django.conf import settings
from shortuuid import uuid

# Create your models here.


class Stream(Timestamps):
    title = models.CharField(max_length=200)
    public_id = models.CharField(default=uuid(), max_length=50)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hosted_stream"
    )
    streamers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="my_streams", null=True
    )
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE)
    description = models.TextField(null=True)

    class Meta:
        ordering = ["-created_at"]

    # default_related_name = "stream"

    def __str__(self):
        return self.title
