from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import PriceList, Payment, User, GymMembership, MembershipType
from schemas import PriceListCreate, PriceList as PriceListSchema, PaymentCreate, Payment as PaymentSchema, MembershipTypeCreate, MembershipTypeSchema, MembershipTypeWithPrice
from dependencies import manager_or_admin, get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Управление прайс-листом (только для менеджеров и админов)
@router.post("/prices", response_model=PriceListSchema, dependencies=[Depends(manager_or_admin)])
def create_price(price: PriceListCreate, db: Session = Depends(get_db)):
    db_price = PriceList(**price.dict())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

@router.get("/prices", response_model=List[PriceListSchema])
def get_prices(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(PriceList)
    if active_only:
        query = query.filter(PriceList.is_active == True)
    return query.all()

@router.put("/prices/{price_id}", response_model=PriceListSchema, dependencies=[Depends(manager_or_admin)])
def update_price(
    price_id: int,
    price_update: PriceListCreate,
    db: Session = Depends(get_db)
):
    db_price = db.query(PriceList).filter(PriceList.id == price_id).first()
    if not db_price:
        raise HTTPException(status_code=404, detail="Тариф не найден")
    
    for key, value in price_update.dict().items():
        setattr(db_price, key, value)
    
    db.commit()
    db.refresh(db_price)
    return db_price

# Оплата и создание абонемента
@router.post("/create", response_model=PaymentSchema, dependencies=[Depends(get_current_user)])
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получаем информацию о тарифе и типе абонемента
    price = db.query(PriceList).join(MembershipType).filter(
        PriceList.id == payment.price_id,
        PriceList.is_active == True,
        MembershipType.is_active == True
    ).first()
    
    if not price:
        raise HTTPException(status_code=404, detail="Тариф не найден или неактивен")
    
    # Создаем запись об оплате
    db_payment = Payment(
        user_id=current_user.id,
        price_id=payment.price_id,
        amount=price.price,
        status="pending",
        payment_method=payment.payment_method
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # В реальном приложении здесь была бы интеграция с платежной системой
    
    return db_payment

@router.post("/{payment_id}/complete", response_model=PaymentSchema)
def complete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    
    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Платеж уже обработан")
    
    # Получаем информацию о тарифе и типе абонемента
    price = db.query(PriceList).join(MembershipType).filter(
        PriceList.id == payment.price_id
    ).first()
    
    membership_type = price.membership_type
    
    # Создаем абонемент на основе типа
    membership = GymMembership(
        user_id=payment.user_id,
        membership_type=membership_type.name,
        start_date=datetime.now().date(),
        end_date=(datetime.now() + timedelta(days=membership_type.duration_days)).date(),
        visits_left=membership_type.visits_limit,
        has_pool=membership_type.has_pool,
        has_sauna=membership_type.has_sauna,
        status="active"
    )
    
    # Обновляем статус платежа
    payment.status = "completed"
    payment.completed_at = datetime.now()
    
    db.add(membership)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.get("/history", response_model=List[PaymentSchema], dependencies=[Depends(get_current_user)])
def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Payment).filter(Payment.user_id == current_user.id).all() 

# Добавим роуты для управления типами абонементов
@router.post("/membership-types", response_model=MembershipTypeSchema, dependencies=[Depends(manager_or_admin)])
def create_membership_type(
    membership_type: MembershipTypeCreate,
    db: Session = Depends(get_db)
):
    db_type = MembershipType(**membership_type.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type

@router.get("/membership-types", response_model=List[MembershipTypeWithPrice])
def get_membership_types(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(MembershipType)
    if active_only:
        query = query.filter(MembershipType.is_active == True)
    return query.all() 