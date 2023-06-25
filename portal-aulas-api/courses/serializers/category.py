from rest_framework import serializers
from ..models import CourseCategory
import json

class CourseCategorySerializerForGETS(serializers.ModelSerializer):
    lessons_order = serializers.SerializerMethodField()

    def get_lessons_order(self, obj):
        return obj.get_lessons_order()

    class Meta:
        model = CourseCategory
        fields = '__all__'

class CourseCategorySerializerForPOSTS(serializers.ModelSerializer):
    lessons_order = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = CourseCategory
        fields = '__all__'