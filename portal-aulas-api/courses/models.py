from django.db import models
from user.models import User 

import os
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/courses', filename)

class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=265, blank=False)
    banner = models.FileField(upload_to=get_file_path)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    content = models.CharField(max_length=1024, null=False, blank=False)

    def __str__(self):
        return self.title 

    def learnings(self):
        return Learning.objects.filter(course=self)

class Learning(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learnings', null=False, blank=False)