from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, TrainerSchedule, UserRole
from schemas import TrainerScheduleCreate, TrainerSchedule as TrainerScheduleSchema, TrainerScheduleBase
from dependencies import trainer_or_admin
from datetime import date, time

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.post("/", response_model=TrainerScheduleSchema, dependencies=[Depends(trainer_or_admin)])
def create_schedule(schedule: TrainerScheduleCreate, db: Session = Depends(get_db)):
    # Проверяем, что пользователь является тренером
    trainer = db.query(User).filter(
        User.id == schedule.trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")
    
    # Проверяем, нет ли пересечений в расписании на эту дату
    existing_schedule = db.query(TrainerSchedule).filter(
        TrainerSchedule.trainer_id == schedule.trainer_id,
        TrainerSchedule.date == schedule.date
    ).first()
    if existing_schedule:
        raise HTTPException(status_code=400, detail="На эту дату уже есть расписание")
    
    db_schedule = TrainerSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

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