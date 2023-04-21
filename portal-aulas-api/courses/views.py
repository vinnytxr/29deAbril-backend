from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Course, Learning
from .serializers.course import CourseSerializerForPOSTS, CourseSerializerForGETS
from .serializers.learning import LearningSerializer
from user.models import User, ROLES

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    # Sobreescrita para utilizar Serializadores diferêntes dependêndo do endpoint
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseSerializerForPOSTS
        else:
            return CourseSerializerForGETS

    # [GET] /<id>
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    # [GET] /?page={int}&size={int}&professor={int}
    def list(self, request, *args, **kwargs):
        # /courses/?page=1&size=3
        queryset = self.filter_queryset(self.get_queryset())

        queryset_courses_by_professor = queryset
        queryset_student_by_student = queryset



        # Verifica se o parâmetro "professor" existe na query string
        professor_id = request.query_params.get('professor')
        if professor_id:
            if not professor_id.isdigit():
                return Response({'professor': 'This query param must be a integer primary key'}, status=status.HTTP_400_BAD_REQUEST)
            # Filtra o queryset para retornar apenas os cursos associados ao professor com o id passado
            queryset_courses_by_professor = queryset.filter(professor__id=professor_id)

        student_id = request.query_params.get('student')
        if student_id:
            if not student_id.isdigit():
                return Response({'student': 'This query param must be a integer primary key'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                student = User.objects.get(id=student_id)
                queryset_student_by_student = student.courses.all()
            except User.DoesNotExist:
                queryset_student_by_student = Course.objects.none()

        queryset = queryset.intersection(queryset_courses_by_professor, queryset_student_by_student)

        # Verifica se o parâmetro "page" existe na query string
        page_number = request.query_params.get('page')
        if page_number is None:
            # Define o tamanho da página como o total de objetos no queryset
            page_size = queryset.count()
        else:
            # Obtém o tamanho da página da query string ou usa o padrão
            page_size = request.query_params.get('size', queryset.count())

        # Define o tamanho da página para a paginação
        self.paginator.page_size = page_size
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # [CREATE]
    # body: multipart/form-data
    def create(self, request, *args, **kwargs):
        professor_id = self.request.data.get('professor')

        if not professor_id or not professor_id.isdigit():
            return Response(
                {'professor': ['This field is required as a integer primary key']},
                status=status.HTTP_403_FORBIDDEN
            )

        professor = User.objects.get(id=professor_id)

        if not professor.role.filter(id=ROLES.PROFESSOR.value).exists():
            return Response(
                {'professor': ['This user does not have permission to perform Professor\'s operations.']},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # [UPDATE] /<id> 
    # body: multipart/form-data
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Verifica se há uma nova imagem na requisição
        if 'banner' in request.FILES:
            # Exclui a imagem antiga
            instance.banner.delete(save=False)
            # Salva a nova imagem
            instance.banner = request.FILES['banner']

        self.perform_update(serializer)

        return Response(serializer.data)
    
    # [PATCH] /<id> 
    # body: multipart/form-data
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    # [DELETE] /<id>
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.banner.delete(save=False) 
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Endpoint personalizado que retorna apenas os cursos em que um professor está matriculado
    @action(detail=False, methods=['post'], url_path='enroll-student/(?P<course_id>\d+)/(?P<student_id>\d+)')
    def student_courses(self, request, course_id=None, student_id=None):
        student = get_object_or_404(User, pk=student_id)
        course = get_object_or_404(Course, pk=course_id)

        student.courses.add(course)
        student.save()

        serializer = self.get_serializer(course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LearningViewSet(viewsets.ModelViewSet):
    queryset = Learning.objects.all()
    serializer_class = LearningSerializer
