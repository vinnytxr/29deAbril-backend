from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, RoleViewSet

app_name = "user"

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'role', RoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]