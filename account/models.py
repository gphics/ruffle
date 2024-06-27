from django.db import models
from django.conf import settings
from shortuuid import uuid
from supports.models import Timestamps
# Create your models here.


class Profile(Timestamps):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.JSONField(null = True)
    location = models.CharField(max_length = 200)
    public_id = models.CharField(default=uuid(), max_length = 50)
    gender_choices = (("M", "Male"), ("F", "Female"))
    gender = models.CharField(choices=gender_choices, default="M", max_length=1)
    # following_channels = models.ManyToManyField("channel.Channel",related_name="fchannels")
    # owned_channels = models.ManyToManyField("channel.Channel",related_name="ochannels")
    # member_channels = models.ManyToManyField("channel.Channel",related_name="mchannels")

    class Meta:
        ordering = ["-created_at"]
        # default_related_name = "profile"

    def __str__(self):
        return self.user.username
