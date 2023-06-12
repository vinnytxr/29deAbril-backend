from user.models import User, Role, Invitation
from courses.models import Course
from user.serializers import UserSerializer, RoleSerializer, InvitationSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions
from user.permissions import CustomIsAdmin
from rest_framework.permissions import AllowAny
from rest_framework import mixins
from . import services
from rest_framework.settings import api_settings
from django.core.validators import URLValidator

import requests
from django.conf import settings
from rest_framework.decorators import action

class RoleViewSet(viewsets.ModelViewSet):
  queryset = Role.objects.all()
  serializer_class = RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

  def perform_create(self, serializer):
      serializer.save()

  def get_success_headers(self, data):
      try:
          return {'Location': str(data[api_settings.URL_FIELD_NAME])}
      except (TypeError, KeyError):
          return {}

  # [UPDATE] /<id> 
  # body: multipart/form-data
  def update(self, request, *args, **kwargs):
      instance = self.get_object()
      serializer = self.get_serializer(instance, data=request.data, partial=True)
      serializer.is_valid(raise_exception=True)

      # Verifica se há uma nova imagem na requisição
      if 'photo' in request.FILES:
        # Exclui a imagem antiga
        instance.photo.delete(save=False)
        
        # Salva a nova imagem
        instance.photo = request.FILES['photo']

      if 'contactLink' in request.data:
        validate = URLValidator()
        validate(request.data["contactLink"])

      self.perform_update(serializer)

      return Response(serializer.data)
  
  # [PATCH] /<id> 
  # body: multipart/form-data
  def partial_update(self, request, *args, **kwargs):
      return self.update(request, *args, **kwargs)

  # [DELETE] /<id>
  def destroy(self, request, *args, **kwargs):
      instance = self.get_object()
      instance.photo.delete(save=False) 
      self.perform_destroy(instance)
      return Response(status=status.HTTP_204_NO_CONTENT)
  
  @action(detail=False, methods=['get'], url_path='list-professors')
  def list_professors(self, request):
      professors = User.objects.filter(role__in=[2])

      serializer = self.get_serializer(professors, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

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

      id_invitation = services.fetch_invitation_by_code(self.request.data["code"])

      obj = queryset.get(pk=id_invitation)
      self.check_object_permissions(self.request, obj)

      return obj

  def put(self, request):
    try:
      instance = self.get_object()
    except:
        return Response({'error': 'Convite inválido'}, status=status.HTTP_400_BAD_REQUEST)

    if instance.professor:
      return Response({'error': 'Este convite já foi utilizado'}, status=status.HTTP_400_BAD_REQUEST)

    professor = UserAPIView.get(self, request)
    partial = professor.data["id"]

    dict_data = {"code": request.data["code"], "professor": partial}

    serializer = self.get_serializer(instance, data=dict_data)
    serializer.is_valid()
    
    try:
      self.perform_update(serializer)
    except:
      return Response({'error': 'Você já foi aceito como um professor'}, status=status.HTTP_400_BAD_REQUEST)

    roles_list = professor.data["role"]

    roles_list.append(2)

    data = {"role": roles_list}
        
    update_url_role = f'{settings.BASE_URL}/user/{partial}/'
    response = requests.put(update_url_role, json=data)

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
          return Response({'error': 'Convite não pode ser destruido'}, status=status.HTTP_400_BAD_REQUEST)
          
        return Response(status=status.HTTP_200_OK)

  def perform_destroy(self, instance):
      instance.delete()

class LoginAPIView(views.APIView):
  def post(self, request):
    email = request.data["email"]
    password = request.data["password"]

    user = services.fetch_user_by_email(email=email)

    if user is None:
      return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(raw_password=password):
      return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

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

    info = serializer.data.copy()
    
    del info["password"]

    return Response(info)

class UserPerfil(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)
    info = {"name": serializer.data["name"], "about": serializer.data["about"], "contactLink": serializer.data["contactLink"], "photo": serializer.data["photo"], "created": serializer.data["created"]}

    return Response(info)

    
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
      return Response({"error": "Usuário não cadastrado."}, status=status.HTTP_400_BAD_REQUEST)
      
    try:
      services.send_email(
        subject = 'Senha temporária (let-cursos)',
        message = f'Sua nova senha temporária é "{new_password}".' ,
        to_email = userEmail
      )
      return Response({"message": "E-mail enviado com sucesso."}, status=status.HTTP_200_OK)
    except:
      return Response({"error": "Falha ao enviar e-mail."}, status=status.HTTP_400_BAD_REQUEST)