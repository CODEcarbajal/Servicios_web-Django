from rest_framework import serializers

from .models import Article, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'article', 'author_name', 'author_email', 'content', 'created_at', 'is_approved']
        read_only_fields = ['id', 'created_at']


class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'author', 'category', 'tags',
                  'published_at', 'updated_at', 'is_published', 'comments']
        read_only_fields = ['id', 'published_at', 'updated_at']

    def validate(self, attrs):
        is_published = attrs.get('is_published', getattr(self.instance, 'is_published', True))
        category = attrs.get('category', getattr(self.instance, 'category', None))
        if is_published and category is None:
            raise serializers.ValidationError(
                'Un artículo publicado debe tener exactamente una categoría asignada.'
            )
        return attrs
