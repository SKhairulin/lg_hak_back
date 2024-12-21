from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Notification, TrainerSchedule, GymMembership, User
import logging

logger = logging.getLogger(__name__)

async def create_notification(db: Session, notification_data: dict):
    """Создание уведомления в базе данных"""
    db_notification = Notification(**notification_data)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

async def send_email_notification(user_email: str, subject: str, body: str):
    """Заглушка для отправки email"""
    logger.info(f"[EMAIL STUB] To: {user_email}, Subject: {subject}, Body: {body}")
    # В реальном приложении здесь будет отправка email
    return True

async def send_training_reminder():
    """Отправка напоминаний о предстоящих тренировках"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    trainings = db.query(TrainerSchedule).filter(
        TrainerSchedule.date == tomorrow
    ).all()
    
    for training in trainings:
        for participant in training.participants:
            if participant.status == "confirmed":
                # Создаем уведомление в базе
                notification = {
                    "user_id": participant.user_id,
                    "type": "training_reminder",
                    "title": "Напоминание о тренировке",
                    "message": f"Завтра в {training.start_time} у вас тренировка"
                }
                await create_notification(db, notification)
                
                # Логируем "отправку" email
                logger.info(
                    f"[TRAINING REMINDER] Would send email to {participant.user.email} "
                    f"about training at {training.start_time}"
                )

async def check_expiring_memberships():
    """Проверка истекающих абонементов"""
    week_later = datetime.now().date() + timedelta(days=7)
    
    expiring = db.query(GymMembership).filter(
        GymMembership.end_date == week_later,
        GymMembership.status == "active"
    ).all()
    
    for membership in expiring:
        # Создаем уведомление в базе
        notification = {
            "user_id": membership.user_id,
            "type": "membership_expiring",
            "title": "Абонемент скоро истекает",
            "message": f"Ваш абонемент истекает {membership.end_date}. Не забудьте продлить!"
        }
        await create_notification(db, notification)
        
        # Логируем "отправку" email
        logger.info(
            f"[MEMBERSHIP EXPIRING] Would send email to {membership.user.email} "
            f"about membership expiring on {membership.end_date}"
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