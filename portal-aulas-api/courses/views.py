from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Course, Learning
from .serializers import CourseSerializer, LearningSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verifica se há uma nova imagem na requisição
        if 'banner' in request.FILES:
            # Exclui a imagem antiga
            instance.banner.delete(save=False)
            # Salva a nova imagem
            instance.banner = request.FILES['banner']

        self.perform_update(serializer)

        return Response(serializer.data)

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
