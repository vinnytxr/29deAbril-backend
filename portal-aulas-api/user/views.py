from user.models import User, Role, Invitation
from user.serializers import UserSerializer, RoleSerializer, InvitationSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions
from user.permissions import CustomIsAdmin, CustomIsProfessor
from rest_framework.permissions import AllowAny
from rest_framework import mixins
from . import services


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
  
  def get_permissions(self):
    if self.action == 'update':
        return [CustomIsProfessor()]
    return [CustomIsAdmin()]
                        
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

  def get_object(self):
      queryset = self.filter_queryset(self.get_queryset())
      # make sure to catch 404's below
      id_invitation = services.fetch_invitation_by_code(self.request.data["code"])
      obj = queryset.get(pk=id_invitation)
      self.check_object_permissions(self.request, obj)
      return obj

  def put(self, request):
    instance = self.get_object()

    if instance.professor:
      return Response({'message': 'This invitation was already used'}, status=status.HTTP_400_BAD_REQUEST)

    professor = UserAPIView.get(self, request)
    partial = professor.data["id"]

    dict_data = {"code": request.data["code"], "professor": partial}

    serializer = self.get_serializer(instance, data=dict_data)
    serializer.is_valid()
    
    try:
      self.perform_update(serializer)
    except:
      return Response({'message': 'You are already accepted as a professor'}, status=status.HTTP_400_BAD_REQUEST)

    if getattr(instance, '_prefetched_objects_cache', None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
        instance._prefetched_objects_cache = {}

    return Response(serializer.data)

  def perform_update(self, serializer):
    serializer.save()

  def partial_update(self, request, *args, **kwargs):
    kwargs['partial'] = True
    return self.update(request, *args, **kwargs)
        

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