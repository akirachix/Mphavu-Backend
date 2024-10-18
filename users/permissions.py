from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdmin(BasePermission):
    """
    Custom permission for admins.
    Admins can access everything related to managing the platform, such as sending invites and viewing the dashboard.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsCoach(BasePermission):
    """
    Custom permission for coaches.
    Coaches can add teams, players, upload stats and videos, and view player performance metrics.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Coaches can view details without restrictions
        return request.user.is_authenticated and request.user.role == 'coach'


class IsAgent(BasePermission):
    """
    Custom permission for agents.
    Agents can only view teams, players, performance metrics, and uploaded videos.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS and request.user.is_authenticated and request.user.role == 'agent'