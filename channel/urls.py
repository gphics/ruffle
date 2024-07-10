from django.urls import path
from . import views

urlpatterns = [
    path("all", views.GetAllChannels.as_view()),
    path("crud", views.CrudView.as_view()),
    path("owner", views.GetChannelOwner.as_view()),
    path("owner/change", views.ChangeOwnershipView.as_view()),
    path("publisher", views.PublisherView.as_view()),
    path("follow", views.FollowChannel.as_view()),
    path("avatar", views.AvatarUpload.as_view()),
   
    # path("<channel>/publisher", views.PublisherView.as_view()),
    # path("me", views..as_view()),
]
