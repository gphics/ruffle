from rest_framework import serializers
from django.contrib.auth.models import User
from account.models import Profile


class reg_serializer(serializers.ModelSerializer):
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("password length must be greater than 5")

        return value

    def validate_email(self, value):

        isExist = User.objects.filter(email=value).exists()
        if isExist:
            raise serializers.ValidationError("user with the email already exist")
        return value

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def save(self, data):
        user = User.objects.create_user(
            data["username"], data["email"], data["password"]
        )
        return user


class user_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class profile_serializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        depth = 2
