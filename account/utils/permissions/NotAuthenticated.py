from rest_framework.permissions import BasePermission

class Main(BasePermission):
    def has_permission(self,req,view):
        state = True if not req.user else False
        return state