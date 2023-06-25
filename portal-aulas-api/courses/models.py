from django.db import models
from user.models import User 

import os
import uuid
import json

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/courses', filename)

def get_certificate_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('documents/courses/certificates', filename)

class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=265, blank=False)
    banner = models.FileField(upload_to=get_file_path)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    content = models.CharField(max_length=1024, null=False, blank=False)
    rating = models.FloatField(default=0.0, null=True)
    count_ratings = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.title 

    def learnings(self):
        return Learning.objects.filter(course=self)

class Learning(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learnings', null=False, blank=False)

class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    commentVisibility = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'course'], name='unique_rating')
        ]


class ProgressCourseRelation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['course', 'student'], name='unique_course_student_progress')
        ]


class CourseCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=64, blank=False)
    lessons_order = models.TextField()

    def set_lessons_order(self, lessons_order):
        self.lessons_order = json.dumps(lessons_order)

    def get_lessons_order(self):
        return json.loads(self.lessons_order)

    def __str__(self):
        return f"CourseCategory object ({self.pk})"