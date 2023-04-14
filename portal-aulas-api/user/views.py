from user.models import User, Role
from user.serializers import UserSerializer, RoleSerializer
from rest_framework import viewsets, views, response, exceptions, permissions
from . import services, authentication


class RoleViewSet(viewsets.ModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class LoginAPIView(views.APIView):
  def post(self, request):
    email = request.data["email"]
    password = request.data["password"]

    user = services.fetch_user_by_email(email=email)

    if user is None:
      raise exceptions.AuthenticationFailed("Invalid credentials.")

    if not user.check_password(raw_password=password):
      raise exceptions.AuthenticationFailed("Invalid credentials.")

    token = services.create_token(user_id=user.id)

    resp = response.Response()

    resp.set_cookie(key="jwt", value=token, httponly=True)

    return resp

class UserAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.IsAuthenticated,)

  def get(self, request):
    user = request.user

    serializer = UserSerializer(user)

    return response.Response(serializer.data)

class LogoutAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.IsAuthenticated,)

  def post(self, request):
    resp = response.Response()
    resp.delete_cookie("jwt")
    resp.data = {"message": "User logout."}

    return resp