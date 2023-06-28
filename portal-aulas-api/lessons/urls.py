from rest_framework import routers
from django.urls import path, include
from .views import LessonViewSet, CommentViewSet, ReplyViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'lessons', LessonViewSet)

app_name = 'lessons'

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/<int:lesson_id>/comments/', CommentViewSet.as_view({'post': 'create'}), name='lesson-comments'),
    path('lessons/<int:lesson_id>/comments/list', CommentViewSet.as_view({'get': 'list'}), name='list-comments'),
    path('lessons/<int:lesson_id>/comments/<int:pk>/', CommentViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='comment-detail'),
    path('lessons/<int:lesson_id>/comments/<int:comment_id>/reply/<int:pk>/', ReplyViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='reply-detail'),
    path('lessons/<int:lesson_id>/comments/<int:pk>/reply', CommentViewSet.as_view({'post': 'create_reply'}), name='reply-comments'),
]
