from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from database import get_db
from models import User, TrainerSchedule, UserRole, TrainingType, TrainingParticipant, GymMembership
from schemas import TrainerScheduleCreate, TrainerSchedule as TrainerScheduleSchema, TrainerScheduleBase, TrainingParticipant as ParticipantSchema, ScheduleCreate, Schedule
from dependencies import trainer_or_admin, get_current_user
from datetime import date, time, datetime, timedelta

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.post("/", response_model=None)
async def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(trainer_or_admin)
):
    db_schedule = TrainerSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/", response_model=None)
async def get_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    trainer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TrainerSchedule)
    
    if start_date:
        query = query.filter(TrainerSchedule.date >= start_date)
    if end_date:
        query = query.filter(TrainerSchedule.date <= end_date)
    if trainer_id:
        query = query.filter(TrainerSchedule.trainer_id == trainer_id)
    
    return query.all()

@router.post("/{schedule_id}/join", response_model=ParticipantSchema)
def join_training(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем существование тренировки
    schedule = db.query(TrainerSchedule).filter(TrainerSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    
    if not schedule.is_available:
        raise HTTPException(status_code=400, detail="Тренировка недоступна для записи")
    
    # Проверяем наличие активного абонемента
    active_membership = db.query(GymMembership).filter(
        GymMembership.user_id == current_user.id,
        GymMembership.status == "active",
        GymMembership.start_date <= datetime.now().date(),
        GymMembership.end_date >= datetime.now().date(),
        GymMembership.visits_left > 0
    ).first()
    
    if not active_membership:
        raise HTTPException(
            status_code=400, 
            detail="У вас нет активного абонемента или закончились доступные посещения"
        )
    
    # Проверяем, не записан ли уже пользователь
    existing_participant = db.query(TrainingParticipant).filter(
        TrainingParticipant.schedule_id == schedule_id,
        TrainingParticipant.user_id == current_user.id
    ).first()
    
    if existing_participant:
        if existing_participant.status == "confirmed":
            raise HTTPException(status_code=400, detail="Вы уже записаны на эту тренировку")
        elif existing_participant.status == "cancelled":
            # Если была отмена, обновляем статус
            existing_participant.status = "confirmed"
            db.commit()
            db.refresh(existing_participant)
            return existing_participant
    
    # Проверяем тип тренировки и доступность мест
    if schedule.training_type == TrainingType.GROUP:
        participants_count = db.query(TrainingParticipant).filter(
            TrainingParticipant.schedule_id == schedule_id,
            TrainingParticipant.status == "confirmed"
        ).count()
        
        if participants_count >= schedule.max_participants:
            raise HTTPException(status_code=400, detail="Группа уже заполнена")
    
    elif schedule.training_type == TrainingType.PERSONAL:
        existing_participant = db.query(TrainingParticipant).filter(
            TrainingParticipant.schedule_id == schedule_id,
            TrainingParticipant.status == "confirmed"
        ).first()
        
        if existing_participant:
            raise HTTPException(status_code=400, detail="На это время уже записан другой клиент")
    
    # Создаем запись на тренировку
    participant = TrainingParticipant(
        schedule_id=schedule_id,
        user_id=current_user.id,
        status="confirmed"
    )
    
    # Уменьшаем количество доступных посещений
    active_membership.visits_left -= 1
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    
    return participant

@router.delete("/{schedule_id}/cancel")
def cancel_training_participation(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Находим запись на тренировку
    participant = db.query(TrainingParticipant).filter(
        TrainingParticipant.schedule_id == schedule_id,
        TrainingParticipant.user_id == current_user.id,
        TrainingParticipant.status == "confirmed"
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Запись на тренировку не найдена")
    
    # Проверяем время до тренировки (например, отмена возможна не менее чем за 24 часа)
    schedule = db.query(TrainerSchedule).filter(TrainerSchedule.id == schedule_id).first()
    training_datetime = datetime.combine(schedule.date, schedule.start_time)
    
    if datetime.now() + timedelta(hours=24) > training_datetime:
        raise HTTPException(
            status_code=400, 
            detail="Отмена тренировки возможна не менее чем за 24 часа"
        )
    
    # Отменяем запись и возвращаем посещение в абонемент
    participant.status = "cancelled"
    
    active_membership = db.query(GymMembership).filter(
        GymMembership.user_id == current_user.id,
        GymMembership.status == "active",
        GymMembership.start_date <= datetime.now().date(),
        GymMembership.end_date >= datetime.now().date()
    ).first()
    
    if active_membership:
        active_membership.visits_left += 1
    
    db.commit()
    
    return {"message": "Запись на тренировку отменена"}

# Добавим новый ��ндпоинт для получения расписания за период
@router.get("/trainer/{trainer_id}/period")
def get_trainer_schedule_by_period(
    trainer_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    trainer = db.query(User).filter(
        User.id == trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")
    
    schedules = db.query(TrainerSchedule).filter(
        TrainerSchedule.trainer_id == trainer_id,
        TrainerSchedule.date >= start_date,
        TrainerSchedule.date <= end_date
    ).all()
    
    return {
        "trainer": trainer,
        "schedules": schedules
    } 

# Просмотр расписания доступен всем
@router.get("/trainer/{trainer_id}")
@router.get("/available")

# Управление расписанием только для тренеров и админов
@router.post("/", dependencies=[Depends(trainer_or_admin)])
@router.put("/{schedule_id}", dependencies=[Depends(trainer_or_admin)])
@router.delete("/{schedule_id}", dependencies=[Depends(trainer_or_admin)]) 

@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(trainer_or_admin)
):
    schedule = db.query(TrainerSchedule).filter(TrainerSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    
    db.delete(schedule)
    db.commit()
    return {"message": "Расписание удалено"} 