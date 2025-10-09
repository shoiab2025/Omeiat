from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'admin'

class IsInstitution(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'institution'

class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'job_seeker'
