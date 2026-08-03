from datetime import datetime
from django.core.exceptions import ValidationError


def get_current_year():
    """
    Возвращает текущий год как число.
    Для MaxValueValidator в модели.
    """
    return datetime.now().year


def validate_year(value):
    """
    Кастомный валидатор. Проверяет, что год <= текущему.
    """
    current_year = get_current_year()
    if value > current_year:
        raise ValidationError(
            'Год написания произведения не может быть больше текущего.',
            params={'value': value},
        )
    return value
