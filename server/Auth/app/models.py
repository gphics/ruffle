from django.db import models
from shortuuid import uuid
from django.conf import settings


class MetaStamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public_id = models.CharField(default=uuid(), max_length=40)

    class Meta:
        abstract = True


class Profile(MetaStamps):
    gender_choices = (("Male", "Male"), ("Female", "Female"))
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    nationality = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=100, blank=True, null=True)
    year_of_birth = models.IntegerField(blank=True, null=True)
    avatar_public_id = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(choices=gender_choices, default="Male", max_length=6)

    class Meta:
        db_table = "profile"

    def __str__(self):
        return self.user.username
