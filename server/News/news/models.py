from django.db import models
from shortuuid import uuid
from django.template.defaultfilters import slugify

# Create your models here.


class MetaStamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_id = models.CharField(max_length=50, default=uuid())

    class Meta:
        abstract = True


class Tag(MetaStamps):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Post(MetaStamps):
    channel = models.CharField(max_length=50)
    content = models.TextField()
    media = models.JSONField(null = True, blank = True)
    title = models.CharField(max_length=300)
    # likes = models.JSONField(null=True, blank=True)
    slug = models.CharField(max_length=300)
    total_views = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    class Meta:
        db_table = "post"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
