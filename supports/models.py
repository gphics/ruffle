from django.db import models
from django.conf import settings
from shortuuid import uuid
# Create your models here.


class Timestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    upated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(Timestamps):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        null=True,
        on_delete=models.CASCADE,
    )
    dep_comment = models.ForeignKey(
        "self", related_name="deps", null=True, on_delete=models.CASCADE
    )
    content = models.TextField()
    news = models.ForeignKey(
        "news.News", related_name="comments", null=True, on_delete=models.CASCADE
    )
    stream = models.ForeignKey(
        "stream.Stream",
        related_name="comments",
        null=True,
        on_delete=models.CASCADE,
    )
    public_id = models.CharField(default=uuid(), max_length=50)

    class Meta:
        # default_related_name = "comments"
        ordering = ["-created_at"]

    def __str__(self):
        return self.author.username


class Tag(Timestamps):
    title = models.CharField(max_length=100)

    class Meta:
        # default_related_name = "tags"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Report(Timestamps):
    news = models.ForeignKey(
        "news.News", null=True, on_delete=models.CASCADE, related_name="reported"
    )
    stream = models.ForeignKey(
        "stream.Stream",
        null=True,
        on_delete=models.CASCADE,
        related_name="reported",
    )
    public_id = models.CharField(default=uuid(), max_length=50)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports",
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        # default_related_name = "reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.author.username
