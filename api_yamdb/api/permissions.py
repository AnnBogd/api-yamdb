"""Кастомные разрешения приложения api."""

from django.db.models import Model
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class IsAdmin(BasePermission):
    """Разрешает доступ только администратору или суперпользователю."""

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """Определить доступ на уровне запроса."""
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(BasePermission):
    """Разрешает чтение всем, а изменение — только администратору."""

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """Определить доступ на уровне запроса."""
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """Разрешает изменение автору, модератору или администратору."""

    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """Определить доступ на уровне запроса."""
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(
            self,
            request: Request,
            view: ViewSet,
            obj: Model
    ) -> bool:
        """Определить доступ на уровне объекта."""
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (
                obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
            )
        )
