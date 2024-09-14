from django.db import models
from news.models import MetaStamps, Post

# Create your models here.


class Report(MetaStamps):
    author = models.CharField(max_length=50)
    post = models.ForeignKey(Post, related_name="report", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    media = models.JSONField()
