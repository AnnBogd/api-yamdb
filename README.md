## Описание проекта

Проект YaMDb позволяет оставлять отзывы пользователям на произведения.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен жанр из списка предустановленных.
Пользователи оставляют к произведениям текстовые отзывы и
ставят произведению оценку. Пользователи могут оставлять комментарии к отзывам.

## Стек технологий
* **Язык программирования:** Python
* **Бэкенд:** Django (5.1), Django REST Framework (3.15)
* **Аутентификация и JWT:** Djoser, SimpleJWT, Social Auth (Social App Django)
* **Тестирование:** Pytest, Pytest-Django
* **Линтеры и качество кода:** Flake8
* **Работа с изображениями:** Pillow
* **Дополнительно:** Requests (работа с внешними API), Jinja2 (шаблоны писем)

## Как запустить проект:
Использовать в командах python3 для mac OS и linux
#### Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:AnnBogd/api-yamdb.git
```
```
cd api_yamdb
```
#### Cоздать и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
#### Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
#### Создать миграции
```
python manage.py makemigrations
```
#### Применить миграции
```
python manage.py migrate
```
#### Заполнить базу данных объектами
```
python manage.py load_csv
```
#### Запустить проект
```
python manage.py runserver
```
## Документация для API
после запуска проекта перейти по адресу
```
http://127.0.0.1:8000/redoc/
```
## Примеры запросов и ответов
#### регистрация нового пользователя
POST запрос на эндпоинт /api/v1/auth/signup/
```
{
  "email": "user@example.com",
  "username": "username"
}
```
ответ API
```
{
  "email": "string",
  "username": "string"
}
```
После чего на электронную почту приходит код подтверждения
POST запрос на /api/v1/auth/token/
```
{
  "username": "username",
  "confirmation_code": "string"
}
```
ответ API
```
{
  "token": "string"
}
```
#### Заполнить поля в своем профиле
PATCH запрос на /api/v1/users/me/
```
{
  "username": "gKJU7N0N5XRZ",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string"
}
```

ответ API
```
{
  "username": "7az-d71b5rd2ufv_wAZtbO_t72.lZ",
  "email": "user@example.com",
  "first_name": "string",
  "last_name": "string",
  "bio": "string",
  "role": "user"
}
```
#### /api/v1/categories/
GET запрос - получить список категорий
ответ API
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "o-5nExwBptbQEiPZGk8PqCBo3R_f4AvqovwDaza59kKfzgpdK7"
    }
  ]
}
```
#### /api/v1/genres/
GET запрос - получить список жанров произведений
ответ API
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "B7DaT2W3sDWJxIct3q1n7jc_4jeEYTElyw_yhMGthoWXOPv-cL"
    }
  ]
}
```
#### /api/v1/titles/
GET запрос - получить список произведений
Параметры для фильтрации:
* category - фильтрует по полю slug категории
* genre - фильтрует по полю slug жанра
* name - фильтрует по названию произведения
* year - фильтрует по году

ответ API
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "GmsWoGxPRXVyOEgN5XQHXc8grNC39KMZlfbQekhM68EwTkc8ai"
        }
      ],
      "category": {
        "name": "string",
        "slug": "_vYPWtUX8JKnvumTgd3bexk5etTouRc8YPs33dYXV8jXQAjf5R"
      }
    }
  ]
}
```
#### /api/v1/titles/{titles_id}/
GET запрос - получить произведение по его id.
Ответ API
```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "c04vFGQGT4f-nUoaC0dnYji69q"
    }
  ],
  "category": {
    "name": "string",
    "slug": "iTM4CCniJ3Zrf3SskP75fJPoxxNNew7fXY-9zuu4B4HmAgUcCj"
  }
}
```
#### /api/v1/titles/{title_id}/reviews/
GET запрос - получить список отзывов на конкретное произведение
POST запрос - отправить отзыв на произведение
(аутентифицированные пользователи).
```
{
  "text": "string",
  "score": 10
}
```
Ответ API
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "text": "string",
      "author": "string",
      "score": 10,
      "pub_date": "2026-08-09T17:17:47.745Z"
    }
  ]
}
```

#### /api/v1/titles/{title_id}/reviews/{review_id}/
GET запрос - получить отзыв по его id.
PATCH запрос (автор отзыва, администратор, модератор) -
частичное изменение отзыва.
DELETE запрос (автор отзыва, администратор, модератор) - удалить отзыв.
```
{
  "text": "string",
  "score": 10
}
```
Ответ API
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 10,
  "pub_date": "2026-08-09T17:20:40.198Z"
}
```
#### /api/v1/titles/{title_id}/reviews/{review_id}/comments/
GET запрос - получить список всех комментариев к отзыву.
POST запрос - оставить комментарий к отзыву.
```
{
  "text": "string"
}
```
ответ API
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2026-08-09T17:24:27.652Z"
}
```
#### /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
GET запрос - получить комментарий по его id.
PATCH запрос (автор комментария, администратор, модератор) -
частичное изменение комментария.
DELETE запрос (автор комментария, администратор, модератор) -
удалить комментарий.
```
{
  "text": "string"
}
```
ответ API
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2026-08-09T17:25:45.377Z"
}
```
## Авторы проекта:
* Петров Георгий - работа с пользователями, регистрацией.
* Волкова Екатерина - работа с произведениями, категориями, жанрами, рейтингом,
загрузка объектов в базу данных.
* Богданова Анна - работа с отзывами, комментариями.

Yandex Practicum.
