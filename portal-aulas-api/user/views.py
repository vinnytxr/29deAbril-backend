from user.models import User, Role, Invitation
from user.serializers import UserSerializer, RoleSerializer, InvitationSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions
from user.permissions import CustomIsAdmin
from rest_framework import mixins


class RoleViewSet(viewsets.ModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class InvitationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, 
                                mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
  serializer_class = InvitationSerializer
  queryset = Invitation.objects.all()
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.CustomIsAdmin,)
                        
  def list(self, request):
    invitations = Invitation.objects.all()
    serializer = InvitationSerializer(invitations, many=True)

    return Response(serializer.data)

  def create(self, request):
    serializer = InvitationSerializer(data=request.data)
    
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
  def update(self, request):
      professor = request.data.pop('professor')
      instance = self.get_object()
      serializer = self.get_serializer(instance, data=request.data, professor=professor)
      serializer.is_valid(raise_exception=True)
      serializer.save()

      if getattr(instance, '_prefetched_objects_cache', None):
          # If 'prefetch_related' has been applied to a queryset, we need to
          # forcibly invalidate the prefetch cache on the instance.
          instance._prefetched_objects_cache = {}

      return Response(serializer.data)
        

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