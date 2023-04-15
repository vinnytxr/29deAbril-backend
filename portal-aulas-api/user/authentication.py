from django.conf import settings
from rest_framework import authentication, exceptions, status
from rest_framework.response import Response
import jwt

from . import models

class CustomUserAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except:
            return Response({"message": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        user = models.User.objects.filter(id=payload["id"]).first()

        return (user, None)