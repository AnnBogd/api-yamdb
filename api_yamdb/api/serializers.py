from rest_framework import serializers
from django.core.validators import RegexValidator
from reviews.models import Category, Genre, Title
from api.validators import validate_year


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг может содержать только латиницу, цифры, дефис и подчеркивание.'
        )]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        max_length=50,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг может содержать только латиницу, цифры, дефис и подчеркивание.'
        )]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):
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
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
