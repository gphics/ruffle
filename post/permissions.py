from rest_framework.permissions import BasePermission
from channel.models import Publisher, Channel
from post.models import News


class NewsCreatePermission(BasePermission):
    def has_permission(self, req, view):
        """
        * This method picks the channel public id from the posted data
        """
        if not req.user:
            return False
        # getting channel public id and if does not exist, I return True early so that the view can handle it
        # by sending an error response
        channel_public_id = req.data.get("channel", None)
        if not channel_public_id:
            return True
        # getting the channel
        c_filt = Channel.objects.filter(public_id=channel_public_id)
        # if channel does not exist, I return True early so that the view can handle the invalid channel public_id
        if not c_filt:
            return True
        channel = c_filt[0]
        # checking if the user is a publisher for this channel
        is_channel_publisher = Publisher.objects.filter(
            user=req.user, channel=channel
        ).exists()

        return is_channel_publisher


class NewsUpdatePermission(BasePermission):
    def has_permission(self, req, view):
        """
        * This method pick the news public id from the url query param
        """
        # getting the news public id and if it does not exist, I return early so that the view can handle the case
        news_public_id = req.GET.get("news", None)
        if not news_public_id:
            return True
        n_filt = News.objects.filter(public_id=news_public_id)
        # getting the news  and if it does not exist, I return early so that the view can handle the case
        if not n_filt:
            return True
        news = n_filt[0]
        is_publisher = Publisher.objects.filter(
            user=req.user, channel=news.channel
        ).exists()
        return is_publisher
