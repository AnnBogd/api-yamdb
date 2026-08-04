from rest_framework import viewsets

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from reviews.models import Review, Title
from .permissions import IsAuthorModeratorAdminOrReadOnly
from .serializers import CommentSerializer, ReviewSerializer


class BaseViewSet(viewsets.ModelViewSet):
    """Абстрактный вьюсет для наследования. (Третий разработчик)
    
    Определяет дублирующуюся логику.
    """

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def _get_title(self) -> Title:
        """Получить произведение по его id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))


class ReviewViewSet(BaseViewSet):
    """Вьюсет для отзывов. (Третий разработчик)"""

    serializer_class = ReviewSerializer

    def get_queryset(self) -> QuerySet:
        """Получить отзывы определенного произведения."""
        title = self._get_title()
        return title.reviews.all()

    def perform_create(self, serializer: ReviewSerializer) -> None:
        """Привязать пользователя к отзыву."""
        title = self._get_title()
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(BaseViewSet):
    """Вьюсет для комментариев. (Третий разработчик)"""

    serializer_class = CommentSerializer

    def _get_review(self) -> Review:
        """Получить отзыв по его id."""
        title = self._get_title()
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title
        )

    def get_queryset(self) -> QuerySet:
        """Получить комментарии определенного отзыва."""
        review = self._get_review()
        return review.comments.all()

    def perform_create(self, serializer: CommentSerializer) -> None:
        """Сохранить автора комментария."""
        review = self._get_review()
        serializer.save(author=self.request.user, review=review)
