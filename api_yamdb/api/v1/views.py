"""Вьюсеты приложения api."""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, IntegerField, QuerySet
from django.db.models.functions import Cast, Round
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    mixins,
    permissions,
    serializers,
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)


User = get_user_model()


class BaseCategoryGenreViewSet(viewsets.GenericViewSet):
    """Базовый вьюсет с общими конфигурационными настройками."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class SignupView(APIView):
    """Регистрирует пользователя и отправляет код подтверждения."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        """Проверить данные пользователя и отправить код подтверждения."""
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения YaMDb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=None,
            recipient_list=(user.email,),
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class TokenView(APIView):
    """Выдаёт JWT-токен по username и коду подтверждения."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        """Выдать пользователю токен."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'],
        )
        confirmation_code = serializer.validated_data[
            'confirmation_code'
        ]

        if not default_token_generator.check_token(
            user,
            confirmation_code,
        ):
            return Response(
                {
                    'confirmation_code': [
                        'Неверный код подтверждения.'
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)},
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    """Управляет пользователями и профилем текущего пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me',
    )
    def me(self, request: Request) -> Response:
        """Просмотреть или отредактировать профиль текущего пользователя."""
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
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    BaseCategoryGenreViewSet,
):
    """Вьюсет для работы с категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    BaseCategoryGenreViewSet,
):
    """Вьюсет для работы с жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""

    queryset = Title.objects.annotate(
        rating=Cast(
            Round(Avg('reviews__score')),
            output_field=IntegerField(),
        )
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self) -> serializers.Serializer:
        """Выбрать сериализатор в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def _get_title(self) -> Title:
        """Получить произведение по его id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self) -> QuerySet:
        """Получить отзывы определенного произведения."""
        title = self._get_title()
        return title.reviews.select_related('author')

    def perform_create(self, serializer: ReviewSerializer) -> None:
        """Привязать пользователя к отзыву."""
        title = self._get_title()
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def _get_review(self) -> Review:
        """Получить отзыв по его id."""
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self) -> QuerySet:
        """Получить комментарии определенного отзыва."""
        review = self._get_review()
        return review.comments.select_related('author')

    def perform_create(self, serializer: CommentSerializer) -> None:
        """Сохранить автора комментария."""
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)
