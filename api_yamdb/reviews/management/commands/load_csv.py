"""Management-команда для импорта тестовых данных из CSV в базу данных."""

import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title


User = get_user_model()


class Command(BaseCommand):
    """Класс команды импорта данных из CSV-файлов."""

    help = 'Импорт данных из CSV файлов в базу данных'

    def _reset_sequences(self, model):
        """Сбросить и обновить счетчики ID в базе данных после импорта."""
        table_name = model._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(
                f'UPDATE sqlite_sequence SET seq = '
                f'(SELECT MAX(id) FROM {table_name}) '
                f'WHERE name = "{table_name}";'
            )

    def handle(self, *args, **options):
        """Логика последовательного чтения и сохранения данных из CSV."""
        csv_dir = os.path.join(settings.BASE_DIR, 'static', 'data')
        with open(os.path.join(csv_dir, 'users.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                User.objects.get_or_create(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row.get('bio', ''),
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', '')
                )
        self._reset_sequences(User)
        self.stdout.write(self.style.SUCCESS('Пользователи успешно загружены'))
        with open(
            os.path.join(csv_dir, 'category.csv'),
            encoding='utf-8'
        ) as f:
            for row in csv.DictReader(f):
                Category.objects.get_or_create(
                    id=row['id'], name=row['name'], slug=row['slug']
                )
        self._reset_sequences(Category)
        self.stdout.write(self.style.SUCCESS('Категории успешно загружены'))
        with open(os.path.join(csv_dir, 'genre.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Genre.objects.get_or_create(
                    id=row['id'], name=row['name'], slug=row['slug']
                )
        self._reset_sequences(Genre)
        self.stdout.write(self.style.SUCCESS('Жанры успешно загружены'))
        with open(os.path.join(csv_dir, 'titles.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category=category
                )
        self._reset_sequences(Title)
        self.stdout.write(self.style.SUCCESS('Произведения успешно загружены'))

        with open(
            os.path.join(csv_dir, 'genre_title.csv'),
            encoding='utf-8'
        ) as f:
            for row in csv.DictReader(f):
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                GenreTitle.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'title': title,
                        'genre': genre
                    }
                )
        self._reset_sequences(GenreTitle)
        self.stdout.write(
            self.style.SUCCESS('Связи жанров и произведений загружены')
        )
        with open(os.path.join(csv_dir, 'review.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'text': row['text'],
                        'author': author,
                        'score': row['score'],
                        'pub_date': row['pub_date'],
                        'title': title,
                    }
                )
        self._reset_sequences(Review)
        self.stdout.write(self.style.SUCCESS('Отзывы успешно загружены'))
        with open(
            os.path.join(csv_dir, 'comments.csv'),
            encoding='utf-8'
        ) as f:
            for row in csv.DictReader(f):
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'review': review,
                        'text': row['text'],
                        'author': author,
                        'pub_date': row['pub_date']
                    }
                )
        self._reset_sequences(Comment)
        self.stdout.write(self.style.SUCCESS('Комментарии успешно загружены'))
