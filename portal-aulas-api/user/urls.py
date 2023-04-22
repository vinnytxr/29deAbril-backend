from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, RoleViewSet, LoginAPIView, UserAPIView, LogoutAPIView, InvitationViewSet

app_name = "user"

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'role', RoleViewSet)
router.register(r'invitation', InvitationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('user-info/', UserAPIView.as_view(), name="userinfo"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
]