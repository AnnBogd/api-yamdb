"""URLS первой версии приложения api."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupView,
    TitleViewSet,
    TokenView,
    UserViewSet,
)


api_v1_router = DefaultRouter()
api_v1_router.register('users', UserViewSet, basename='users')
api_v1_router.register('categories', CategoryViewSet, basename='categories')
api_v1_router.register('genres', GenreViewSet, basename='genres')
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
api_v1_router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(
        'auth/signup/',
        SignupView.as_view(),
        name='signup',
    ),
    path(
        'auth/token/',
        TokenView.as_view(),
        name='token',
    ),
    path('', include(api_v1_router.urls)),
]
