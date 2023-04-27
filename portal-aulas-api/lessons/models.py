from django.db import models
from courses.models import Course

import os
import uuid

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/courses/lessons', filename)

class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=False)
    content = models.CharField(max_length=1024, blank=False)
    banner = models.FileField(upload_to=get_file_path)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', null=False, blank=False)

    def __str__(self):
        return "Lesson({})".format(self.title)