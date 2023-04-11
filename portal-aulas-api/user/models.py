from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password

from django_extensions.db.models import (
    TimeStampedModel 
)

class Role(models.Model):
  name = models.CharField("Nome", max_length=20)

  def __str__(self):
    return self.name

# Para poder criar um usuário por linha de comando
class UserManager(auth_models.BaseUserManager):
  def create_user(self, name: str, email: str, is_staff = False, is_superuser = False, **extra_fields) -> "User":
    if not email:
      raise ValueError("Campo 'email' é obrigatório!")
    if not name:
      raise ValueError("Campo 'name' é obrigatório!")
    
    email = self.normalize_email(email)
    user = self.model(email=email, name=name, is_active=True, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
    hashed_password = make_password(password)
    user.set_password(hashed_password)
    user.save()
    
    return user

  def create_superuser(self, name: str, email: str, **extra_fields) -> "User":
    user = self.create_user(
      name=name,
      email=email,
      password=password,
      is_staff=True,
      is_superuser=True
    )

    return user
    
    

class User(TimeStampedModel, auth_models.AbstractUser):
  name = models.CharField("nome", max_length=120)
  email = models.CharField("email", max_length=120, unique=True)
  photo = models.CharField("foto", max_length=256, blank=True, null=True)
  about = models.TextField("sobre mim", blank=True, null=True)
  role = models.ManyToManyField(Role, verbose_name="cargo")

  username = None

  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["name"]

  def __str__(self):
        return self.name