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

class CustomUserAuthenticationWIthoutError(authentication.BaseAuthentication):
     def authenticate(self, request):
        token = request.headers.get('jwt')

        if token is None:
            return None  # Retorna None se o token não estiver presente

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user = models.User.objects.filter(id=payload["id"]).first()
            return (user, None)
        except jwt.ExpiredSignatureError:
            return None, {"message": "Token de autenticação expirado"}
        except jwt.InvalidTokenError:
            return None, {"message": "Token de autenticação inválido"}