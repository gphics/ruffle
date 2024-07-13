from rest_framework import serializers
from post.models import News
from channel.models import Publisher, Channel
from supports.models import Tag


class NewsReadSerializer(serializers.ModelSerializer):
    class Meta:
        # depth = 3
        model = News
        fields = "__all__"


class NewsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = "__all__"

    def validate_tags(self, value):
        if value:
            for x in value:
                state = Tag.objects.filter(pk=x).exists()
                if not state:
                    raise serializers.ValidationError("tag does not exist")
        return value
