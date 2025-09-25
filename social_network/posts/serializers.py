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

    def representation(self, post):
        representation = super().to_representation(post)
        representation['likes_count'] = post.likes.count()
        return representation