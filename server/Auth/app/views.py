from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegSerializer, ReadProfileSerializer
from .genRes import generateResponse
from .create_token import get_or_create
from django.contrib.auth import authenticate
from .models import Profile
from shortuuid import uuid
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
import requests
import os


class RegView(APIView):
    """
    * This is the user registration class
    """

    permission_classes = [AllowAny]

    def post(self, req):
        """
        > A method for creating the user
        * Required data params:
            > email
            > password
            > username
        > This method return an auth token
        """
        if req.user.is_authenticated:
            print(req.user)
            return Response(generateResponse({"msg": "you are authenticated already"}))
        email = req.data.get("email", None)
        password = req.data.get("password", None)
        username = req.data.get("username", None)
        if not email:
            return Response(generateResponse(err={"msg": "email must be provided"}))
        if not password:
            return Response(generateResponse(err={"msg": "password must be provided"}))
        if not username:
            return Response(generateResponse(err={"msg": "username must be provided"}))

        user = RegSerializer(data=req.data)
        if not user.is_valid():
            email_err = user.errors.get("email", None)
            password_err = user.errors.get("password", None)
            username_err = user.errors.get("username", None)
            if email_err:
                return Response(generateResponse(err={"msg": "email already exist"}))
            if username_err:

                return Response(generateResponse(err={"msg": "username already exist"}))
            if password_err:
                return Response(
                    generateResponse(
                        err={"msg": "password length must be greater than 5"}
                    )
                )
        user.save(user.data)
        auth_user = authenticate(
            username=user.data["username"], password=user.data["password"]
        )
        if not auth_user:
            return Response(generateResponse(err={"msg": "user does not exist"}))
        token = get_or_create(user=auth_user)
        user_profile = Profile.objects.create(user=auth_user, public_id=uuid())

        return Response(generateResponse({"msg": "user created"} | token))


class LoginView(APIView):
    """
    > This is the user login view
    """

    permission_classes = [AllowAny]

    def post(self, req):
        """
        > A method for signing in the user
        * Required data params:
            > password
            > username
        > This method return an auth token
        """
        print(req.headers["Auth"])
        username = req.data.get("username", None)
        password = req.data.get("password", None)

        if not username or not password:
            return Response(
                generateResponse(err={"msg": "username and password must be provided"})
            )
        auth_user = authenticate(username=username, password=password)

        if not auth_user:
            return Response(generateResponse(err={"msg": "invalid credentials"}))
        token = get_or_create(user=auth_user)

        return Response(
            generateResponse(data={"msg": "user login successfully"} | token)
        )


class ProfileView(APIView):
    """
    > A class responsible for all CRUD operations on the user profile
    """

    def get(self, req):
        """
        > A method for getting user profile
        """
        storage_server_url = os.getenv("STORAGE_SERVER_URL")
        user = req.user
        first = Profile.objects.filter(user=user)
        if not first.exists:
            return Response(generateResponse(err={"msg": "user does not exist"}))
        second = ReadProfileSerializer(instance=first[0]).data
        # getting user avatar
        # avavtar_public_id = second["avatar_public_id"]
        # if avavtar_public_id:
        #     x = requests.get(f"{storage_server_url}?id={avavtar_public_id}")
        #     y = x.json()
        #     if y["err"]:
        #         return Response(generateResponse(err=y["err"]))
        #     z = {**second, avatar: y["data"]}
        #     return Response(generateResponse({"profile": z}))
        return Response(generateResponse({"profile": second}))

    def put(self, req):
        """
        > A method for updating the user profile along with the user
        """
        req_user = req.data.get("user", None)
        req_profile = req.data.get("profile", None)
        first = Profile.objects.filter(user=req.user)
        if not first.exists():
            return Response(generateResponse(err={"msg": "user does not exist"}))
        _first = first[0]
        if not req_profile and not req_user:
            return Response(
                generateResponse(err={"msg": "user and profile data must be provided"})
            )

        # if user data is provided
        if req_user:
            first_name = req_user["first_name"] or req.user.first_name
            last_name = req_user["last_name"] or req.user.last_name
            User.objects.filter(email=req.user.email).update(
                first_name=first_name, last_name=last_name
            )
        # if profile data is provided
        if req_profile:
            gender = req_profile.get("gender") or _first.gender
            contact = req_profile.get("contact") or _first.contact
            nationality = req_profile.get("nationality") or _first.nationality
            Profile.objects.filter(user=req.user).update(
                gender=gender, contact=contact, nationality=nationality
            )
        return Response(generateResponse({"msg": "profile updated"}))

    def delete(self, req):
        """
        > This is a method for deleting the profile along with it's user
        """
        first = Profile.objects.filter(user=req.user)
        if not first.exists():
            return Response(generateResponse(err={"msg": "user does not exists"}))
        first.delete()
        return Response(generateResponse({"msg": "user deleted"}))


class AvatarView(APIView):
    """
    > This method is responsible for managing user avatar
    """

    storage_server_url = os.getenv("STORAGE_SERVER_URL")

    def post(self, req):
        """
        > This method is responsible for updating and uploading user avatar
        """
        folder = "auth"
        media = req.FILES.get("media", None)
        if not media:
            return Response(generateResponse(err={"msg": "media must be provided"}))
        first = Profile.objects.filter(user=req.user)
        if not first.exists():
            return Response(generateResponse(err={"msg": "user does not exists"}))
        profile = first[0]
        try:
            token = Token.objects.get(user=req.user).key
            avatar_public_id = profile.avatar_public_id
            if not avatar_public_id:
                first_req = requests.post(
                    f"{self.storage_server_url}?folder=auth",
                    files={"media": media},
                    headers={"Token": token},
                )
                res = first_req.json()
                err = res.get("err", None)
                data = res.get("data", None)
                if err:
                    return Response(generateResponse(err=err))
                profile.avatar_public_id = data["msg"]
                profile.save()
                return Response(
                    generateResponse({"msg": "avatar uploaded successfully"})
                )
            else:
                first_req = requests.put(
                    f"{self.storage_server_url}?id={avatar_public_id}",
                    files={"media": media},
                    headers={"Token": token},
                )
                res = first_req.json()
                err = res.get("err", None)
                data = res.get("data", None)
                if err:
                    return Response(generateResponse(err=err))
                return Response(
                    generateResponse({"msg": "avatar updated successfully"})
                )
        except Exception as e:
            return Response(generateResponse(err={"msg": "something went wrong"}))


@api_view(["PUT"])
def email_update_view(req):
    """
    > A function based view responsible for changing user email
    > Required param:
        > email
    """
    new_email = req.data.get("email", None)
    old_email = req.user.email

    if not new_email:
        return Response(generateResponse(err={"msg": "new email must be provided"}))
    if old_email == new_email:
        return Response(
            generateResponse(
                err={
                    "msg": "the new mail provided must not be the same as the old email"
                }
            )
        )
    is_exist = User.objects.filter(email=new_email).exists()

    if is_exist:
        return Response(
            generateResponse(err={"msg": "user with the email provided already exist"})
        )
    user = User.objects.filter(email=old_email)[0]
    user.email = new_email
    user.save()
    token = get_or_create(user)
    return Response(generateResponse({"msg": "email updated"} | token))


@api_view(["PUT"])
def password_update_view(req):
    """
    > A function based view responsible for changing user password
    > Required param:
        > old_password
        > new_password
    """
    new_password = req.data.get("new_password", None)
    old_password = req.data.get("old_password", None)

    if not old_password or not new_password:
        return Response(
            generateResponse(err={"msg": "old and new password must be provided"})
        )
    if len(new_password) < 6:
        return Response(
            generateResponse(err={"msg": "password length must be greater than 5"})
        )
    check_user = authenticate(username=req.user.username, password=old_password)
    if not check_user:
        return Response(generateResponse(err={"msg": "incorrect old password"}))
    user = User.objects.get(username=req.user.username)
    user.set_password = new_password
    user.save()
    token = get_or_create(user=user)

    return Response(generateResponse({"msg": "password updated"} | token))


@api_view(["PUT"])
def username_update_view(req):
    """
    > A function based view responsible for changing username
    > Required param:
        > username
    """
    new_username = req.data.get("username", None)
    if not new_username:
        return Response(generateResponse(err={"msg": "new username must be provided"}))
    old_username = req.user.username
    if old_username == new_username:
        return Response(
            generateResponse(
                err={"msg": "the new username must be different from the previous one"}
            )
        )
    is_exist = User.objects.filter(username=new_username).exists()
    if is_exist:
        return Response(generateResponse(err={"msg": "username not available"}))
    user = User.objects.filter(username=old_username)[0]
    user.username = new_username
    user.save()
    token = get_or_create(user)
    return Response(generateResponse({"msg": "username updated"} | token))


@api_view(["GET"])
def validate_auth(req):
    if req.user:
        return Response(generateResponse({"msg": True}))
    return Response(generateResponse(err={"msg": False}))
