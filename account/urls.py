from django.urls import path
from . import views
urlpatterns = [
    path("register", views.RegisterView.as_view()),
    path("login", views.LoginView.as_view()),
    path("", views.ProfileView.as_view()),
    path("avatar", views.AvatarView.as_view()),
    path("user", views.UsersView.as_view()),
    path("user/update-password", views.update_password_view),
    path("user/update-email", views.update_email_view),
    path("user/update-username", views.update_username_view),
    # path("user/update-is-active", views.update_is_active_view),
]
