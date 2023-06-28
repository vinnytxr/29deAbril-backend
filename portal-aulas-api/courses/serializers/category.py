from rest_framework import serializers
from ..models import CourseCategory
from lessons.models import Lesson
import json

class CourseCategoryResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name']

class CourseCategorySerializerForGETS(serializers.ModelSerializer):
    lessons_order = serializers.SerializerMethodField()

    def get_lessons_order(self, obj):
        return obj.get_lessons_order()

    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'lessons_order', 'lessons']
        depth=1

class CourseCategorySerializerForPOSTS(serializers.ModelSerializer):
    lessons_order = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = CourseCategory
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class CourseCategoryDepthSerializerForGETS(serializers.ModelSerializer):
    lessons_order = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_order(self, obj):
        return obj.get_lessons_order()

    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'lessons_order', 'lessons']