from datetime import datetime
from django.core.exceptions import ValidationError


def get_current_year():
    """Возвращает текущий год как число для MaxValueValidator в модели."""
    return datetime.now().year


def validate_year(value):
    """Год написания произведения <= текущему (для сериализаторов)."""
    current_year = get_current_year()
    if value > current_year:
        raise ValidationError(
            'Год написания произведения не может быть больше текущего.',
            params={'value': value},
        )
    return value
