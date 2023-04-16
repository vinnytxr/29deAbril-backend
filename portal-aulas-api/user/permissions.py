from rest_framework import exceptions, permissions

class CustomIsAuthenticated(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        
        raise exceptions.NotAuthenticated({"message": "Permissions denied"})

    