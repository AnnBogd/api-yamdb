from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Определяет доступ к объекту. (Третий разработчик)"""

    def has_permission(
            self,
            request: Request,
            view: ViewSet
        ) -> bool:
        """Определить доступ на уровне запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(
            self,
            request: Request,
            view: ViewSet,
            obj: Model
        ) -> bool:
        """Определить доступ на уровне объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        is_moderator = getattr(request.user, 'role', None) == 'moderator'
        is_admin = (
            getattr(request.user, 'role', None) == 'admin'
            or request.user.is_staff
            or request.user.is_superuser
        )
        is_author = obj.author == request.user
        return is_author or is_moderator or is_admin
