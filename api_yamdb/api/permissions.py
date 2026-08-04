from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    """Разрешает доступ только администратору или суперпользователю."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'is_admin', False)
        )


class IsAdminOrReadOnly(BasePermission):
    """Разрешает чтение всем, а изменение — только администратору."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and getattr(request.user, 'is_admin', False)
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """Разрешает изменение автору, модератору или администратору."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or getattr(request.user, 'is_moderator', False)
            or getattr(request.user, 'is_admin', False)
        )
