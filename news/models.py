from django.db import models
from django.conf import settings
from supports.models import Timestamps
from shortuuid import uuid

# Create your models here.


class News(Timestamps):
    title = models.CharField(max_length=300)
    public_id = models.CharField(default=uuid(), max_length=50)
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE)
    publisher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="published_news",
    )
    media = models.JSONField(null=True)
    tags = models.ManyToManyField("supports.Tag", related_name="news", null=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="likes", null=True
    )
    content = models.TextField(null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
