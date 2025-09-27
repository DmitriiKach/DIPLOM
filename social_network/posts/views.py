from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from .models import Comment, Like, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CommentPostSerializer, ImagePostSerializer, PostSerializer
    )


class PostViewSet(ModelViewSet):
    """ViewSet для работы с постами."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        """Получение прав"""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action in ["list", "retrieve"]:
            return []

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=self.request.user)
        # Добавление фото
        for image in request.FILES.getlist("images"):
            data = {"image": image, "post": post.id}
            serializer = ImagePostSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(ModelViewSet):
    """ViewSet для работы с комментариями."""

    queryset = Comment.objects.all()
    serializer_class = CommentPostSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_pk"]).order_by(
            "created_at"
        )

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs["post_pk"],
                        author=self.request.user)

    def get_permissions(self):
        """Получение прав"""
        if self.action in ["list", "retrieve"]:
            return []  # чтение всем
        elif self.action == "create":
            return [IsAuthenticated()]  # create
        else:
            return [
                IsAuthenticated(),
                IsOwnerOrReadOnly(),
            ]  # update/partial_update/destroy


class LikeView(APIView):
    """APIView для работы с лайками."""

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        likes, created = Like.objects.get_or_create(
            post=post, author=request.user
            )
        if created:
            return Response({"detail": "liked"},
                            status=status.HTTP_201_CREATED)
        return Response({"detail": "already liked"}, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        deleted, _ = Like.objects.filter(
            post=post, author=request.user).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "not liked"}, status=status.HTTP_404_NOT_FOUND
            )
