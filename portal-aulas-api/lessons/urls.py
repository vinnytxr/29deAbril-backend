from rest_framework import routers
from django.urls import path, include
from .views import LessonViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'lessons', LessonViewSet)

app_name = 'lessons'

urlpatterns = [
    path('', include(router.urls))
]
