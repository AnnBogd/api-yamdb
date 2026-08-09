"""Модели приложения reviews."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# ИСПРАВЛЕНО: Импортируем актуальный кастомный валидатор года
from .validators import validate_year

# 2.rev Величины ограничений вынесены в константы
MAX_NAME_LENGTH = 256


class Category(models.Model):
    """Модель категорий."""

    # 2.rev Поля перенесены напрямую (абстрактный класс удален)
    name = models.CharField("Название", max_length=MAX_NAME_LENGTH)
    # ИСПРАВЛЕНО: Удален избыточный max_length=50
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("name",)

    def __str__(self) -> str:
        """Переопределить строковое представление объекта."""
        return self.name


class Genre(models.Model):
    """Модель жанров."""

    # 2.rev Поля перенесены напрямую (абстрактный класс удален)
    name = models.CharField("Название", max_length=MAX_NAME_LENGTH)
    # ИСПРАВЛЕНО: Удален избыточный max_length=50
    slug = models.SlugField("Слаг", unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("name",)

    def __str__(self) -> str:
        """Переопределить строковое представление объекта."""
        return self.name


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField("Название произведения", max_length=MAX_NAME_LENGTH)
    # 2.rev SmallIntegerField для поддержки дат до нашей эры
    year = models.SmallIntegerField(
        "Год создания произведения",
        db_index=True,
        validators=[
            # 2.rev MinValueValidator удален, оставлен кастомный валидатор
            validate_year,
        ],
    )
    description = models.TextField(
        "Описание произведения", default="", blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        verbose_name="Жанр произведения",
        blank=True,
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория произведения",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="titles",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ("name",)

    def __str__(self) -> str:
        """Переопределить строковое представление объекта."""
        return self.name


class GenreTitle(models.Model):
    """Промежуточная таблица для связи Many-to-Many между Title и Genre."""

    genre = models.ForeignKey(
        Genre,
        verbose_name="Жанр",
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        'Title',
        verbose_name="Произведениe",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Связь жанра и произведения"
        verbose_name_plural = "Связи жанров и произведений"

    def __str__(self):
        return f'{self.genre} {self.title}'


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
        ordering = ('pub_date',)
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
        ordering = ('pub_date',)

    def __str__(self) -> str:
        """Переопределить строковой представление комментария."""
        return f'Комментарий от {self.author} к отзыву "{self.review.author}"'
