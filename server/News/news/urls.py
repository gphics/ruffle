from django.urls import path
from . import views
urlpatterns = [
    path("tag", views.TagView.as_view()),
    path("post", views.PostView.as_view()),
    path("tag/single", views.get_post_through_tag),
]
