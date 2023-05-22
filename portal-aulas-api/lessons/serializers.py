from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Lesson

class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
    
class LessonWithPrevNextSerializer(serializers.ModelSerializer):
    prev = serializers.SerializerMethodField('get_prev_lesson')
    next = serializers.SerializerMethodField('get_next_lesson')
    class Meta:
        model = Lesson
        fields = '__all__'
        depth = 0
    
    def get_prev_lesson(self, obj):
        prev_lesson = Lesson.objects.filter(course=obj.course, id__lt=obj.id).order_by('-id').first()
        if prev_lesson:
            return LessonResumeSerializer(prev_lesson).data
        return None
    
    def get_next_lesson(self, obj):
        next_lesson = Lesson.objects.filter(course=obj.course, id__gt=obj.id).order_by('id').first()
        if next_lesson:
            return LessonResumeSerializer(next_lesson).data
        return None


class LessonResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'banner']