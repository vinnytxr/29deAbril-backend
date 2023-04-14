from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Course, Learning
from .serializers import CourseSerializer, LearningSerializer
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # def get_object(self, pk):
    #     try:
    #         return Course.objects.get(pk=pk)
    #     except Course.DoesNotExist:
    #         raise status.HTTP_404_NOT_FOUND

    # [GET] /<id>
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    # [GET] /?page={int}&size={int}
    def list(self, request, *args, **kwargs):
        # /courses/?page=1&size=3
        print("list")
        queryset = self.filter_queryset(self.get_queryset())

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # [UPDATE] /<id> 
    # body: multipart/form-data
    def update(self, request, *args, **kwargs):
        print("update")
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
    
    # def patch(self, request):
    #     print("partial")
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)

    #     # Verifica se há uma nova imagem na requisição
    #     if 'banner' in request.FILES:
    #         # Exclui a imagem antiga
    #         instance.banner.delete(save=False)
    #         # Salva a nova imagem
    #         instance.banner = request.FILES['banner']

    #     self.perform_update(serializer)

    #     return Response(serializer.data)

    # [DELETE] /<id>
    def destroy(self, request, *args, **kwargs):
        print("destroy")
        instance = self.get_object()
        instance.banner.delete(save=False) 
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LearningViewSet(viewsets.ModelViewSet):
    queryset = Learning.objects.all()
    serializer_class = LearningSerializer
