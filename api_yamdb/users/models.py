"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ROLE_MAX_LENGTH, USERNAME_MAX_LENGTH
from .validators import username_validator, validate_username


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
        validators=(username_validator, validate_username),
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
