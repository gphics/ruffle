from django.urls import path
from . import views

urlpatterns = [
    path("tag/create", views.create_tag),
    path("tag/update", views.update_tag),
    path("tag/delete", views.delete_tag),
    path("tag/all", views.GetTags.as_view()),
]
