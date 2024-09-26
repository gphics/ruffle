from rest_framework import serializers
from news.models import Tag, Post
from comment.models import Comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        depth = 2
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        depth = 2
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
