from django.db import models
from django.conf import settings
from supports.models import MetaStamps
from shortuuid import uuid
from django.template.defaultfilters import slugify

# Create your models here.


class News(MetaStamps):
    slug = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300)
    channel = models.ForeignKey("channel.Channel", on_delete=models.CASCADE)
    publisher = models.ForeignKey(
        "channel.Publisher",
        on_delete=models.CASCADE,
        related_name="published_news",
    )
    media = models.JSONField(null=True, blank=True)
    tags = models.ManyToManyField("supports.Tag", related_name="news", blank=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="likes", blank=True
    )
    content = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
