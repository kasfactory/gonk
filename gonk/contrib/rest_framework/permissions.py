from rest_framework.permissions import BasePermission


class CanCreateTaskPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.has_perm('gonk.can_create_task')


class CanCancelTaskPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.has_perm('gonk.can_cancel_task') and request.user.username == obj.username


class CanRevertTaskPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.get_taskrunner().reversible:
            return False

        return request.user.is_superuser or request.user.has_perm('gonk.can_revert_task') and request.user.username == obj.username
