from django.urls import path
from . import views

urlpatterns = [
    path("create", views.NewsCreateView.as_view()),
    path("update", views.NewsUpdateView.as_view()),
]
