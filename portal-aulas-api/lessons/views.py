from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Lesson, Comment
from user.models import User
from courses.models import CompletedCourseRelation
from .serializers import LessonSerializer, CommentSerializer
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from user import authentication, permissions
from django.http.response import StreamingHttpResponse
from wsgiref.util import FileWrapper
from .serializers import LessonSerializer, LessonWithPrevNextSerializer
from wsgiref.util import FileWrapper
import os
import uuid
import cv2
import re
import mimetypes

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self
    
    def __next__(self):
        if(self.remaining is None):
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data

# Create your views here.
class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return LessonWithPrevNextSerializer
        else:
            return LessonSerializer
        
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        # Retrieve the saved object
        lesson = serializer.instance

        if 'banner' not in request.data and lesson.video is not None:
            # Access the 'banner' attribute of the saved object
            video_partial_relative_path = lesson.video.url
            if len(video_partial_relative_path) > 0 and video_partial_relative_path[0] == '/':
                video_partial_relative_path = video_partial_relative_path[1:]

            pasta_raiz = os.getcwd()
            default_path_to_store_temp_images_of_video = os.path.join(pasta_raiz, settings.MEDIA_ROOT, 'videos/courses/lessons')
            temp_video_full_path = os.path.join(pasta_raiz, video_partial_relative_path)
            name, extension = os.path.splitext(os.path.basename(temp_video_full_path))
            video_name = name
            temp_banner_path = os.path.join(default_path_to_store_temp_images_of_video, f'{video_name}.jpg')

            try:
                # Read the first frame of the video using OpenCV
                video_capture = cv2.VideoCapture(temp_video_full_path)
                ret, frame = video_capture.read() 
                video_capture.release()

                if ret:
                    cv2.imwrite(temp_banner_path, frame)

                    with open(temp_banner_path, 'rb') as file:
                        lesson.banner.save('_.jpg', file)
                    lesson.save()

                    try:
                        os.remove(temp_banner_path)
                        print(f"Arquivo {temp_banner_path} removido com sucesso.")
                    except OSError as e:
                        print(f"Falha ao remover o arquivo {temp_banner_path}: {str(e)}")
                else:
                    return Response({'error': 'Failed to capture the first frame of the video'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # [UPDATE] /<id> 
    # body: multipart/form-data
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        use_banner_from_frame_video = False

        if 'useframe' in request.data:
            use_banner_from_frame_video = True if int(request.data['useframe']) == 1 else False

        print('userframe: ', use_banner_from_frame_video)

        # Verifica se há uma nova imagem na requisição
        if 'banner' in request.FILES:
            # Exclui a imagem antiga
            instance.banner.delete(save=False)
            # Salva a nova imagem
            instance.banner = request.FILES['banner']

        if 'video' in request.FILES:
            # Exclui a imagem antiga
            instance.video.delete(save=False)
            # Salva a nova imagem
            instance.video = request.FILES['video']

        self.perform_update(serializer)

        lesson = serializer.instance

        # if 'banner' not in request.data and 'video' in request.data and lesson.video is not None:
        if use_banner_from_frame_video and lesson.video is not None:
            # Access the 'banner' attribute of the saved object
            video_partial_relative_path = lesson.video.url
            if len(video_partial_relative_path) > 0 and video_partial_relative_path[0] == '/':
                video_partial_relative_path = video_partial_relative_path[1:]

            pasta_raiz = os.getcwd()
            default_path_to_store_temp_images_of_video = os.path.join(pasta_raiz, settings.MEDIA_ROOT, 'videos/courses/lessons')
            temp_video_full_path = os.path.join(pasta_raiz, video_partial_relative_path)
            name, extension = os.path.splitext(os.path.basename(temp_video_full_path))
            video_name = name
            temp_banner_path = os.path.join(default_path_to_store_temp_images_of_video, f'{video_name}.jpg')

            try:
                # Read the first frame of the video using OpenCV
                video_capture = cv2.VideoCapture(temp_video_full_path)
                ret, frame = video_capture.read() 
                video_capture.release()

                if ret:
                    cv2.imwrite(temp_banner_path, frame)

                    with open(temp_banner_path, 'rb') as file:
                        lesson.banner.save('_.jpg', file)
                    lesson.save()

                    try:
                        os.remove(temp_banner_path)
                        print(f"Arquivo {temp_banner_path} removido com sucesso.")
                    except OSError as e:
                        print(f"Falha ao remover o arquivo {temp_banner_path}: {str(e)}")
                else:
                    return Response({'error': 'Failed to capture the first frame of the video'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.data)
    
    # [PATCH] /<id> 
    # body: multipart/form-data
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'], url_path='complete-course/(?P<lesson_id>\d+)/(?P<student_id>\d+)')
    def complete_course(self, request, lesson_id=None, student_id=None):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        student = get_object_or_404(User, pk=student_id)

        

        lesson.users_who_completed.add(student)
        lesson.save()

        serializer = self.get_serializer(lesson)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='stream-video/(?P<path>[^\s]+)')
    def stream_video(self, request, path=None):

        full_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'courses', 'lessons', path)

        if not os.path.exists(full_path):
            raise Http404("File not found")
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        size = os.path.getsize(full_path)
        content_type, encoding = mimetypes.guess_type(full_path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >- size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(RangeFileWrapper(open(full_path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            resp = StreamingHttpResponse(FileWrapper(open(full_path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        return resp
        
    @action(detail=False, methods=['get'], url_path='files')
    def info_files(self, request, path=None):

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
        
class CommentViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.CustomUserAuthentication,)
    permission_classes = (permissions.CustomIsAuthenticated,)

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        lesson_id = kwargs['lesson_id']
        user_id = request.user.id
        data = request.data.copy()
        data['lesson'] = lesson_id
        data['user'] = user_id
        print(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, user_id)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def create_reply(self, request, *args, **kwargs):
        parent_comment = self.get_object()
        lesson_id = kwargs['lesson_id']
        user_id = request.user.id
        data = request.data.copy()
        data['lesson'] = lesson_id
        data['user'] = user_id
        print(data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create_reply(serializer, parent_comment, user_id)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, user_id):
        serializer.save(user_id=user_id)
    
    def perform_create_reply(self, serializer, parent_comment, user_id):
        serializer.save(parent=parent_comment, user_id=user_id)

    def list(self, request, *args, **kwargs):
        lesson_id = kwargs['lesson_id']
        queryset = self.filter_queryset(self.get_queryset().filter(lesson_id=lesson_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        lesson_id = kwargs['lesson_id']
        instance = self.get_object()
        user_id = request.user.id
        data = request.data.copy()
        data['lesson'] = lesson_id
        data['user'] = user_id
        
        # Verifique se o usuário é o proprietário do comentário
        if instance.user != request.user:
            return Response({'detail': 'Você não tem permissão para atualizar este comentário.'}, status=status.HTTP_403_FORBIDDEN)

        # Atualize o comentário com os dados fornecidos
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)  