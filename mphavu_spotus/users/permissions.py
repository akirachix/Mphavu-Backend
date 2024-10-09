from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsAuthenticatedAndHasPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('Admin')
class HasTotostepsPermissions(BasePermission):
    """
    Custom permission for admins.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        totosteps_permissions = [
            'users.can_add_parent',
            'users.can_edit_questions',
            'users.can_view_parents',
            'users.can_view_children',
        ]
        return any(request.user.has_perm(perm) for perm in totosteps_permissions)
class HasParentPermissions(BasePermission):
    """
    Custom permission for parents.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        parent_permissions = [
            'users.can_add_child',
            'users.can_view_resources',
            'users.can_view_milestones',
            'users.can_view assessment',
            'users.can_view_results',
            'users.can_add_autism_ image',
            'users.can_view_children',
            'users.can_edit_questions',
        ]
        return any(request.user.has_perm(perm) for perm in parent_permissions)
class HasAdminPermissions(BasePermission):
    """
    Custom permission for admin.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        admin_permissions = [
            'users.view_dashboard',
        ]
        return any(request.user.has_perm(perm) for perm in admin_permissions)