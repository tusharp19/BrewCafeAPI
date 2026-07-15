from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self,request,view):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

class OrderBelongsToUser(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        return obj.user==request.user