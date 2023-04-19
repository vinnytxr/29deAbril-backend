from user.models import User, Role, Invitation
from rest_framework import serializers
from . import services

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'photo', 'about', 'role', 'created', 'modified')
        extra_kwargs = {'password': {'required': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        role_ids = validated_data.pop('role')
        if not role_ids:
            raise serializers.ValidationError({'Cargo': 'Usuário precisa ter um cargo.'})
        user = User.objects.create_user(password=password, **validated_data)
        user.role.set(role_ids)
        return user

class InvitationSerializer(serializers.ModelSerializer):

    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

    class Meta:
        model = Invitation
        fields = ['id', 'code', 'professor']

    def create(self, validated_data):
        code = validated_data.pop('code')
        code = services.create_invitation()

        invitation = Invitation.objects.create(code=code, **validated_data)
        return invitation
