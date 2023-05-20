import datetime
import jwt
from . import models
from . import views
from django.conf import settings
from django.utils import timezone
import pytz

from django.core.mail import EmailMessage, get_connection
from django.conf import settings

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

def validate_age(birth_date)->bool:
    today = datetime.date.today()

    birth_obj = datetime.datetime.strptime(birth_date, '%Y-%m-%d')

    if (today.year - birth_obj.year) < 7:
        return False
    return True
def send_email(subject: str, message: str, to_email: str):
    with get_connection(  
        host=settings.EMAIL_HOST, 
            port=settings.EMAIL_PORT,  
            username=settings.EMAIL_HOST_USER, 
            password=settings.EMAIL_HOST_PASSWORD, 
            use_tls=settings.EMAIL_USE_TLS  
        ) as connection:  
            email_from = settings.EMAIL_HOST_USER  
            recipient_list = [f'{to_email}']  
            email = EmailMessage(subject, message, email_from, recipient_list, connection=connection)
            email.content_subtype = "html"
            email.send()
        
