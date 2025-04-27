from rest_framework import permissions

class IsMentor(permissions.BasePermission):
    """
    Allows access only to users who are mentors.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_mentor

class IsMentee(permissions.BasePermission):
    """
    Allows access only to users who are mentees.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_mentee