from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast, Round
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.permissions import IsAdmin, IsAdminOrReadOnly
from api.serializers import (
    CategorySerializer,
    GenreSerializer,
    SignupSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)
from reviews.models import Category, Genre, Title


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
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


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

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для работы с категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для работы с жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'delete']


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""

    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        """Возвращает произведения с фильтрацией и рейтингом."""

        queryset = Title.objects.annotate(
            rating=Cast(
                Round(Avg('reviews__score')),
                output_field=IntegerField(),
            )
        ).order_by('name')

        category_slug = self.request.query_params.get('category')
        genre_slug = self.request.query_params.get('genre')
        year = self.request.query_params.get('year')
        name = self.request.query_params.get('name')

        if category_slug is not None:
            queryset = queryset.filter(
                category__slug=category_slug
            )

        if genre_slug is not None:
            queryset = queryset.filter(
                genre__slug=genre_slug
            )

        if year is not None:
            queryset = queryset.filter(year=year)

        if name is not None:
            queryset = queryset.filter(
                name__icontains=name
            )

        return queryset

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от действия."""

        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def create(self, request, *args, **kwargs):
        """Создаёт произведение и возвращает данные для чтения."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.save()

        title_with_rating = self.get_queryset().get(pk=title.pk)
        response_serializer = TitleReadSerializer(
            title_with_rating
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Обновляет произведение и возвращает свежие данные."""

        partial = kwargs.get('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        title = serializer.save()

        title_with_rating = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).get(pk=title.pk)

        response_serializer = TitleReadSerializer(
            title_with_rating
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )