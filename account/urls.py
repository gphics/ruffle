from django.urls import path
from . import views
urlpatterns = [
    path("create", views.RegisterView.as_view()),
    path("login", views.LoginView.as_view()),
    path("", views.UserView.as_view()),
]
