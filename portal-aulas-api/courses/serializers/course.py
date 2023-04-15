from rest_framework import serializers
from ..models import Course
from user.models import User

class ProfessorResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')

class CourseSerializerForGETS(serializers.ModelSerializer):
    professor = serializers.SerializerMethodField('get_professor')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'professor', 'learnings']
        depth = 1
        
    def get_professor(self, obj):
        return ProfessorResumeSerializer(obj.professor).data

class CourseSerializerForPOSTS(serializers.ModelSerializer):
    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    def get_professor(self, obj):
        return ProfessorResumeSerializer(obj.professor).data

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'professor', 'learnings']
        depth = 1