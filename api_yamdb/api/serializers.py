"""Сериализаторы приложения api."""

from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import ValidationError, UniqueValidator


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

    # 2.rev Явное поле slug удалено, так как ModelSerializer
    # автоматически подтягивает настройки и валидацию уникальности из модели.

    class Meta:
        """Метаданные сериализатора категорий."""
        model = Category
        fields = ('name', 'slug')
 
 
class GenreSerializer(serializers.ModelSerializer): 
    """Сериализатор для моделей Жанров произведений."""

    # 2.rev Явное поле slug удалено по аналогичной причине (избыточность)

    class Meta:
        """Метаданные сериализатора жанров."""
        model = Genre
        fields = ('name', 'slug') 

class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного чтения произведений (GET)."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    # 2.rev Удалено явное переопределение поля description.
    # Настройки (включая валидацию) автоматически подтянутся из модели.

    # 2.rev: Вместо allow_null добавлен параметр default=None
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
 
    # ИСПРАВЛЕНО: Поле year удалено, так как валидация подтянется из модели.
    
    category = serializers.SlugRelatedField( 
        slug_field='slug', 
        queryset=Category.objects.all(), 
        # Аргументы required=True и allow_null=False являются дефолтными 
        # для ForeignKey-полей модели, их можно опустить.
    ) 
    genre = serializers.SlugRelatedField( 
        slug_field='slug', 
        queryset=Genre.objects.all(), 
        many=True, 
        # ИСПРАВЛЕНО: Запрет пустого списка через атрибут вместо метода validate_genre
        allow_empty=False, 
    ) 
    
    # 2.rev Поле description удалено, настройки подтянутся из модели.
    # 2.rev Поле rating удалено (оно описывается только в сериализаторе представления).
 
    class Meta: 
        """Метаданные сериализатора записи произведений.""" 
        model = Title 
        # 2.rev Из списка полей удален 'rating'
        fields = ( 
            'id', 
            'name', 
            'year', 
            'description', 
            'genre', 
            'category', 
        ) 
 
    # 2.rev: Метод validate_genre удален за ненадобностью.

    def to_representation(
            self,
            instance: serializers.Serializer
    ) -> serializers.Serializer:
        """Выбрать сериализатор для вывода данных."""
        return TitleReadSerializer(instance, context=self.context).data


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
