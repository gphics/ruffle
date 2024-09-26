from django.db import models
from news.models import MetaStamps
# Create your models here.


class Comment(MetaStamps):
    author = models.CharField(max_length=50)
    content = models.TextField()
    post = models.ForeignKey("news.Post", on_delete=models.CASCADE, related_name="comments")
    # media = models.JSONField()

    class Meta:
        db_table = "comment"
        ordering = ["-created_at"]