from django.conf import settings
from rest_framework import authentication, exceptions, status
import jwt

from . import models

class CustomUserAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.headers['jwt']

        if not token:
            raise exceptions.AuthenticationFailed({"message": "Authenticate::User not authenticated"})

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except:
            raise exceptions.AuthenticationFailed({"message": "User not authenticated"})

        user = models.User.objects.filter(id=payload["id"]).first()

        return (user, None)