from django.db import models
from django.conf import settings
from shortuuid import uuid
from supports.models import MetaStamps

# Create your models here.


class Profile(MetaStamps):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.JSONField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    gender_choices = (("M", "Male"), ("F", "Female"))
    gender = models.CharField(choices=gender_choices, default="M", max_length=1)
    # following_channels = models.ManyToManyField("channel.Channel",related_name="fchannels")
    # owned_channels = models.ManyToManyField("channel.Channel",related_name="ochannels")
    # member_channels = models.ManyToManyField("channel.Channel",related_name="mchannels")

    class Meta:
        db_table = "profile"

    def __str__(self):
        return self.user.username
