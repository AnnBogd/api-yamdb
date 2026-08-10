"""Валидаторы приложения users."""

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from .constants import FORBIDDEN_USERNAMES


username_validator = UnicodeUsernameValidator()


def validate_username(value: str) -> None:
    """Запретить использование служебных имён пользователей."""
    if value.lower() in FORBIDDEN_USERNAMES:
        raise ValidationError(
            'Использовать это имя в качестве username запрещено.'
        )
