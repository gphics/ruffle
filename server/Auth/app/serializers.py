from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class RegSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def validate_email(self, value):
        is_exist = User.objects.filter(email=value).exists()
        if is_exist:
            raise serializers.ValidationError("email already exist")
        return value

    def validate_username(self, value):
        is_exist = User.objects.filter(username=value).exists()
        if is_exist:
            raise serializers.ValidationError("username` already exist")
        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("password length is too short")
        return value

    def save(self, data):
        user = User.objects.create_user(
            email=data["email"], username=data["username"], password=data["password"]
        )
        return user


class ReadProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields= "__all__"
        depth = 2