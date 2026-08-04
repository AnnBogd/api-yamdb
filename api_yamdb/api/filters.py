"""Модуль кастомной фильтрации контента для API сервиса YaMDb."""

import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """
    Класс фильтрации произведений по слагам связанных моделей.

    Позволяет фильтровать произведения по текстовым слагам категорий
    и жанров, по году выпуска, а также выполнять частичный поиск
    по названию произведения.
    """

    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        """Метаданные фильтра для привязки к модели Title."""

        model = Title
        fields = ('category', 'genre', 'name', 'year')
