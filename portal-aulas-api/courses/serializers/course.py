from rest_framework import serializers
from ..models import Course
from user.models import User
from lessons.models import Lesson
from lessons.serializers import LessonSerializer
# from user.serializers import UserResumeSerializer

class UserResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class CourseSerializerForGETS(serializers.ModelSerializer):
    professor = serializers.SerializerMethodField('get_professor')
    students = serializers.SerializerMethodField('get_students')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'content', 'professor', 'learnings', 'students', 'lessons']
        depth = 1
        
    def get_professor(self, obj):
        return UserResumeSerializer(obj.professor).data
    
    def get_students(self, obj): 
        students = User.objects.filter(courses=obj)
        return UserResumeSerializer(students, many=True).data

class CourseSerializerForPOSTS(serializers.ModelSerializer):
    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    def get_professor(self, obj):
        return ProfessorResumeSerializer(obj.professor).data

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'content', 'professor', 'learnings']
        depth = 1

class CourseResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']