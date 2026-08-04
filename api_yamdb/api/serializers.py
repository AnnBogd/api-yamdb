from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """Проверяет данные самостоятельной регистрации"""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def validate(self, attrs):
        username = attrs['username']
        email = attrs['email']

        user_by_username = User.objects.filter(username=username).first()
        user_by_email = User.objects.filter(email=email).first()

        if user_by_username and user_by_username.email != email:
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким username уже существует.'}
            )
        if user_by_email and user_by_email.username != username:
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )
        return attrs

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        if created:
            user.set_unusable_password()
            user.save(update_fields=('password',))
        return user


class TokenSerializer(serializers.Serializer):
    """Проверяет данные для получения JWT-токена"""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Управления пользователями для администратора"""

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

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_unusable_password()
        user.save()
        return user


class UserMeSerializer(UserSerializer):
    """Профиль текущего пользователя."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
