from django.db import models

class User(models.Model):
  name = models.CharField(max_length=120)
  email = models.CharField(max_length=120)
  password = models.CharField(max_length=120)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
        return self.name

