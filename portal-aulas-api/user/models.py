from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password, check_password

from django_extensions.db.models import (
    TimeStampedModel 
)

class Role(models.Model):
  name = models.CharField("Nome", max_length=20)

  def __str__(self):
    return self.name

class CustomPasswordField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 128
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return CustomPassword(value)

    def to_python(self, value):
        if isinstance(value, CustomPassword):
            return value
        if value is None:
            return value
        return CustomPassword(value)

    def get_prep_value(self, value):
        if isinstance(value, CustomPassword):
            return str(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, CustomPassword):
            return str(value)
        return value


class CustomPassword:
    def __init__(self, raw_password):
        self.raw_password = raw_password

    def __eq__(self, other):
        if isinstance(other, str):
            return check_password(other, self.raw_password)
        elif isinstance(other, CustomPassword):
            return check_password(other.raw_password, self.raw_password)
        return False

    def __str__(self):
        return make_password(self.raw_password)

# Para poder criar um usuário por linha de comando
class UserManager(auth_models.BaseUserManager):
  def create_user(self, name: str, email: str, password: str = None, is_staff = False, is_superuser = False, **extra_fields) -> "User":
    if not email:
      raise ValueError("Campo 'email' é obrigatório!")
    if not name:
      raise ValueError("Campo 'name' é obrigatório!")
    
    email = self.normalize_email(email)
    user = self.model(email=email, name=name, is_active=True, is_staff=is_staff, is_superuser=is_superuser, **extra_fields)
    user.set_password(password)
    user.save()
    
    return user

  def create_superuser(self, name: str, email: str, password: str = None, **extra_fields) -> "User":
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
  email = models.EmailField("email", max_length=120, unique=True)
  password = CustomPasswordField()
  photo = models.CharField("foto", max_length=256, blank=True, null=True)
  about = models.TextField("sobre mim", blank=True, null=True)
  role = models.ManyToManyField(Role, verbose_name="cargo")

  username = None

  objects = UserManager()

  USERNAME_FIELD = "email"
  REQUIRED_FIELDS = ["name"]

  def set_password(self, raw_password):
      self.password = make_password(raw_password)
  
  def check_password(self, raw_password):
      return check_password(raw_password, self.password)

  def __str__(self):
        return self.name