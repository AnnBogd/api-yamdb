"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ROLE_MAX_LENGTH, USERNAME_MAX_LENGTH
from .validators import (
    validate_username_characters,
    validate_username_not_forbidden,
)


class User(AbstractUser):
    """Пользователь проекта YaMDb."""

    class Role(models.TextChoices):
        """Роли пользователей YaMDb."""

        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(
            validate_username_characters,
            validate_username_not_forbidden,
        ),
    )
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
    )
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        """Вернуть имя пользователя."""
        return self.username

    @property
    def is_admin(self) -> bool:
        """Проверить права администратора с учётом суперпользователя."""
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        """Проверить, назначена ли пользователю роль модератора."""
        return self.role == self.Role.MODERATOR
