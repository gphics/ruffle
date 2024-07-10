from rest_framework import serializers
from django.contrib.auth.models import User




class login_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "username":{"required":True},
            "password":{"required":True},
        }

 