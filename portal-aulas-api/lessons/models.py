from django.db import models
from courses.models import Course, CourseCategory
from user.models import User

import os
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/courses/lessons', filename)

def get_video_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('videos/courses/lessons', filename)

def get_appendix_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('appendices/courses/lessons', filename)


class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=False)
    content = models.CharField(max_length=1024, blank=False)
    banner = models.FileField(upload_to=get_file_path, null=True, blank=True)
    video = models.FileField(upload_to=get_video_path, null=True, blank=True)
    appendix = models.FileField(upload_to=get_appendix_path, null=True, blank=True)
    title_appendix = models.CharField(max_length=64, null=True, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', null=False, blank=False)
    users_who_completed = models.ManyToManyField(User, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)

    def __str__(self):
        return "Lesson({})".format(self.title)

class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return "Comment({})".format(self.id)