from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import GymMembership, User, Payment, MembershipType
from schemas import MembershipCreate
from .notifications import create_notification, send_email_notification

class MembershipService:
    def __init__(self, db: Session):
        self.db = db

    async def create_membership(self, user_id: int, membership_type_id: int, payment_id: int) -> GymMembership:
        """Создание нового абонемента после оплаты"""
        membership_type = self.db.query(MembershipType).filter_by(id=membership_type_id).first()
        if not membership_type:
            raise HTTPException(status_code=404, detail="Тип абонемента не найден")

        # Проверяем оплату
        payment = self.db.query(Payment).filter_by(id=payment_id, status="completed").first()
        if not payment:
            raise HTTPException(status_code=400, detail="Оплата не подтверждена")

        # Проверяем активные абонементы
        active_membership = self.db.query(GymMembership).filter(
            GymMembership.user_id == user_id,
            GymMembership.status == "active",
            GymMembership.end_date >= datetime.now().date()
        ).first()

        start_date = datetime.now().date()
        if active_membership:
            # Если есть активный абонемент, новый начнется после окончания текущего
            start_date = active_membership.end_date + timedelta(days=1)

        new_membership = GymMembership(
            user_id=user_id,
            membership_type=membership_type.name,
            start_date=start_date,
            end_date=start_date + timedelta(days=membership_type.duration_days),
            visits_left=membership_type.visits_limit,
            has_pool=membership_type.has_pool,
            has_sauna=membership_type.has_sauna,
            status="active",
            payment_id=payment_id
        )

        self.db.add(new_membership)
        self.db.commit()
        self.db.refresh(new_membership)

        # Отправляем уведомление
        await create_notification(self.db, {
            "user_id": user_id,
            "type": "membership_created",
            "title": "Абонемент активирован",
            "message": f"Ваш новый абонемент активирован и действует до {new_membership.end_date}"
        })

        return new_membership

    async def extend_membership(self, membership_id: int, payment_id: int) -> GymMembership:
        """Продление существующего абонемента"""
        membership = self.db.query(GymMembership).filter_by(id=membership_id).first()
        if not membership:
            raise HTTPException(status_code=404, detail="Абонемент не найден")

        payment = self.db.query(Payment).filter_by(id=payment_id, status="completed").first()
        if not payment:
            raise HTTPException(status_code=400, detail="Оплата не подтверждена")

        membership_type = self.db.query(MembershipType).filter_by(name=membership.membership_type).first()
        
        # Продлеваем абонемент
        membership.end_date = membership.end_date + timedelta(days=membership_type.duration_days)
        membership.visits_left += membership_type.visits_limit
        membership.status = "active"

        self.db.commit()
        self.db.refresh(membership)

        await create_notification(self.db, {
            "user_id": membership.user_id,
            "type": "membership_extended",
            "title": "Абонемент продлен",
            "message": f"Ваш абонемент продлен до {membership.end_date}"
        })

        return membership

    async def freeze_membership(self, membership_id: int, days: int, reason: str) -> GymMembership:
        """Заморозка абонемента"""
        if days > 30:  # Максимальный срок заморозки
            raise HTTPException(status_code=400, detail="Максимальный срок заморозки - 30 дней")

        membership = self.db.query(GymMembership).filter_by(id=membership_id, status="active").first()
        if not membership:
            raise HTTPException(status_code=404, detail="Активный абонемент не найден")

        membership.status = "frozen"
        membership.end_date = membership.end_date + timedelta(days=days)
        membership.freeze_reason = reason
        membership.freeze_start = datetime.now().date()
        membership.freeze_end = datetime.now().date() + timedelta(days=days)

        self.db.commit()
        self.db.refresh(membership)

        await create_notification(self.db, {
            "user_id": membership.user_id,
            "type": "membership_frozen",
            "title": "Абонемент заморожен",
            "message": f"Ваш абонемент заморожен до {membership.freeze_end}"
        })

        return membership

    async def unfreeze_membership(self, membership_id: int) -> GymMembership:
        """Разморозка абонемента"""
        membership = self.db.query(GymMembership).filter_by(id=membership_id, status="frozen").first()
        if not membership:
            raise HTTPException(status_code=404, detail="Замороженный абонемент не найден")

        membership.status = "active"
        membership.freeze_end = datetime.now().date()

        self.db.commit()
        self.db.refresh(membership)

        await create_notification(self.db, {
            "user_id": membership.user_id,
            "type": "membership_unfrozen",
            "title": "Абонемент разморожен",
            "message": "Ваш абонемент снова активен"
        })

        return membership

    async def check_expiring_memberships(self):
        """Проверка истекающих абонементов"""
        week_later = datetime.now().date() + timedelta(days=7)
        
        expiring = self.db.query(GymMembership).filter(
            GymMembership.end_date == week_later,
            GymMembership.status == "active"
        ).all()

        for membership in expiring:
            await create_notification(self.db, {
                "user_id": membership.user_id,
                "type": "membership_expiring",
                "title": "Абонемент скоро истекает",
                "message": f"Ваш абонемент истекает {membership.end_date}. Не забудьте продлить!"
            })

    def get_active_membership(self, user_id: int) -> GymMembership:
        """Получение активного абонемента пользователя"""
        return self.db.query(GymMembership).filter(
            GymMembership.user_id == user_id,
            GymMembership.status == "active",
            GymMembership.end_date >= datetime.now().date()
        ).first() 