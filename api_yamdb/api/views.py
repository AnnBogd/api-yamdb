"""Представления (Views) для управления контентом сервиса YaMDb."""

from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response

from reviews.models import Category, Genre, Title
from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    Вьюсет для работы с категориями произведений.

    Предоставляет возможность всем пользователям просматривать список категорий.
    Создание и удаление категорий доступно только администраторам.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    Вьюсет для работы с жанрами произведений.

    Позволяет анонимным пользователям просматривать существующие жанры.
    Управление записями (создание и удаление) ограничено ролью администратора.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete', 'head', 'options']


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления произведениями (фильмы, книги, музыка).

    Динамически вычисляет средний рейтинг на основе оценок в отзывах.
    Разделяет логику сериализаторов для безопасного чтения и записи данных.
    """

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def create(self, request, *args, **kwargs):
        """Создает произведение и возвращает развернутый JSON с рейтингом."""
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.save()
        
        # Гарантия вывода рейтинга
        title_with_rating = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).get(pk=title.pk)
        response_serializer = TitleReadSerializer(title_with_rating)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Частично обновляет произведение и возвращает свежий JSON."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer_class()(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        title = serializer.save()
        
        title_with_rating = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).get(pk=title.pk)
        response_serializer = TitleReadSerializer(title_with_rating)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
