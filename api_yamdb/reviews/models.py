from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.validators import get_current_year
#Анна, вот тут импорт для третьего разраба
from users.models import User


class CategoryGenreModel(models.Model):
    """Абстрактная модель для Категорий и Жанров."""
    name = models.CharField("Название", max_length=256)
    slug = models.SlugField("Слаг", max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self):
        return self.name


class Category(CategoryGenreModel):
    """Модель категорий."""
    class Meta(CategoryGenreModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Genre(CategoryGenreModel):
    """Модель жанров."""
    class Meta(CategoryGenreModel.Meta):
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField("Название произведения", max_length=256)
    year = models.PositiveSmallIntegerField(
        "Год создания произведения",
        db_index=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(get_current_year),
        ],
    )
    description = models.TextField("Описание произведения", null=True, blank=True)
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

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Промежуточная таблица для связи Many-to-Many между Title и Genre."""
    genre = models.ForeignKey(Genre, verbose_name="Жанр", on_delete=models.CASCADE)
    title = models.ForeignKey('Title', verbose_name="Произведениe", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Связь жанра и произведения"
        verbose_name_plural = "Связи жанров и произведений"

    def __str__(self):
        return f'{self.genre} {self.title}'
