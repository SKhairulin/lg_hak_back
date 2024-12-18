from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import TrainerInfo, User, UserRole
from schemas import (
    TrainerInfoCreate,
    TrainerInfo as TrainerInfoSchema,
    TrainerWithFullInfo,
    TrainerInfoBase
)
from dependencies import trainer_or_admin
import shutil
import os
from uuid import uuid4

router = APIRouter(prefix="/api/trainers", tags=["trainers"])

UPLOAD_DIR = "uploads/trainers"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/info", response_model=TrainerInfoSchema, dependencies=[Depends(trainer_or_admin)])
def create_trainer_info(trainer_info: TrainerInfoCreate, db: Session = Depends(get_db)):
    # Проверяем, что пользователь является тренером
    trainer = db.query(User).filter(
        User.id == trainer_info.trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")
    
    # Проверяем, нет ли уже информации о тренере
    existing_info = db.query(TrainerInfo).filter(
        TrainerInfo.trainer_id == trainer_info.trainer_id
    ).first()
    if existing_info:
        raise HTTPException(status_code=400, detail="Информация о тренере уже существует")
    
    db_trainer_info = TrainerInfo(**trainer_info.dict())
    db.add(db_trainer_info)
    db.commit()
    db.refresh(db_trainer_info)
    return db_trainer_info

@router.get("/info/{trainer_id}", response_model=TrainerWithFullInfo)
def get_trainer_info(trainer_id: int, db: Session = Depends(get_db)):
    trainer = db.query(User).filter(
        User.id == trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")
    return trainer

@router.get("/all", response_model=List[TrainerWithFullInfo])
def get_all_trainers_info(db: Session = Depends(get_db)):
    trainers = db.query(User).filter(User.role == UserRole.TRAINER).all()
    return trainers

@router.put("/info/{trainer_id}", response_model=TrainerInfoSchema, dependencies=[Depends(trainer_or_admin)])
def update_trainer_info(
    trainer_id: int,
    trainer_info: TrainerInfoBase,
    db: Session = Depends(get_db)
):
    db_trainer_info = db.query(TrainerInfo).filter(TrainerInfo.trainer_id == trainer_id).first()
    if not db_trainer_info:
        raise HTTPException(status_code=404, detail="Информация о тренере не найдена")
    
    for key, value in trainer_info.dict().items():
        setattr(db_trainer_info, key, value)
    
    db.commit()
    db.refresh(db_trainer_info)
    return db_trainer_info

@router.post("/info/{trainer_id}/photo", dependencies=[Depends(trainer_or_admin)])
async def upload_trainer_photo(
    trainer_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    trainer_info = db.query(TrainerInfo).filter(TrainerInfo.trainer_id == trainer_id).first()
    if not trainer_info:
        raise HTTPException(status_code=404, detail="Информация о тренере не найдена")
    
    # Генерируем уникальное имя файла
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Обновляем путь к фото в БД
    trainer_info.photo_url = f"/uploads/trainers/{file_name}"
    db.commit()
    
    return {"photo_url": trainer_info.photo_url} 