from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, TrainerSchedule, UserRole, TrainingType, TrainingParticipant, GymMembership
from schemas import TrainerScheduleCreate, TrainerSchedule as TrainerScheduleSchema, TrainerScheduleBase, TrainingParticipant as ParticipantSchema
from dependencies import trainer_or_admin, get_current_user
from datetime import date, time, datetime, timedelta

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.post("/", response_model=TrainerSchedule, dependencies=[Depends(trainer_or_admin)])
def create_schedule(
    schedule: TrainerScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(trainer_or_admin)
):
    # Проверяем, что пользователь является тренером или админом
    if current_user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Только тренер может создавать расписание")
    
    # Проверяем корректность данных для групповой тренировки
    if schedule.training_type == TrainingType.GROUP:
        if not schedule.max_participants:
            raise HTTPException(
                status_code=400, 
                detail="Для групповой тренировки необходимо указать максимальное количество участников"
            )
        if not schedule.name:
            raise HTTPException(
                status_code=400,
                detail="Для групповой тренировки необходимо указать название"
            )
    
    # Проверяем, нет ли пересечений в расписании
    existing_schedule = db.query(TrainerSchedule).filter(
        TrainerSchedule.trainer_id == schedule.trainer_id,
        TrainerSchedule.date == schedule.date,
        TrainerSchedule.start_time < schedule.end_time,
        TrainerSchedule.end_time > schedule.start_time
    ).first()
    
    if existing_schedule:
        raise HTTPException(status_code=400, detail="В это время уже есть запись в расписании")
    
    db_schedule = TrainerSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

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

# Добавим новый эндпоинт для получения расписания за период
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