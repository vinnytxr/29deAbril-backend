import datetime
import jwt
from . import models
from django.conf import settings
from django.utils import timezone
import pytz

def fetch_user_by_email(email: str)->"User":
    user = models.User.objects.filter(email=email).first()

    return user

def create_token(user_id: int)->str:
    payload = {
        "id":user_id,
        "exp":datetime.datetime.now(tz=timezone.get_current_timezone()) + datetime.timedelta(hours=24)
    }

    token=jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    return token
