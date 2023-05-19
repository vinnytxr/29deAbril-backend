from user.models import User, Role, Invitation
from user.serializers import UserSerializer, RoleSerializer, InvitationSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions
from user.permissions import CustomIsAdmin
from rest_framework.permissions import AllowAny
from rest_framework import mixins
from . import services


class RoleViewSet(viewsets.ModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def update_role(self, id_user):
    user = services.fetch_user_by_id(id_user)
    
    list_roles = [val for val in user.role.all()]

    list_roles.append(services.fetch_id_role_by_name("PROFESSOR"))

    updated_user = user
    updated_user.role.set(list_roles)

    _serializer = self.serializer_class(instance=user,
                                        data=updated_user,
                                        partial=True) 
    if _serializer.is_valid():
        _serializer.save()
        return Response(data=_serializer.data, status=status.HTTP_201_CREATED) 
    else:
        return Response(data=_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvitationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, 
                                mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
  serializer_class = InvitationSerializer
  queryset = Invitation.objects.all()
  authentication_classes = (authentication.CustomUserAuthentication,)
  
  def get_permissions(self):
    if self.action == 'list' or self.action == 'create' or self.action == 'destroy':
        return [CustomIsAdmin()]
    return [AllowAny()]
                        
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

      try:
        id_invitation = services.fetch_invitation_by_code(self.request.data["code"])
      except:
        return Response({'message': 'Invitation could not be fetched'}, status=status.HTTP_400_BAD_REQUEST)

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
      UserViewSet.update_role(UserViewSet, partial)
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

  def delete(self, request):
        instance = self.get_object()
        try:
          self.perform_destroy(instance)
        except:
          return Response({'message': 'Invitation could not be destroyed'}, status=status.HTTP_400_BAD_REQUEST)
          
        return Response(status=status.HTTP_200_OK)

  def perform_destroy(self, instance):
      instance.delete()

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

    resp = Response({'token': token}, status=status.HTTP_200_OK)

    # resp.set_cookie(key="jwt", value=token, httponly=False)

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
    resp = Response({"message": "Not implemented"}, status=status.HTTP_400_BAD_REQUEST)
    return resp
  
class SendEmailAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.CustomIsAdmin,)
  
  def post(self, request):
    userEmail = request.data['email']
    code = request.data['code']
    
    try:
      services.send_email(
        subject = 'Código professor (let-cursos)',
        message = f'Use o código "{code}" para se cadastrar como professor.' ,
        to_email = userEmail
      )
      return Response({"message": "E-mail enviado com sucesso"}, status=status.HTTP_200_OK)
    except:
      return Response({"message": "Falha ao enviar e-mail"}, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordAPIView(views.APIView):
  authentication_classes = (authentication.CustomUserAuthentication,)
  
  def put(self, request):
      user = request.user
      
      if 'old_password' not in request.data:
          return Response({'error': 'A senha atual é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

      if 'new_password' not in request.data:
          return Response({'error': 'A nova senha é obrigatória.'}, status=status.HTTP_400_BAD_REQUEST)

      if not user.check_password(request.data['old_password']):
          return Response({'error': 'A senha atual fornecida é incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

      user.set_password(request.data['new_password'])
      user.save()

      return Response({'message': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)
    
class GeneratePasswordAPIView(views.APIView):
  
  def post(self, request):
    userEmail = request.data['email']
    
    try:
      user = services.fetch_user_by_email(userEmail)
      new_password = User.objects.make_random_password(length=6)

      user.set_password(new_password)
      user.save()
    except:
      return Response({"message": "Usuário não cadastrado"}, status=status.HTTP_400_BAD_REQUEST)
      
    try:
      services.send_email(
        subject = 'Senha temporária (let-cursos)',
        message = f'Sua nova senha temporária é "{new_password}".' ,
        to_email = userEmail
      )
      return Response({"message": "E-mail enviado com sucesso"}, status=status.HTTP_200_OK)
    except:
      return Response({"message": "Falha ao enviar e-mail"}, status=status.HTTP_400_BAD_REQUEST)