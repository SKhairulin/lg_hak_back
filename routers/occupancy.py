from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
from models import GymVisit, User
from schemas import GymOccupancyStats
from dependencies import trainer_or_admin
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/api/occupancy", tags=["occupancy"])

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

@router.get("/daily", response_model=List[GymOccupancyStats])
def get_daily_stats(target_date: date = None, db: Session = Depends(get_db)):
    if not target_date:
        target_date = date.today()
    
    stats = []
    for hour in range(24):
        start_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
        end_time = start_time + timedelta(hours=1)
        
        # Подсчитываем количество людей в зале за каждый час
        visitors_count = db.query(GymVisit).filter(
            GymVisit.check_in < end_time,
            (GymVisit.check_out == None) | (GymVisit.check_out > start_time)
        ).count()
        
        stats.append(GymOccupancyStats(
            current_visitors=visitors_count,
            timestamp=start_time
        ))
    
    return stats

@router.get("/weekly", response_model=List[List[GymOccupancyStats]])
def get_weekly_stats(start_date: date = None, db: Session = Depends(get_db)):
    if not start_date:
        # Если дата не указана, берем начало текущей недели
        start_date = date.today() - timedelta(days=date.today().weekday())
    
    end_date = start_date + timedelta(days=6)
    
    weekly_stats = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_stats = []
        for hour in range(24):
            start_time = datetime.combine(current_date, datetime.min.time().replace(hour=hour))
            end_time = start_time + timedelta(hours=1)
            
            visitors_count = db.query(GymVisit).filter(
                GymVisit.check_in < end_time,
                (GymVisit.check_out == None) | (GymVisit.check_out > start_time)
            ).count()
            
            daily_stats.append(GymOccupancyStats(
                current_visitors=visitors_count,
                timestamp=start_time
            ))
        
        weekly_stats.append(daily_stats)
        current_date += timedelta(days=1)
    
    return weekly_stats

@router.get("/peak-hours", response_model=List[GymOccupancyStats])
def get_peak_hours(days: int = 30, db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Агрегируем данные по часам
    peak_hours = []
    for hour in range(24):
        avg_visitors = db.query(func.count(GymVisit.id)).filter(
            GymVisit.check_in >= start_date,
            GymVisit.check_in <= end_date,
            func.extract('hour', GymVisit.check_in) == hour
        ).scalar() or 0
        
        peak_hours.append(GymOccupancyStats(
            current_visitors=avg_visitors,
            timestamp=datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        ))
    
    return sorted(peak_hours, key=lambda x: x.current_visitors, reverse=True) 