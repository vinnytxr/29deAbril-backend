from django.shortcuts import get_object_or_404
from rest_framework import serializers
from courses.serializers.category import CourseCategoryResumeSerializer
from courses.models import CourseCategory
from .models import Lesson, Comment, User, CommentReply
import json

class LessonSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('get_category')

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_category(self, obj):
        return CourseCategoryResumeSerializer(obj.category).data
    
class LessonWithPrevNextSerializer(serializers.ModelSerializer):
    prev = serializers.SerializerMethodField('get_prev_lesson')
    next = serializers.SerializerMethodField('get_next_lesson')
    professor = serializers.SerializerMethodField('get_professor_from_course')
    category = serializers.SerializerMethodField('get_category')
    
    class Meta:
        model = Lesson
        fields = '__all__'
        depth = 0
    
    def get_prev_lesson(self, obj):

        prev_lesson = None

        lessons_order = json.loads(obj.category.lessons_order)
        lessons_in_same_category = Lesson.objects.filter(category=obj.category)

        lessons_arr = [i for i in lessons_in_same_category]
        lessons_arr.sort(key=lambda x: lessons_order.index(x.id))
        lessons_arr_ids = [i.id for i in lessons_arr]

        if obj.id in lessons_arr_ids:
            obj_idx_on_array = lessons_arr_ids.index(obj.id)
            if obj_idx_on_array > 0:
                prev_lesson = lessons_arr[obj_idx_on_array - 1]

        if prev_lesson:
            return LessonResumeSerializer(prev_lesson).data
        return None
    
    def get_category(self, obj):
        return CourseCategoryResumeSerializer(obj.category).data
    
    def get_next_lesson(self, obj):

        next_lesson = None

        lessons_order = json.loads(obj.category.lessons_order)
        lessons_in_same_category = Lesson.objects.filter(category=obj.category)

        lessons_arr = [i for i in lessons_in_same_category]
        lessons_arr.sort(key=lambda x: lessons_order.index(x.id))
        lessons_arr_ids = [i.id for i in lessons_arr]

        if obj.id in lessons_arr_ids:
            obj_idx_on_array = lessons_arr_ids.index(obj.id)
            if len(lessons_arr_ids) > (obj_idx_on_array + 1):
                next_lesson = lessons_arr[obj_idx_on_array+1]

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
    user = serializers.SerializerMethodField()

    class Meta:
        model = CommentReply
        fields = ['id', 'content', 'user', 'lesson', 'comment']
        read_only_fields = ['comment']

    def get_user(self, obj):
        user = obj.user
        serializer = UserSimpleSerializer(user)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    replies = CommentReplySerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'lesson', 'replies']

    def get_user(self, obj):
        user = obj.user
        serializer = UserSimpleSerializer(user)
        return serializer.data


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'photo']