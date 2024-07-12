from rest_framework import serializers
from supports.models import Tag


class TagReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
