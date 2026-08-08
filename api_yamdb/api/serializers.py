"""Сериализаторы приложения api."""

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import ValidationError, UniqueValidator

from api.validators import validate_year
from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


def validate_username_not_me(value: str) -> str:
    """Запретить использовать служебное имя `me`."""
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
    return value


class SignupSerializer(serializers.Serializer):
    """Проверяет данные самостоятельной регистрации."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_me,
        ],
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

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {
                    'username':
                    'Пользователь с таким username уже существует.'
                }
            )

        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                {
                    'email':
                    'Пользователь с таким email уже существует.'
                }
            )

        return attrs

    def create(self, validated_data: dict) -> AbstractUser:
        """Создать нового пользователя и установить невалидный пароль."""
        user, created = User.objects.get_or_create(**validated_data)

        if created:
            user.set_unusable_password()
            user.save(update_fields=('password',))

        return user


class TokenSerializer(serializers.Serializer):
    """Проверяет данные для получения JWT-токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Управление пользователями для администратора."""

    username = serializers.CharField(
        max_length=150,
        validators=[
            UnicodeUsernameValidator(),
            validate_username_not_me,
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

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

    def create(self, validated_data: dict) -> AbstractUser:
        """Создать нового пользователя и установить невалидный пароль."""
        user = super().create(validated_data)
        user.set_unusable_password()
        user.save(update_fields=('password',))
        return user


class UserMeSerializer(UserSerializer):
    """Профиль текущего пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Категорий контента."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            # Этот валидатор спасёт от UNIQUE constraint failed
            UniqueValidator(
                queryset=Category.objects.all(),
                message='Категория с таким slug уже существует.'
            )
        ],
    )

    class Meta:
        """Метаданные сериализатора категорий."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для моделей Жанров произведений."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            # Проверяем уникальность слага по таблице жанров
            UniqueValidator(
                queryset=Genre.objects.all(),
                message='Жанр с таким slug уже существует.'
            )
        ],
    )

    class Meta:
        """Метаданные сериализатора жанров."""

        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного чтения произведений (GET)."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, allow_null=True)
    #rating = serializers.IntegerField(read_only=True)

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

    year = serializers.IntegerField(validators=[validate_year])
    
    # Категория должна быть обязательной (без allow_null), чтобы ловить опечатки типа "categoty"
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    
    # Для жанров ОБЯЗАТЕЛЬНО возвращаем allow_empty=True, 
    # чтобы можно было создавать произведения без жанров
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=True
    )
    
    rating = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        """Метаданные сериализатора записи произведений."""
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

    def to_representation(self, instance):
        """При выводе данных использует структуру сериализатора чтения."""
        return TitleReadSerializer(instance).data

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    score = serializers.IntegerField(min_value=1, max_value=10)

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
                .filter(title__id=title_id, author=request.user)
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
