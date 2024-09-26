from django.urls import path
from . import views
urlpatterns = [
    path("", views.CommentCRUD.as_view())
]
