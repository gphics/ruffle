from rest_framework import serializers
from channel.models import Channel, Publisher


class ChannelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name", "description"]

    def validate(self, data):
        if not data["name"]:
            raise serializers.ValidationError("channel name must be provided")
        if not data["description"]:
            raise serializers.ValidationError("channel name must be provided")
        return data


class ChannelReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"
        depth = 3


class ChannelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ("name", "description")


class PublisherReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"
        depth = 3
