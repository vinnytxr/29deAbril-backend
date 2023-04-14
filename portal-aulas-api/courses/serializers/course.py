from rest_framework import serializers
from ..models import Course
from user.models import User
# from api.settings import BASE_DIR

class ProfessorResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')

class CourseSerializerForGETS(serializers.ModelSerializer):
    professor = serializers.SerializerMethodField('get_professor')
    # professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'professor', 'learnings']
        depth = 1
        
    def get_professor(self, obj):
        return ProfessorResumeSerializer(obj.professor).data

class CourseSerializerForPOSTS(serializers.ModelSerializer):
    # professor = serializers.SerializerMethodField('get_professor')
    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'professor', 'learnings']
        depth = 1
        
    # def get_professor(self, obj):
    #     return ProfessorResumeSerializer(obj.professor).data