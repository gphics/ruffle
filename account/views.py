from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils.serializers.user import reg_serializer, user_serializer, profile_serializer
from rest_framework.response import Response
from helpers.res import generateResponse
from .models import Profile
from rest_framework.authtoken.models import Token
from rest_framework import generics
from .utils.serializers.auth import login_serializer
from django.contrib.auth.models import User

from shortuuid import uuid
from helpers


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, req):
        """
        * A method for creating new user
        * Required data:
            > username (unique)
            > email (unique)
            > password
        """
        user = reg_serializer(data=req.data)
        if not user.is_valid():
            email_err = user.errors.get("email", None)
            password_err = user.errors.get("password", None)
            if email_err:
                return Response(generateResponse(err="email already exist"))
            if password_err:
                return Response(
                    generateResponse(err="password length should be greater than 5")
                )
        user.save(user.data)
        auth_user = authenticate(
            username=user.data["username"], password=user.data["password"]
        )
        if not auth_user:
            return Response(generateResponse(err="user does not exists"))
        token = Token.objects.get_or_create(user=auth_user)
        user_profile = Profile.objects.create(user=auth_user, public_id=uuid())
        key = str(token[0])
        return Response(generateResponse({"token": key}))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, req):
        """
        A method for authenticating & generating user token
        """
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


class ProfileView(APIView):
    def get(self, req):
        print(req.user.is_publisher)
        """
        A method for getting the current user
        """
        raw_profile = Profile.objects.get(user=req.user)
        profile = profile_serializer(instance=raw_profile)
        return Response(generateResponse(profile.data))

    def put(self, req):
        """
        A method for updating the current user and it's profile
        > fields for profile update:
            > gender
            > location
            > phone
        > fields for user update:
            > first_name
            > last_name
        """
        user_data = req.data.get("user", None)
        profile_data = req.data.get("profile", None)
        first = Profile.objects.get(user=req.user)
        second = None
        third = None
        if not profile_data and not user_data:
            return Response(
                generateResponse(err="profile data or user data must be provided ")
            )
        # if profile dict was provided
        if profile_data:
            gender = profile_data["gender"] or first.gender
            phone = profile_data["phone"] or first.phone
            location = profile_data["location"] or first.location
            second = Profile.objects.filter(user=req.user).update(
                location=location, gender=gender, phone=phone
            )
        # if user dict was provided
        if user_data:
            first_name = user_data["first_name"] or req.user.first_name
            last_name = user_data["last_name"] or req.user.last_name
            third = User.objects.filter(username=req.user.username).update(
                last_name=last_name, first_name=first_name
            )
        return Response(generateResponse({"message": "account update successful"}))

    def delete(self, req):
        """
        A method for deleting current the user
        """
        req_user = req.user
        if req_user.avatar:
            cloud = Cloud("ll")
            cloud.destroy(req_user.avatar["public_id"])
        user = User.objects.filter(username=req.user.username).delete()
        return Response(generateResponse({"message": "account delete successful"}))


class AvatarView(APIView):

    def post(self, req):
        """
        * Method for uploading/updating profile avatar
        """
        avatar = req.FILES.get("avatar", None)
        
        if not avatar:
            return Response(generateResponse(err="avatar file not uploaded"))
        validation_res = cloud.img_validate(avatar.content_type, avatar.size)

        if not validation_res["mimetype"]:
            return Response(generateResponse(err="mimetype not accepted"))
        if not validation_res["size"]:
            return Response(generateResponse(err="file size too large"))
        profile = Profile.objects.get(user=req.user)
        try:
            if profile.avatar:
                cloud.destroy(profile.avatar["public_id"])
            uploads = cloud.img_upload(avatar)
            profile.avatar = uploads
            profile.save()
            return Response(generateResponse("profile updated successfully"))
        except Exception as e:
            print(e)
            return Response(generateResponse(err="something went wrong"))
    # def post(self, req):
    #     """
    #     method for uploading/updating profile avatar
    #     """
    #     avatar = req.FILES.get("avatar", None)
    #     cloud = Cloud("account")
    #     if not avatar:
    #         return Response(generateResponse(err="avatar file not uploaded"))
    #     validation_res = cloud.img_validate(avatar.content_type, avatar.size)

    #     if not validation_res["mimetype"]:
    #         return Response(generateResponse(err="mimetype not accepted"))
    #     if not validation_res["size"]:
    #         return Response(generateResponse(err="file size too large"))
    #     profile = Profile.objects.get(user=req.user)
    #     try:
    #         if profile.avatar:
    #             cloud.destroy(profile.avatar["public_id"])
    #         uploads = cloud.img_upload(avatar)
    #         profile.avatar = uploads
    #         profile.save()
    #         return Response(generateResponse("profile updated successfully"))
    #     except Exception as e:
    #         print(e)
    #         return Response(generateResponse(err="something went wrong"))


class UsersView(APIView):
    def get(self, req):
        """
        A methhod for getting users
            > return one user if a username param is provided
            > return all users if no username param is provided
        """
        username = req.GET.get("username", None)
        if username:
            user = User.objects.get(username=username)
            if not user:
                return Response(
                    generateResponse(err="user with the username does not exist")
                )
            first = Profile.objects.get(user=user.pk)
            second = profile_serializer(instance=first)
            return Response(generateResponse(second.data))
        first = Profile.objects.all().order_by("-created_at")
        second = profile_serializer(instance=first, many=True)
        return Response(generateResponse(second.data))


# special updates
@api_view(["PUT"])
def update_password_view(req):
    """
    A view for updating user password
    """
    old_password = req.data.get("old_password", None)
    new_password = req.data.get("new_password", None)
    if not old_password:
        return Response(generateResponse(err="old password must be provided"))
    if not new_password:
        return Response(generateResponse(err="new password must be provided"))
    if len(new_password) < 6:
        return Response(
            generateResponse(
                err="the length of the new password must be greated than five"
            )
        )
    if old_password == new_password:
        return Response(generateResponse(err="the two password must not be the same"))
    auth_user = authenticate(username=req.user.username, password=old_password)
    if not auth_user:
        return Response(generateResponse(err="old password not correct"))
    user = req.user
    user.set_password(new_password)
    user.save()
    return Response(generateResponse("password updated"))


@api_view(["PUT"])
def update_username_view(req):
    """
    A view for updating username
    """
    user = req.user
    old_username = user.username
    new_username = req.data.get("username", None)
    # validations
    if not new_username:
        return Response(generateResponse(err="new username must be provided"))
    if old_username == new_username:
        return Response(
            generateResponse(err="new username must be different from old username")
        )
    isExist = User.objects.filter(username=new_username).exists()
    if isExist:
        return Response(generateResponse(err="username not available"))
    user.username = new_username
    user.save()
    return Response(generateResponse("username updated"))


@api_view(["PUT"])
def update_email_view(req):
    """
    A view for updating email
    """
    user = req.user
    old_email = user.email
    new_email = req.data.get("email", None)
    # validations
    if not new_email:
        return Response(generateResponse(err="new email must be provided"))
    if old_email == new_email:
        return Response(
            generateResponse(err="new email must be different from old email")
        )
    isExist = User.objects.filter(email=new_email).exists()
    if isExist:
        return Response(generateResponse(err="email not available"))
    user.email = new_email
    user.save()
    return Response(generateResponse("email updated"))


# maybe for future purpose
# def update_is_active_view(req):
#     is_active = req.data.get("is_active", True)
#     user = req.user
#     user.is_active = is_active
#     user.save()
#     state = "activation" if is_active else "deactivation"
#     return Response(generateResponse(f"user {state} successful"))
