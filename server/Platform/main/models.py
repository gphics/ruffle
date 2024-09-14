from django.db import models
from shortuuid import uuid


class Metastamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_id = models.CharField(max_length=50, default=uuid())

    class Meta:
        abstract = True

 
class Channel(Metastamps):
    name = models.CharField(max_length=100)
    # the user will be filled with public_id of the auth user
    owner = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    avatar_public_id = models.CharField(max_length=50, blank=True, null=True)
    follows = models.JSONField(max_length=50, blank=True, null=True)

    class Meta:
        # ordering = ["-created_at"]
        db_table = "channel"


class Publisher(Metastamps):
    # the user will be filled with public_id of the auth user
    user = models.CharField(max_length=50)
    is_admin = models.BooleanField(default=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="publishers")

    class Meta:
        ordering = ["-created_at"]
        db_table = "publisher"
