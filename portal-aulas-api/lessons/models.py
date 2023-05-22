from django.db import models
from courses.models import Course
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

class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=False)
    content = models.CharField(max_length=1024, blank=False)
    banner = models.FileField(upload_to=get_file_path, null=True, blank=True)
    video = models.FileField(upload_to=get_video_path, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', null=False, blank=False)
    users_who_completed = models.ManyToManyField(User)

    def __str__(self):
        return "Lesson({})".format(self.title)