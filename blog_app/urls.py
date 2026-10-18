from rest_framework import routers

from .views import ArticleViewSet, CategoryViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('articles', ArticleViewSet)
router.register('comments', CommentViewSet)

urlpatterns = router.urls
