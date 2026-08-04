"""Сериализаторы для работы с контентом (Категории, Жанры, Произведения)."""

from django.core.validators import RegexValidator
from rest_framework import serializers

from api.validators import validate_year
from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Категорий контента."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message=(
                'Слаг может содержать только латиницу, '
                'цифры, дефис и подчеркивание.'
            )
        )]
    )

    class Meta:
        """Метаданные сериализатора категорий."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Жанров произведений."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message=(
                'Слаг может содержать только латиницу, '
                'цифры, дефис и подчеркивание.'
            )
        )]
    )

    class Meta:
        """Метаданные сериализатора жанров."""

        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного чтения произведений (GET)."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        """Метаданные сериализатора чтения произведений."""

        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения произведений (POST, PATCH)."""

    year = serializers.IntegerField(validators=[validate_year])
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        """Метаданные сериализатора записи произведений."""

        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
