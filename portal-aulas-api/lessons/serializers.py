from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Lesson, Comment
# from courses.serializers.course import CourseResumeSerializer

# from user.serializers import UserResumeSerializer

class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
    
class LessonWithPrevNextSerializer(serializers.ModelSerializer):
    prev = serializers.SerializerMethodField('get_prev_lesson')
    next = serializers.SerializerMethodField('get_next_lesson')
    professor = serializers.SerializerMethodField('get_professor_from_course')
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
    
    def get_professor_from_course(self, obj):
        return obj.course.professor.id
        


class LessonResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'banner']
        
class CommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'lesson']


class CommentSerializer(serializers.ModelSerializer):
    replies = CommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'lesson', 'replies']
