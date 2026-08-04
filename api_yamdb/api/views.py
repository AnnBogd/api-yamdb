from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import IsAdmin
from api.serializers import (
    SignupSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)

User = get_user_model()


class SignupView(APIView):
    """Регистрирует пользователя и отправляет код подтверждения."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=(user.email,),
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    """Выдаёт JWT-токен по username и коду подтверждения."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'],
        )
        confirmation_code = serializer.validated_data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': ['Неверный код подтверждения.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Управляет пользователями и профилем текущего пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me',
    )
    def me(self, request):
        if request.method == 'PATCH':
            serializer = UserMeSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
