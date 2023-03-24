from django.urls import path
from users.views import UserListAndCreate, UserDetailChangeAndDelete

urlpatterns = [
    path('', UserListAndCreate.as_view()),
    path('<int:pk>/', UserDetailChangeAndDelete.as_view())
]