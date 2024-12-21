from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Notification, TrainerSchedule, GymMembership, User
from schemas import NotificationCreate

conf = ConnectionConfig(
    MAIL_USERNAME="your_email@gmail.com",
    MAIL_PASSWORD="your_password",
    MAIL_FROM="your_email@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)

async def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

async def send_email_notification(user_email: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[user_email],
        body=body,
        subtype="html"
    )
    await fastmail.send_message(message)

async def send_training_reminder():
    """Отправка напоминаний о пре��стоящих тренировках"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    trainings = db.query(TrainerSchedule).filter(
        TrainerSchedule.date == tomorrow
    ).all()
    
    for training in trainings:
        for participant in training.participants:
            if participant.status == "confirmed":
                notification = NotificationCreate(
                    user_id=participant.user_id,
                    type="training_reminder",
                    title="Напоминание о тренировке",
                    message=f"Завтра в {training.start_time} у вас тренировка"
                )
                await create_notification(db, notification)
                await send_email_notification(
                    participant.user.email,
                    "Напоминание о тренировке",
                    f"Здравствуйте! Напоминаем, что завтра в {training.start_time} у вас запланирована тренировка."
                )

async def check_expiring_memberships():
    """Проверка истекающих абонементов"""
    week_later = datetime.now().date() + timedelta(days=7)
    
    expiring = db.query(GymMembership).filter(
        GymMembership.end_date == week_later,
        GymMembership.status == "active"
    ).all()
    
    for membership in expiring:
        notification = NotificationCreate(
            user_id=membership.user_id,
            type="membership_expiring",
            title="Абонемент скоро истекает",
            message=f"Ваш абонемент истекает {membership.end_date}. Не забудьте продлить!"
        )
        await create_notification(db, notification)
        await send_email_notification(
            membership.user.email,
            "Абонемент скоро истекает",
            f"Здравствуйте! Ваш абонемент истекает {membership.end_date}. Пожалуйста, продлите его, чтобы продолжить посещать тренировки."
        )

async def notify_training_cancelled(training_id: int):
    """Уведомление об отмене тренировки"""
    training = db.query(TrainerSchedule).filter(TrainerSchedule.id == training_id).first()
    
    for participant in training.participants:
        notification = NotificationCreate(
            user_id=participant.user_id,
            type="training_cancelled",
            title="Тренировка отменена",
            message=f"Тренировка {training.start_time} была отменена"
        )
        await create_notification(db, notification)
        await send_email_notification(
            participant.user.email,
            "Тренировка отменена",
            f"К сожалению, ваша тренировка {training.start_time} была отменена. Пожалуйста, выберите другое время."
        ) 