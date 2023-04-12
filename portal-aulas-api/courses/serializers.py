from rest_framework import serializers
from .models import Course, Learning
from api.settings import BASE_DIR

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = '__all__'

class LearningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Learning
        fields = '__all__'