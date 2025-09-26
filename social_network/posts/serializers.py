from rest_framework import serializers
from posts.models import Post, Comment, PostImage


class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ('author', 'text', 'created_at')

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at']

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['post', 'image']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    images = ImagePostSerializer(read_only=True, many=True)
    class Meta:
        model = Post
        fields = ('id', 'text', 'images', 'created_at', 'comments')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['likes_count'] = instance.likes.count()
        return representation