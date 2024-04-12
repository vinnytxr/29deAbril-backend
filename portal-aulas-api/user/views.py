from user.models import User, Role, Invitation, Anotation
from courses.models import Course
from lessons.models import Lesson
from user.serializers import UserSerializer, RoleSerializer, InvitationSerializer, UserSerializerForListProf, AnotationSerializer, UserSerializerForListUser
from courses.serializers.course import CourseResumeSerializer
from lessons.serializers import LessonResumeSerializer
from rest_framework import viewsets, views, exceptions, status
from rest_framework.response import Response
from . import services, authentication, permissions
from user.permissions import CustomIsAdmin
from rest_framework.permissions import AllowAny
from rest_framework import mixins
from . import services
from rest_framework.settings import api_settings
from django.core.validators import URLValidator
import json
from django.db.models import Max, Value, When, Case, IntegerField
import requests
from django.conf import settings
from rest_framework.decorators import action, api_view, permission_classes

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
  
  @action(detail=False, methods=['get'], url_path='list-users', authentication_classes=[authentication.CustomUserAuthentication], permission_classes=[CustomIsAdmin])
  def list_users(self, request):
      order_by = request.query_params.get('order_by', None)

      users = User.objects.annotate(max_role=Max('role')).filter(role__in=[1, 2, 3]).distinct()

      if order_by == 'ra':
          users = users.order_by('ra')
      elif order_by == 'role':
          users = users.order_by(
              Case(
                  When(max_role=1, then=Value(0)),
                  When(max_role=2, then=Value(1)),
                  When(max_role=3, then=Value(2)),
                  default=Value(3),
                  output_field=IntegerField(),
              ),
              'ra'
          )

      serializer = UserSerializerForListUser(users, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
  
  @action(detail=False, methods=['get'], url_path='list-professors', authentication_classes = [authentication.CustomUserAuthentication], permission_classes=[CustomIsAdmin])
  def list_professors(self, request):
      professors = User.objects.filter(role__in=[2])

      serializer = UserSerializerForListProf(professors, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
  
  @action(detail=False, methods=['patch'], url_path='prof-permission/(?P<professor_id>\d+)', authentication_classes = [authentication.CustomUserAuthentication], permission_classes=[CustomIsAdmin])
  def prof_perm(self, request, professor_id=None):
    professor = User.objects.get(id=professor_id)
    acao = request.data["permission"]
    
    roles_objects = list(professor.role.all())
    roles_list = [getattr(role, 'name') for role in roles_objects]

    new_list = []

    if acao:
        if 'STUDENT' in roles_list:
           new_list.append(1)
        if 'PROFESSOR' not in roles_list:
          new_list.append(2)
        if 'ADMIN' in roles_list:
          new_list.append(3)

        data = {"role": new_list}
    else:
       if 'STUDENT' in roles_list:
           new_list.append(1)
       if 'ADMIN' in roles_list:
          new_list.append(3)
       
       data = {"role": new_list}

    partial = professor.id
        
    update_url_role = f'{settings.BASE_URL}/user/{partial}/'
    response = requests.put(update_url_role, json=data)

    response_json = json.loads(response.text)

    return Response(response_json, status=status.HTTP_200_OK, content_type='application/json')

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
    
class AnotationViewSet(viewsets.ModelViewSet):
  queryset = Anotation.objects.all()
  serializer_class = AnotationSerializer

  authentication_classes = (authentication.CustomUserAuthentication,)
  permission_classes = (permissions.CustomIsAuthenticated,)

  @action(detail=False, methods=['get'], url_path='list-notes-lesson/(?P<user_id>\d+)/(?P<lesson_id>\d+)', authentication_classes = [authentication.CustomUserAuthentication])
  def list_notes_lesson(self, request, user_id=None, lesson_id=None):
      anotations = Anotation.objects.filter(user=user_id, lesson=lesson_id)
      serializer = self.get_serializer(anotations, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)

  @action(detail=False, methods=['get'], url_path='list-notes/(?P<user_id>\d+)', authentication_classes = [authentication.CustomUserAuthentication])
  def list_notes(self, request, user_id=None):
      anotations = Anotation.objects.filter(user=user_id)

      serializer = self.get_serializer(anotations, many=True)

      input_list = serializer.data.copy()

      output_list = []
      sections = {}

      for item in input_list:
          curso_id = item["course"]
          course_object = Course.objects.get(id=curso_id)
          serializer_curso = CourseResumeSerializer(course_object)
          titulo_curso = serializer_curso.data["title"]
          if curso_id not in sections:
              sections[curso_id] = {
                  "course": curso_id,
                  "titulo": titulo_curso,
                  "notes": []
              }
          lesson_object = Lesson.objects.get(id=item["lesson"])
          serializer_lesson = LessonResumeSerializer(lesson_object)
          titulo_aula = serializer_lesson.data["title"]
          sections[curso_id]["notes"].append({
              "id": item["id"],
              "lesson": item["lesson"],
              "titulo": titulo_aula,
              "time": item["time"],
              "note": item["note"],
          })

      output_list = list(sections.values())

      return Response(output_list, status=status.HTTP_200_OK)