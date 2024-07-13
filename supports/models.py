from django.db import models
from django.conf import settings
from shortuuid import uuid

# Create your models here.


class MetaStamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    upated_at = models.DateTimeField(auto_now=True)
    public_id = models.CharField(default=uuid(), max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Comment(MetaStamps):
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
        "post.News",
        related_name="comments",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )
    stream = models.ForeignKey(
        "stream.Stream",
        related_name="comments",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )

    class Meta:
        db_table = "comment"

    def __str__(self):
        return self.author.username


class Tag(MetaStamps):
    title = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "tag"

    def __str__(self):
        return self.title


class Report(MetaStamps):
    news = models.ForeignKey(
        "post.News",
        null=True,
        on_delete=models.CASCADE,
        related_name="reported",
        blank=True,
    )
    stream = models.ForeignKey(
        "stream.Stream",
        null=True,
        on_delete=models.CASCADE,
        related_name="reported",
        blank=True
    )
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reports",
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "report"

    def __str__(self):
        return self.author.username
