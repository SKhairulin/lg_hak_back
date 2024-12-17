# API Documentation

## Содержание
- [Аутентификация](#аутентификация)
- [Пользователи](#пользователи)
- [Абонементы](#абонементы)
- [Коды ошибок](#коды-ошибок)
- [Роли и права доступа](#роли-и-права-доступа)
- [Примечания](#примечания)

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
```
