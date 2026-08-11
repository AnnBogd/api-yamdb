"""Сериализаторы приложения api."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title
from users.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from users.validators import username_validator, validate_username


User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Проверяет данные самостоятельной регистрации."""

    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(username_validator, validate_username),
    )

    def validate(self, attrs: dict) -> dict:
        """Проверить входные данные пользователя."""
        username = attrs['username']
        email = attrs['email']

        user_by_username = User.objects.filter(
            username=username
        ).first()
        user_by_email = User.objects.filter(
            email=email
        ).first()
        errors = {}
        if user_by_username and user_by_username.email != email:
            errors['username'] = (
                'Пользователь с таким username уже существует.'
            )

        if user_by_email and user_by_email.username != username:
            errors['email'] = (
                'Пользователь с таким email уже существует.'
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class TokenSerializer(serializers.Serializer):
    """Проверяет данные для получения JWT-токена."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(username_validator, validate_username),
    )
    confirmation_code = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Управление пользователями для администратора."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserMeSerializer(UserSerializer):
    """Профиль текущего пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Категорий контента."""

    class Meta:
        """Метаданные сериализатора категорий."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Жанров произведений."""

    class Meta:
        """Метаданные сериализатора жанров."""

        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного чтения произведений (GET)."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        """Метаданные сериализатора чтения произведений."""

        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False,
    )

    class Meta:
        """Метаданные сериализатора записи произведений."""

        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(
            self,
            instance: serializers.Serializer
    ) -> serializers.Serializer:
        """Выбрать сериализатор для вывода данных."""
        return TitleReadSerializer(instance, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data: dict) -> dict:
        """Проверить, что нельзя повторно оставить отзыв на произведение."""
        request = self.context.get('request')
        title_id = self.context['view'].kwargs.get('title_id')
        if request and request.method == 'POST':
            if (
                Review
                .objects
                .filter(title_id=title_id, author=request.user)
                .exists()
            ):
                raise ValidationError(
                    'Вы уже оставили отзыв на это произведение.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
