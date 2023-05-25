from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Course, Learning, Ratings
from .serializers.course import CourseSerializerForPOSTS, CourseSerializerForGETS
from .serializers.learning import LearningSerializer
from .serializers.ratings import RatingsSerializer
from user.models import User, ROLES
from django.db import models

import requests
from django.conf import settings

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

    def calculate_rating_mean(self, course_id):
        rating_sum = Ratings.objects.filter(course_id=course_id).aggregate(total_rating_sum=models.Sum('rating'))['total_rating_sum']
        return rating_sum

    # [UPDATE] /<id> 
    # body: multipart/form-data
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        new_data = dict(request.data)

        # print(new_data)

        # Verifica se há uma nova imagem na requisição
        if 'banner' in request.FILES:
            # Exclui a imagem antiga
            instance.banner.delete(save=False)
            # Salva a nova imagem
            instance.banner = request.FILES['banner']
        
        if 'rating' in request.data:
            if 'count_ratings' in request.data:
                new_data["count_ratings"] = instance.count_ratings + 1
            else:
                new_data["count_ratings"] = instance.count_ratings

            # print(new_data["count_ratings"])
            sum_rating = self.calculate_rating_mean(instance.id)
            new_mean = sum_rating / int(new_data["count_ratings"])
            # print(new_mean)
            new_data["rating"] = round(new_mean, 1)

        # print(new_data)
        
        serializer = self.get_serializer(instance, data=new_data, partial=True)
        serializer.is_valid(raise_exception=True)

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

class RatingsViewSet(viewsets.ModelViewSet):
    queryset = Ratings.objects.all()
    serializer_class = RatingsSerializer

    def create(self, request, *args, **kwargs):
        serializer = RatingsSerializer(data=request.data)
    
        if serializer.is_valid():
            try:
                serializer.save()
            except:
                return Response({"message": "Could not create the rating. Check the ids."}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'count_ratings': 1, 
                'rating': 1
            }
        
            update_url_rating = f'{settings.BASE_URL}/courses/courses/{request.data["course"]}'
            response = requests.put(update_url_rating, json=data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='update-rating/(?P<course_id>\d+)/(?P<user_id>\d+)')
    def update_rating(self, request, course_id=None, user_id=None):
        instance = Ratings.objects.get(user=user_id, course_id=course_id)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        data = {
                'rating': 1
            }
        
        update_url_rating = f'{settings.BASE_URL}/courses/courses/{course_id}'
        response = requests.put(update_url_rating, json=data)


        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='check-rating/(?P<course_id>\d+)/(?P<user_id>\d+)')
    def check_rating(self, request, course_id=None, user_id=None):
        try:
            instance = Ratings.objects.get(user=user_id, course_id=course_id)
            return Response({"result": 1}, status=status.HTTP_200_OK)
        except:
            return Response({"result": 0}, status=status.HTTP_200_OK)