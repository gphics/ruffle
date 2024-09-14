from django.urls import path
from . import views

urlpatterns = [
    path("register", views.RegView.as_view()),
    path("login", views.LoginView.as_view()),
    path("validate-auth", views.validate_auth),
    path("upload-avatar", views.AvatarView.as_view()),
    path("", views.ProfileView.as_view()),
    path("update-email", views.email_update_view),
    path("update-username", views.username_update_view),
    path("update-password", views.password_update_view),
    path("verify-user", views.verify_user),
    path("users", views.get_all_users),
    
]
