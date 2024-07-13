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
    nationality = models.CharField(max_length=200, null=True, blank=True)
    gender_choices = (("Male", "Male"), ("Female", "Female"))
    gender = models.CharField(choices=gender_choices, default="Male", max_length=6)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "profile"

    def __str__(self):
        return self.user.username
