# Структура базы данных фитнес-центра

## 1. User (Пользователь)
Основная таблица для хранения информации о пользователях системы.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор пользователя
- username: String (уникальный) - Логин пользователя
- email: String (уникальный) - Email адрес пользователя
- hashed_password: String - Хэшированный пароль
- role: String - Роль пользователя (admin/trainer/client/manager)
- phone: String (опционально) - Номер телефона
- created_at: DateTime - Дата создания аккаунта

**Связи:**
- membership: один к одному с GymMembership - Текущий абонемент
- schedules: один ко многим с TrainerSchedule - Расписание (для тренеров)
- trainer_info: один к одному с TrainerInfo - Информация о тренере
- visits: один ко многим с GymVisit - История посещений
- notifications: один ко многим с Notification - Уведомления пользователя
- news: один ко многим с News - Созданные новости (для админов)
- payments: один ко многим с Payment - История платежей

## 2. GymMembership (Абонемент)
Информация об абонементах пользователей.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор абонемента
- user_id: Integer (FK) - ID владельца абонемента
- membership_type_id: Integer (FK) - Тип абонемента
- start_date: Date - Дата начала действия
- end_date: Date - Дата окончания действия
- visits_left: Integer - Оставшееся количество посещений
- status: String - Статус абонемента (active/frozen/expired)
- freeze_end_date: Date - Дата окончания заморозки
- freeze_reason: String - Причина заморозки

**Связи:**
- user: многие к одному с User - Владелец абонемента
- visits: один ко многим с GymVisit - Посещения по абонементу
- membership_type: многие к одному с MembershipType - Тип абонемента

## 3. TrainerSchedule (Расписание тренера)
Расписание занятий и доступность тренеров.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор записи расписания
- trainer_id: Integer (FK) - ID тренера
- date: Date - Дата занятия
- start_time: Time - Время начала
- end_time: Time - Время окончания
- is_available: Boolean - Доступность для записи
- training_type: String - Тип тренировки (personal/group)
- max_participants: Integer - Максимальное количество участников
- current_participants: Integer - Текущее количество участников
- name: String - Название занятия
- description: String - Описание занятия
- timezone: String - Часовой пояс

**Связи:**
- trainer: многие к одному с User - Тренер
- participants: один ко многим с TrainingParticipant - Участники тренировки

## 4. TrainerInfo (Информация о тренере)
Дополнительная информация о тренерах.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор
- trainer_id: Integer (FK, уникальный) - ID тренера
- specialization: String - Специализация
- experience_years: Integer - Стаж работы
- education: String - Образование
- achievements: String - Достижения
- description: String - Описание
- photo_url: String - Путь к фотографии
- rating: Float - Средний рейтинг
- price_per_hour: Decimal - Стоимость персональной тренировки

**Связи:**
- trainer: один к одному с User - Тренер
- reviews: один ко многим с TrainerReview - Отзывы

## 5. GymVisit (Посещение)
Учет посещений фитнес-центра.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор посещения
- user_id: Integer (FK) - ID пользователя
- check_in: DateTime - Время входа
- check_out: DateTime - Время выхода
- membership_id: Integer (FK) - ID абонемента
- duration: Integer - Длительность посещения в минутах
- visit_type: String - Тип посещения (gym/pool/group_training)

**Связи:**
- user: многие к одному с User - Посетитель
- membership: многие к одному с GymMembership - Использованный абонемент

## 6. TrainerReview (Отзывы о тренере)
Отзывы клиентов о тренерах.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор отзыва
- trainer_id: Integer (FK) - ID тренера
- user_id: Integer (FK) - ID автора отзыва
- rating: Integer - Оценка (1-5)
- comment: String - Текст отзыва
- created_at: DateTime - Дата создания
- is_approved: Boolean - Статус модерации
- reply: String - Ответ тренера
- reply_date: DateTime - Дата ответа

**Связи:**
- trainer: многие к одному с User - Тренер
- user: многие к одному с User - Автор отзыва

## 7. News (Новости)
Новости и объявления фитнес-центра.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор новости
- title: String - Заголовок
- content: String - Содержание
- image_url: String - Путь к изображению
- created_at: DateTime - Дата создания
- updated_at: DateTime - Дата обновления
- author_id: Integer (FK) - ID автора
- is_published: Boolean - Статус публикации
- category: String - Категория новости
- views_count: Integer - Количество просмотров

**Связи:**
- author: многие к одному с User - Автор новости

## 8. MembershipType (Типы абонементов)
Доступные типы абонементов.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор типа
- name: String (уникальный) - Название
- description: String - Описание
- duration_days: Integer - Длительность в днях
- visits_limit: Integer - Лимит посещений
- price: Decimal - Стоимость
- has_pool: Boolean - Доступ в бассейн
- has_sauna: Boolean - Доступ в сауну
- has_group_training: Boolean - Доступ к групповым занятиям
- is_active: Boolean - Активность типа абонемента
- created_at: DateTime - Дата создания
- updated_at: DateTime - Дата обновления

## 9. Notification (Уведомления)
Система уведомлений пользователей.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор уведомления
- user_id: Integer (FK) - ID получателя
- type: String - Тип уведомления
- title: String - Заголовок
- message: String - Текст сообщения
- created_at: DateTime - Дата создания
- read: Boolean - Статус прочтения
- priority: Integer - Приоритет
- expiration_date: DateTime - Срок актуальности

**Связи:**
- user: многие к одному с User - Получатель уведомления

## 10. TrainingParticipant (Участники тренировок)
Связь между тренировками и участниками.

**Атрибуты:**
- id: Integer (PK) - Уникальный идентификатор записи
- schedule_id: Integer (FK) - ID тренировки
- user_id: Integer (FK) - ID участника
- status: String - Статус участия (confirmed/cancelled/waiting)
- registration_date: DateTime - Дата регистрации
- cancellation_reason: String - Причина отмены
- attendance: Boolean - Присутствие на тренировке

**Связи:**
- schedule: многие к одному с TrainerSchedule - Тренировка
- user: многие к одному с User - Участник 