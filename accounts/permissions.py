from rest_framework.permissions import BasePermission

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (request.user
                and request.user.is_authenticated
                and request.user.role
                and request.user.role.name == 'Teacher'
        )
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user