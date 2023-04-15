from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Lesson
from .serializers import LessonSerializer

# Create your views here.
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

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