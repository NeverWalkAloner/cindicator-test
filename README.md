Веб сервис реализующий систему опросов.

# Установка

установите Django и djangorestframework:
```
pip install -r requirements.txt
```
запустите тесты:
```
python manage.py test polls
```


# Описание сервиса

## 1. Регистрация нового пользователя
http://127.0.0.1/sign-on/ method: POST
тело запроса:
```json
{
  "username": "username",
  "password": "password"
}
```
Тело ответа:
```json
{
  "token": "67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f",
  "user_id": 7
}
```

## 2. Получение токена для зарегистрированных пользователей
http://127.0.0.1/get-auth-token/ method: POST
тело запроса:
```json
{
  "username": "username",
  "password": "password"
}
```
Тело ответа:
```json
{
  "token": "67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f"
}
```
## 3. Получение списка опросов
http://127.0.0.1/questions/ method: GET
обязательный заголовок:
```json
Authorization: Token 67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f
```
Тело ответа:
```json
[
  {
    "title": "Выборы США 2016",
    "pub_date": "2017-01-14T13:10:31.518988Z"
  },
  {
    "title": "Победитель лиги чемпионов 2016-2017",
    "pub_date": "2017-01-14T13:10:50.770397Z"
  }
]
```

## 4. Детальная информация по опросу
http://127.0.0.1/questions/{id}/ method: GET
обязательный заголовок:
```json
Authorization: Token 67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f
```
Тело ответа:
```json
{
  "title": "Выборы США 2016",
  "text": "Кто станет президентом США",
  "date_start": "2017-01-14T00:00:00Z",
  "date_end": "2017-01-21T00:00:00Z",
  "answer_set": [
    {
      "id": 1,
      "answer_text": "Мистер\tТрамп"
    },
    {
      "id": 2,
      "answer_text": "Миссис\tКлинтон"
    }
  ]
}
```
## 5. Голосование в опросе
http://127.0.0.1/questions/{id}/vote/ method: POST
обязательный заголовок:
```json
Authorization: Token 67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f
```
Тело запроса:
```json
{
  "answer": "answer_id"
}
```

Тело ответа:
```json
{
  "user": "username",
  "question": "Выборы США 2016",
  "answer": 1
}
```
## 6. Просмотр статистики
Доступно только суперюзеру или участнику группы Clients.
http://127.0.0.1/questions/statistics/ method: GET
обязательный заголовок:
```json
Authorization: Token 67a0ebaead3d8f26a3d02ad3d18c049ff4bfa08f
```

Тело ответа:
```json
{
    "question": 1,
    "question__title": "Выборы США 2016",
    "answer__answer_text": "Мистер\tТрамп",
    "total": 4,
    "answer": 1,
    "frequency": "0.57"
  },
  {
    "question": 1,
    "question__title": "Выборы США 2016",
    "answer__answer_text": "Миссис\tКлинтон",
    "total": 3,
    "answer": 2,
    "frequency": "0.43"
  }
```
