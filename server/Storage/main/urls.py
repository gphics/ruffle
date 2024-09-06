from django.urls import path
from . import views

urlpatterns = [path("", views.Cloud.as_view()),]
