from rest_framework import viewsets

from .models import Article, Category, Comment
from .serializers import ArticleSerializer, CategorySerializer, CommentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.prefetch_related('comments', 'tags')
    serializer_class = ArticleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('article')
    serializer_class = CommentSerializer
