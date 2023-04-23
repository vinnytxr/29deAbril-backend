from user.models import User, Role, Invitation
from rest_framework import serializers
from courses.models import Course
from courses.serializers.course import CourseResumeSerializer
from . import services

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)
    created_courses = serializers.SerializerMethodField()
    enrolled_courses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'photo', 'about', 'role', 'enrolled_courses', 'created_courses', 'created', 'modified')
        extra_kwargs = {'password': {'required': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        role_ids = validated_data.pop('role')
        if not role_ids:
            raise serializers.ValidationError({'Cargo': 'Usuário precisa ter um cargo.'})
        user = User.objects.create_user(password=password, **validated_data)
        user.role.set(role_ids)
        return user
    
    def get_created_courses(self, obj):
        created_courses = Course.objects.filter(professor=obj)
        return CourseResumeSerializer(created_courses, many=True).data
    
    def get_enrolled_courses(self, obj):
        enrolled_course = obj.courses.all()
        return CourseResumeSerializer(enrolled_course, many=True).data
    
class UserResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

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
