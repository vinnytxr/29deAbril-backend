from user.models import User, Role
from user.serializers import UserSerializer, RoleSerializer
from rest_framework import viewsets

class RoleViewSet(viewsets.ModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer