from rest_framework import serializers
from ..models import Course, ProgressCourseRelation
from user.models import User
from lessons.models import Lesson
from lessons.serializers import LessonSerializer
from .category import CourseCategorySerializerForGETS
# from user.serializers import UserResumeSerializer

class ProgressCourseRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressCourseRelation
        fields = '__all__'

class UserResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class CourseSerializerForGETS(serializers.ModelSerializer):
    professor = serializers.SerializerMethodField('get_professor')
    students = serializers.SerializerMethodField('get_students')
    completed_course_relation = serializers.SerializerMethodField('get_completed_relations')
    categories = serializers.SerializerMethodField('get_categories')

    def get_categories(self, obj):
        return CourseCategorySerializerForGETS(obj.categories, many=True).data

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'content', 'rating', 'count_ratings', 'professor', 'learnings', 'students', 'lessons', 'completed_course_relation', 'categories']
        depth = 1
        
    def get_professor(self, obj):
        return UserResumeSerializer(obj.professor).data
    
    def get_students(self, obj): 
        students = User.objects.filter(courses=obj)
        return UserResumeSerializer(students, many=True).data
    
    def get_completed_relations(self, obj):
        relations = ProgressCourseRelation.objects.filter(course=obj)
        return ProgressCourseRelationSerializer(relations, many=True).data

class CourseSerializerForPOSTS(serializers.ModelSerializer):
    professor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    # def get_professor(self, obj):
    #     return ProfessorResumeSerializer(obj.professor).data

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'banner', 'content', 'rating', 'count_ratings', 'professor', 'learnings']
        depth = 1

class CourseResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']