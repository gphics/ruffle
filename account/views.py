from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils.serializers.user import reg_serializer, user_serializer, profile_serializer
from rest_framework.response import Response
from .utils.res import generateResponse
from .models import Profile
from rest_framework.authtoken.models import Token
from rest_framework import generics
from .utils.serializers.auth import login_serializer
from django.contrib.auth.models import User


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, req):
        user = reg_serializer(data=req.data)
        if not user.is_valid():
            return Response(generateResponse(err=user.errors))
        user.save(user.data)
        auth_user = authenticate(
            username=user.data["username"], password=user.data["password"]
        )
        if not auth_user:
            return Response(generateResponse(err="user does not exists"))
        token = Token.objects.get_or_create(user=auth_user)
        user_profile = Profile.objects.create(user=auth_user)
        print(user_profile)
        key = str(token[0])
        return Response(generateResponse({"token": key}))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, req):
        password = req.data.get("password", None)
        username = req.data.get("username", None)
        if not username:
            return Response(generateResponse(err="username must be provided"))
        if not password:
            return Response(generateResponse(err="password must be provided"))
        serializer = login_serializer(instance=req.data)
        user = authenticate(
            username=serializer.data["username"], password=serializer.data["password"]
        )
        if not user:
            return Response(generateResponse(err="invalid credentials"))
        token = Token.objects.get_or_create(user=user)
        key = str(token[0])
        return Response(generateResponse({"token": key}))


class UserView(APIView):
    def get(self, req):
        raw_profile = Profile.objects.get(user=req.user)
        profile = profile_serializer(instance=raw_profile)
        return Response(generateResponse(profile.data))
