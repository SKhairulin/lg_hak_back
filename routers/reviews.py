from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import TrainerReview, User, UserRole
from schemas import (
    TrainerReviewCreate,
    TrainerReview as TrainerReviewSchema,
    TrainerReviewStats
)
from dependencies import trainer_or_admin, all_roles, get_current_user, manager_or_admin
from datetime import datetime

router = APIRouter(prefix="/api/reviews", tags=["reviews"])

@router.post("/", response_model=TrainerReviewSchema, dependencies=[Depends(get_current_user)])
def create_review(
    review: TrainerReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем, что оценка в допустимом диапазоне
    if not 1 <= review.rating <= 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 1 до 5")
    
    # Проверяем, что пользователь оставляет отзыв тренеру
    trainer = db.query(User).filter(
        User.id == review.trainer_id,
        User.role == UserRole.TRAINER
    ).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")
    
    # Проверяем, не оставлял ли пользователь уже отзыв этому тренеру
    existing_review = db.query(TrainerReview).filter(
        TrainerReview.trainer_id == review.trainer_id,
        TrainerReview.user_id == current_user.id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Вы уже оставляли отзыв этому тренеру")
    
    db_review = TrainerReview(
        **review.dict(),
        user_id=current_user.id,
        is_approved=False  # Новые отзывы требуют модерации
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/trainer/{trainer_id}", response_model=List[TrainerReviewSchema])
def get_trainer_reviews(
    trainer_id: int,
    approved_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(TrainerReview).filter(TrainerReview.trainer_id == trainer_id)
    if approved_only:
        query = query.filter(TrainerReview.is_approved == True)
    return query.order_by(TrainerReview.created_at.desc()).all()

@router.get("/trainer/{trainer_id}/stats", response_model=TrainerReviewStats)
def get_trainer_review_stats(trainer_id: int, db: Session = Depends(get_db)):
    # Получаем только одобренные отзывы
    reviews = db.query(TrainerReview).filter(
        TrainerReview.trainer_id == trainer_id,
        TrainerReview.is_approved == True
    ).all()
    
    if not reviews:
        return TrainerReviewStats(
            average_rating=0.0,
            total_reviews=0,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        )
    
    # Подсчитываем статистику
    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews
    
    # Распределение оценок
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        distribution[review.rating] += 1
    
    return TrainerReviewStats(
        average_rating=round(average_rating, 2),
        total_reviews=total_reviews,
        rating_distribution=distribution
    )

@router.put("/{review_id}/approve", dependencies=[Depends(manager_or_admin)])
def approve_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(TrainerReview).filter(TrainerReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    review.is_approved = True
    db.commit()
    return {"message": "Отзыв одобрен"}

@router.delete("/{review_id}", dependencies=[Depends(manager_or_admin)])
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(TrainerReview).filter(TrainerReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    db.delete(review)
    db.commit()
    return {"message": "Отзыв удален"} 