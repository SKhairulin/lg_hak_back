from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, UserRole
from schemas import UserCreate, User as UserSchema
from dependencies import admin_only
from utils import get_password_hash

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(admin_only)])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/trainers", response_model=List[UserSchema])
def get_trainers(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == UserRole.TRAINER).all()

@router.put("/{user_id}/role", dependencies=[Depends(admin_only)])
def update_user_role(user_id: int, role: UserRole, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.role = role
    db.commit()
    return {"message": "Роль успешно обновлена"} 