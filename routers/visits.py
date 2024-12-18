from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List
from database import get_db
from models import GymVisit, User, GymMembership
from schemas import GymVisitCreate, GymVisit as GymVisitSchema, GymVisitUpdate, GymOccupancyStats
from dependencies import trainer_or_admin
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/api/visits", tags=["visits"])

@router.post("/check-in", response_model=GymVisitSchema, dependencies=[Depends(trainer_or_admin)])
def check_in(visit: GymVisitCreate, db: Session = Depends(get_db)):
    # Проверяем, есть ли активное посещение
    active_visit = db.query(GymVisit).filter(
        GymVisit.user_id == visit.user_id,
        GymVisit.check_out == None
    ).first()
    
    if active_visit:
        raise HTTPException(status_code=400, detail="У пользователя уже есть активное посещение")
    
    # Проверяем действительность абонемента
    membership = db.query(GymMembership).filter(
        GymMembership.id == visit.membership_id,
        GymMembership.user_id == visit.user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Абонемент не найден")
    
    if membership.visits_left <= 0:
        raise HTTPException(status_code=400, detail="Закончились посещения по абонементу")
    
    # Создаем запись о посещении
    db_visit = GymVisit(**visit.dict())
    db.add(db_visit)
    
    # Уменьшаем количество оставшихся посещений
    membership.visits_left -= 1
    
    db.commit()
    db.refresh(db_visit)
    return db_visit

@router.post("/check-out/{visit_id}", response_model=GymVisitSchema, dependencies=[Depends(trainer_or_admin)])
def check_out(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(GymVisit).filter(GymVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Посещение не найдено")
    
    if visit.check_out:
        raise HTTPException(status_code=400, detail="Посещение уже завершено")
    
    visit.check_out = datetime.now()
    db.commit()
    db.refresh(visit)
    return visit

@router.get("/current", response_model=GymOccupancyStats)
def get_current_occupancy(db: Session = Depends(get_db)):
    # Подсчитываем количество людей в зале (с check_in, но без check_out)
    current_visitors = db.query(GymVisit).filter(
        GymVisit.check_out == None
    ).count()
    
    return GymOccupancyStats(
        current_visitors=current_visitors,
        timestamp=datetime.now()
    )

@router.get("/stats/daily", response_model=List[GymOccupancyStats])
def get_daily_stats(target_date: date = None, db: Session = Depends(get_db)):
    if not target_date:
        target_date = date.today()
    
    # Получаем статистику по часам
    stats = []
    for hour in range(24):
        start_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
        end_time = start_time + timedelta(hours=1)
        
        # Подсчитываем количество людей в зале за каждый час
        visitors_count = db.query(GymVisit).filter(
            and_(
                GymVisit.check_in < end_time,
                or_(
                    GymVisit.check_out == None,
                    GymVisit.check_out > start_time
                )
            )
        ).count()
        
        stats.append(GymOccupancyStats(
            current_visitors=visitors_count,
            timestamp=start_time
        ))
    
    return stats

@router.get("/user/{user_id}", response_model=List[GymVisitSchema])
def get_user_visits(
    user_id: int,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    query = db.query(GymVisit).filter(GymVisit.user_id == user_id)
    
    if start_date:
        query = query.filter(GymVisit.check_in >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(GymVisit.check_in <= datetime.combine(end_date, datetime.max.time()))
    
    return query.order_by(GymVisit.check_in.desc()).all() 