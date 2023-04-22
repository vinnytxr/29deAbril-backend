import datetime
import jwt
from . import models
from . import views
from django.conf import settings
from django.utils import timezone
import pytz

def fetch_user_by_email(email: str)->"User":
    user = models.User.objects.filter(email=email).first()

    return user

def fetch_invitation_by_code(code: str)->"Invitation":
    invitation = models.Invitation.objects.filter(code=code).first()

    return invitation.id

def fetch_user_by_id(id: int)->"User":
    user = models.User.objects.filter(id=id).first()

    return user

def fetch_id_role_by_name(name: str)->int:
    role = models.Role.objects.filter(name=name).first()

    return role.id

def create_token(user_id: int)->str:
    payload = {
        "id":user_id,
        "exp":datetime.datetime.now(tz=timezone.get_current_timezone()) + datetime.timedelta(hours=24)
    }

    token=jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    return token

def create_invitation()->str:
    payload = {
        "creation_date":datetime.datetime.now(tz=timezone.get_current_timezone()).strftime("%m/%d/%Y %H:%M:%S")
    }

    code=jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    code = code[-7:]

    return code
