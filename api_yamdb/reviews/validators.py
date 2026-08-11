"""Кастомные валидаторы приложения reviews"""

from datetime import datetime

from django.core.exceptions import ValidationError


YEAR_ERROR_MESSAGE = ("Год написания произведения не может быть больше "
                      "текущего.")


def validate_year_not_in_future(value: int) -> None:
    """Проверить, что год написания произведения не больше текущего."""
    current_year = datetime.now().year

    if value > current_year:
        raise ValidationError(
            YEAR_ERROR_MESSAGE,
            params={"value": value},
        )
