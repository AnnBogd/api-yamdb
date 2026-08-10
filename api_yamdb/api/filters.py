import django_filters
from reviews.models import Title

#2.rev файл создан по замечанию ревьюера
class TitleFilter(django_filters.FilterSet):
    """Кастомный фильтр для произведений."""

    # Фильтруем по слагу связанных моделей
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    # Фильтр поиска по названию без учета регистра
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')
