from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional, List, Dict

# Схемы для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Базовые схемы
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "client"

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

# Схемы для абонементов
class GymMembershipBase(BaseModel):
    membership_type: str
    start_date: date
    end_date: date
    visits_left: int
    status: str = "active"

class GymMembershipCreate(GymMembershipBase):
    user_id: int

class GymMembership(GymMembershipBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Схемы для посещений
class GymVisitBase(BaseModel):
    user_id: int
    membership_id: int

class GymVisitCreate(GymVisitBase):
    pass

class GymVisitUpdate(BaseModel):
    check_out: datetime

class GymVisit(GymVisitBase):
    id: int
    check_in: datetime
    check_out: Optional[datetime] = None

    class Config:
        from_attributes = True

class GymOccupancyStats(BaseModel):
    current_visitors: int
    max_capacity: int = 50
    timestamp: datetime

    class Config:
        from_attributes = True

# Схемы для расписания
class TrainerScheduleBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool = True

class TrainerScheduleCreate(TrainerScheduleBase):
    trainer_id: int

class TrainerSchedule(TrainerScheduleBase):
    id: int
    trainer_id: int

    class Config:
        from_attributes = True

# Схемы для информации о тренере
class TrainerInfoBase(BaseModel):
    specialization: str
    experience_years: int
    education: str
    achievements: str
    description: str
    photo_url: Optional[str] = None

class TrainerInfoCreate(TrainerInfoBase):
    trainer_id: int

class TrainerInfo(TrainerInfoBase):
    id: int
    trainer_id: int

    class Config:
        from_attributes = True

# Схемы для отзывов
class TrainerReviewBase(BaseModel):
    rating: int
    comment: str

class TrainerReviewCreate(TrainerReviewBase):
    trainer_id: int

class TrainerReview(TrainerReviewBase):
    id: int
    trainer_id: int
    user_id: int
    created_at: datetime
    is_approved: bool
    
    class Config:
        from_attributes = True

class TrainerReviewStats(BaseModel):
    average_rating: float
    total_reviews: int
    rating_distribution: Dict[int, int]

    class Config:
        from_attributes = True

# Объединенная схема для тренера
class TrainerWithFullInfo(User):
    trainer_info: Optional[TrainerInfo] = None
    schedules: List[TrainerSchedule] = []
    reviews: List[TrainerReview] = []
    review_stats: Optional[TrainerReviewStats] = None