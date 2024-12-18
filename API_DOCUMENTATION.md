# API Documentation

## Аутентификация

### Регистрация пользователя
**POST** `/api/auth/register`

**Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "client" // опционально, по умолчанию "client"
}
```

**Response:** `200 OK`
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "string"
}
```

### Получение токена (Вход)
**POST** `/api/auth/token`

**Form Data:**
- `username`: string
- `password`: string

**Response:** `200 OK`
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

## Пользователи

### Получение списка всех пользователей (только для админов)
**GET** `/api/users/`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "role": "string"
    }
]
```

### Получение списка тренеров
**GET** `/api/users/trainers`

**Response:** `200 OK`
```json
[
    {
        "id": "integer",
        "username": "string",
        "email": "string",
        "role": "trainer"
    }
]
```

### Изменение роли пользователя (только для админов)
**PUT** `/api/users/{user_id}/role`

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `role`: "admin" | "trainer" | "client"

**Response:** `200 OK`
```json
{
    "message": "Роль успешно обновлена"
}
```

## Абонементы

### Создание абонемента (для тренеров и админов)
**POST** `/api/membership/`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "user_id": "integer",
    "membership_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "visits_left": "integer",
    "status": "string"
}
```

**Response:** `200 OK`
```json
{
    "id": "integer",
    "user_id": "integer",
    "membership_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "visits_left": "integer",
    "status": "string"
}
```

### Получение своего абонемента (для всех авторизованных)
**GET** `/api/membership/my`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
    "id": "integer",
    "user_id": "integer",
    "membership_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "visits_left": "integer",
    "status": "string"
}
```

### Получение всех абонементов (для тренеров и админов)
**GET** `/api/membership/all`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
[
    {
        "id": "integer",
        "user_id": "integer",
        "membership_type": "string",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "visits_left": "integer",
        "status": "string"
    }
]
```

### Обновление абонемента (для тренеров и админов)
**PUT** `/api/membership/{membership_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "membership_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "visits_left": "integer",
    "status": "string"
}
```

**Response:** `200 OK`
```json
{
    "id": "integer",
    "user_id": "integer",
    "membership_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "visits_left": "integer",
    "status": "string"
}
```

## Коды ошибок

- `400 Bad Request` - Неверный запрос или данные
- `401 Unauthorized` - Требуется авторизация
- `403 Forbidden` - Недостаточно прав для выполнения операции
- `404 Not Found` - Ресурс не найден

## Роли и права доступа

### Администратор (admin)
- Полный доступ ко всем эндпоинтам
- Управление ролями пользователей
- Управление всеми абонементами
- Просмотр всех пользователей

### Тренер (trainer)
- Создание и редактирование абонементов
- Просмотр всех абонементов
- Просмотр списка тренеров

### Клиент (client)
- Просмотр своего абонемента
- Просмотр списка тренеров

## Примечания

1. Все запросы к защищенным эндпоинтам должны содержать заголовок авторизации:
```
Authorization: Bearer <access_token>
```

2. Токен доступа действителен в течение 30 минут

3. При регистрации пользователь по умолчанию получает роль "client"

4. Дата должна быть в формате "YYYY-MM-DD"

### Создание расписания тренера
**POST** `/api/schedule/`

**Body:**
```json
{
    "trainer_id": "integer",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM:SS",
    "end_time": "HH:MM:SS",
    "is_available": "boolean"
}
```

### Получение расписания тренера за период
**GET** `/api/schedule/trainer/{trainer_id}/period`

**Query Parameters:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD

**Response:** `200 OK`
```json
{
    "trainer": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "role": "trainer"
    },
    "schedules": [
        {
            "id": "integer",
            "date": "YYYY-MM-DD",
            "start_time": "HH:MM:SS",
            "end_time": "HH:MM:SS",
            "is_available": "boolean",
            "trainer_id": "integer"
        }
    ]
}
```

## Информация о тренерах

### Создание информации о тренере
**POST** `/api/trainers/info`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "trainer_id": "integer",
    "specialization": "string",
    "experience_years": "integer",
    "education": "string",
    "achievements": "string",
    "description": "string",
    "photo_url": "string (optional)"
}
```

### Получение информации о тренере
**GET** `/api/trainers/info/{trainer_id}`

**Response:** `200 OK`
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "trainer",
    "trainer_info": {
        "id": "integer",
        "specialization": "string",
        "experience_years": "integer",
        "education": "string",
        "achievements": "string",
        "description": "string",
        "photo_url": "string",
        "trainer_id": "integer"
    },
    "schedules": [...]
}
```

### Получение информации о всех тренерах
**GET** `/api/trainers/all`

### Обновление информации о тренере
**PUT** `/api/trainers/info/{trainer_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "specialization": "string",
    "experience_years": "integer",
    "education": "string",
    "achievements": "string",
    "description": "string",
    "photo_url": "string (optional)"
}
```

### Загрузка фото тренера
**POST** `/api/trainers/info/{trainer_id}/photo`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
- Form-data with file field

**Response:** `200 OK`
```json
{
    "photo_url": "string"
}
```


## Учет посещений и загруженность зала

### Регистрация входа в зал
**POST** `/api/visits/check-in`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "user_id": "integer",
    "membership_id": "integer"
}
```

### Регистрация выхода из зала
**POST** `/api/visits/check-out/{visit_id}`

**Headers:**
```
Authorization: Bearer <token>
```

### Текущая загруженность зала
**GET** `/api/visits/current`

**Response:** `200 OK`
```json
{
    "current_visitors": "integer",
    "max_capacity": "integer",
    "timestamp": "datetime"
}
```

### Статистика посещений за день
**GET** `/api/visits/stats/daily`

**Query Parameters:**
- `target_date`: YYYY-MM-DD (опционально, по умолчанию - текущий день)

**Response:** `200 OK`
```json
[
    {
        "current_visitors": "integer",
        "max_capacity": "integer",
        "timestamp": "datetime"
    }
]
```

### История посещений пользователя
**GET** `/api/visits/user/{user_id}`

**Query Parameters:**
- `start_date`: YYYY-MM-DD (опционально)
- `end_date`: YYYY-MM-DD (опционально)

**Response:** `200 OK`
```json
[
    {
        "id": "integer",
        "user_id": "integer",
        "membership_id": "integer",
        "check_in": "datetime",
        "check_out": "datetime"
    }
]


## Отзывы и оценки тренеров

### Создание отзыва
**POST** `/api/reviews/`

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
    "trainer_id": "integer",
    "rating": "integer (1-5)",
    "comment": "string"
}
```

### Получение отзывов тренера
**GET** `/api/reviews/trainer/{trainer_id}`

**Query Parameters:**
- `approved_only`: boolean (по умолчанию true)

**Response:** `200 OK`
```json
[
    {
        "id": "integer",
        "trainer_id": "integer",
        "user_id": "integer",
        "rating": "integer",
        "comment": "string",
        "created_at": "datetime",
        "is_approved": "boolean"
    }
]
```

### Получение статистики отзывов тренера
**GET** `/api/reviews/trainer/{trainer_id}/stats`

**Response:** `200 OK`
```json
{
    "average_rating": "float",
    "total_reviews": "integer",
    "rating_distribution": {
        "1": "integer",
        "2": "integer",
        "3": "integer",
        "4": "integer",
        "5": "integer"
    }
}
```

### Одобрение отзыва (только для админов и тренеров)
**PUT** `/api/reviews/{review_id}/approve`

### Удаление отзыва (только для админов и тренеров)
**DELETE** `/api/reviews/{review_id}`
