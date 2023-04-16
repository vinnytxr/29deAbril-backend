from user.models import User, Role
from user.serializers import UserSerializer, RoleSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions


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
      return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(raw_password=password):
      return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    token = services.create_token(user_id=user.id)

    resp = Response(status=status.HTTP_200_OK)

    resp.set_cookie(key="jwt", value=token, httponly=True)

    return resp

class UserAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.CustomIsAuthenticated,)

  def get(self, request):
    user = request.user

    serializer = UserSerializer(user)

    return Response(serializer.data)

class LogoutAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.CustomIsAuthenticated,)

  def post(self, request):
    resp = Response({"message": "User logout"})
    resp.delete_cookie("jwt")

    return resp