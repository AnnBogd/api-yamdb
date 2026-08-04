import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from reviews.models import Category, Genre, Title, GenreTitle


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов в базу данных'

    def handle(self, *args, **options):
        csv_dir = os.path.join(settings.BASE_DIR, 'static', 'data')

        # 1. Категории
        with open(os.path.join(csv_dir, 'category.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Category.objects.get_or_create(id=row['id'], name=row['name'], slug=row['slug'])
        self.stdout.write(self.style.SUCCESS('Категории успешно загружены'))

        # 2. Жанры
        with open(os.path.join(csv_dir, 'genre.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                Genre.objects.get_or_create(id=row['id'], name=row['name'], slug=row['slug'])
        self.stdout.write(self.style.SUCCESS('Жанры успешно загружены'))

        # 3. Произведения
        with open(os.path.join(csv_dir, 'titles.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'], name=row['name'], year=row['year'], category=category
                )
        self.stdout.write(self.style.SUCCESS('Произведения успешно загружены'))

        # 4. Связи Many-to-Many через промежуточную модель GenreTitle
        with open(os.path.join(csv_dir, 'genre_title.csv'), encoding='utf-8') as f:
            for row in csv.DictReader(f):
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                GenreTitle.objects.get_or_create(title=title, genre=genre)
        self.stdout.write(self.style.SUCCESS('Связи жанров и произведений загружены'))
