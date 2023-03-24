from users.models import User
from users.serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework import status, generics

class UserListAndCreate(generics.ListCreateAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer

class UserDetailChangeAndDelete(APIView):
  def get_object(self, pk):
    try:
      return User.objects.get(pk=pk)
    except User.DoesNotExist:
      raise NotFound()
    
  def get(self, request, pk):
    user = self.get_object(pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)
  
  def put(self, request, pk):
    user = self.get_object(pk)
    serializer = UserSerializer(user, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    user = self.get_object(pk)
    user.delete()
    return Response(status.HTTP_204_NO_CONTENT)