from django.urls import path
from . import views

urlpatterns = [
    path("channel", views.ChannelCRUD.as_view()),
    path("publisher", views.PublisherCRUD.as_view()),
    path("channel/all", views.all_channels)
]
