from rest_framework import routers
from django.urls import path, include
from .views import CourseViewSet, LearningViewSet, RatingsViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'courses', CourseViewSet) 
router.register(r'learnings', LearningViewSet)
router.register(r'ratings', RatingsViewSet)

app_name = 'courses'

urlpatterns = [
    path('', include(router.urls))
]
