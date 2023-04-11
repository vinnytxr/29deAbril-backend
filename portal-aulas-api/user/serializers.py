from user.models import User, Role
from rest_framework import serializers

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
      model = Role
      fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
      model = User
      fields = ['id', 'name', 'email', 'password', 'photo', 'about', 'role', 'created', 'modified']
