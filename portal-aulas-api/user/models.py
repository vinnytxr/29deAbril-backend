from django.db import models
from django.contrib.auth import models as auth_models
from enum import Enum
import os
import uuid
from django.core.validators import MinLengthValidator
import datetime
from django.core.exceptions import ValidationError

from django_extensions.db.models import (
    TimeStampedModel 
)

# Enum com as roles padrões
# Apenas um enum utilizado como constante no projeto
# Não possui qualquer efeito no database ou no model
class ROLES(Enum):
    STUDENT = 1
    PROFESSOR = 2
    ADMIN = 3


class Role(models.Model):
  name = models.CharField("Nome", max_length=20)

  def __str__(self):
    return self.name
    

# Para poder criar um usuário por linha de comando
class UserManager(auth_models.BaseUserManager):
  def create_user(self, name: str, email: str, password=None, is_staff = False, is_superuser = False, **extra_fields) -> "User":
    if not email:
      raise ValueError("Campo 'email' é obrigatório!")
    if not name:
      raise ValueError("Campo 'name' é obrigatório!")
    
    email = self.normalize_email(email)
    user = self.model(email=email, name=name, is_active=True, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
    user.set_password(password)
    user.save()
    
    return user

  def create_superuser(self, name: str, email: str, password=None, **extra_fields) -> "User":
    user = self.create_user(
      name=name,
      email=email,
      password=password,
      is_staff=True,
      is_superuser=True
    )

    return user
    
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('images/users', filename)

class User(TimeStampedModel, auth_models.AbstractUser):
  def validate_age(birth_date):
    today = datetime.date.today()

    birth_obj = datetime.datetime.strptime(str(birth_date), '%Y-%m-%d')

    if (today.year - birth_obj.year) < 7:
        raise ValidationError("Usuário precisa ter 7 anos ou mais para realizar o cadastro")

  name = models.CharField("nome", max_length=120)
  email = models.EmailField("email", max_length=120, unique=True)
  password = models.CharField(max_length=128, verbose_name='password', validators=[MinLengthValidator(4)])
  ra = models.CharField("ra", max_length=8, unique=True, validators=[MinLengthValidator(8)])
  photo = models.FileField("foto", upload_to=get_file_path, null=True)
  contactLink = models.URLField(max_length=200, null=True)
  about = models.TextField("sobre mim", blank=True, null=True)
  birth = models.DateField("data de nascimento", null=True, validators=[validate_age])
  role = models.ManyToManyField(Role, verbose_name="cargo")
  courses = models.ManyToManyField('courses.Course', related_name='enrolled_users', blank=True)
  favorite_courses = models.ManyToManyField('courses.Course', related_name='favorited_users', blank=True)

  username = None

  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["name"]


  def __str__(self):
        return self.name


class Invitation(models.Model):
  code = models.CharField(max_length=256, null=False, blank=True)
  professor = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)


class Anotation(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
   course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True)
   lesson = models.ForeignKey('lessons.Lesson', on_delete=models.CASCADE, null=True)
   time = models.FloatField("Tempo", null=True) # só um float da soma dos segundos
   note = models.TextField("Nota", null=True)