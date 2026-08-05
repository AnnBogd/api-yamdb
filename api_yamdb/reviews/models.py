from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Модель отзыва."""

    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        verbose_name='Оценка произведения',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации отзыва',
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        verbose_name='Произведение',
    )

    class Meta:

        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_author_title'
            )
        ]

    def __str__(self) -> str:
        """Переопределить строковой представление отзыва."""
        return f'Отзыв от {self.author} на произведение "{self.title}"'


class Comment(models.Model):
    """Модель комментария."""

    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв',
    )

    class Meta:
        default_related_name = 'comments'

    def __str__(self) -> str:
        """Переопределить строковой представление комментария."""
        return f'Комментарий от {self.author} к отзыву "{self.review.author}"'
