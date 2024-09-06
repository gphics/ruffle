from rest_framework import serializers

from ..models import StorageManager


class ReadStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageManager
        fields = "__all__"
