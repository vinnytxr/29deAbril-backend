from django.db import models

class User(models.Model):
  name = models.CharField(max_length=120)
  created_at = models.DateField(auto_now_add=True)

