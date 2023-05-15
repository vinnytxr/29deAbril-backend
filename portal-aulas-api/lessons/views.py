from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Lesson
from .serializers import LessonSerializer
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.http.response import StreamingHttpResponse
import os
from wsgiref.util import FileWrapper

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
    
    # # Endpoint personalizado para upload de video
    # @action(detail=False, methods=['post'], url_path='upload-video/(?P<lesson_id>\d+)')
    # def upload_video(self, request, lesson_id=None):
    #     lesson = get_object_or_404(Lesson, pk=lesson_id)

    #     serializer = self.get_serializer(lesson)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Endpoint personalizado para upload de video
    @action(detail=False, methods=['get'], url_path='stream-video/(?P<path>[^\s]+)')
    def stream_video(self, request, path=None):

        print("path: "+path)

        full_path = os.path.join(settings.MEDIA_ROOT, 'images', 'courses', 'lessons', path)
        if os.path.exists(full_path):
            response = FileResponse(open(full_path, 'rb'), content_type='video/mp4')
            return response
        else:
            return Response({'detail': 'File not found.'}, status=404)
        
    @action(detail=False, methods=['get'], url_path='files')
    def stream_video(self, request, path=None):
        # get the full path of the folder
        # folder_path = os.path.join(os.getcwd(), folder_path)
        folder_path = '/app/media'

        # iterate over all files in the folder and subfolders
        files = []
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                # get the full path of the file
                file_path = os.path.join(dirpath, filename)
                # get the file size in bytes
                file_size = os.path.getsize(file_path)
                # convert file size to MB
                file_size_mb = file_size / (1024 * 1024)
                # add file information to list
                files.append({'path': file_path, 'size_mb': file_size_mb})
                # add file size to total size
                total_size += file_size

        # convert total size to MB
        total_size_mb = total_size / (1024 * 1024)

        # create response JSON
        response_data = {
            'files': files,
            'total': total_size_mb
        }

        # return response
        return JsonResponse(response_data)
        

        