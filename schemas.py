from pydantic import BaseModel, Field, EmailStr, validator
from datetime import date, time, datetime
from typing import Optional, List, Dict
from enum import Enum

# Схемы для аутентификации
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Базовые схемы
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r'^\+7\d{10}$')

class UserCreate(UserBase):
    password: str = Field(min_length=8, regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$')
    role: str = Field(default="client", pattern='^(client|trainer|admin|manager)$')

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
class TrainingType(str, Enum):
    PERSONAL = "personal"
    GROUP = "group"

class TrainerScheduleBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool = True
    training_type: str = Field(pattern='^(personal|group)$')
    max_participants: Optional[int] = Field(None, gt=0, le=50)
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('date')
    def date_not_in_past(cls, v):
        if v < date.today():
            raise ValueError('Дата не может быть в прошлом')
        return v
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('Время окончания должно быть позже времени начала')
        return v

class TrainerScheduleCreate(TrainerScheduleBase):
    trainer_id: int

class TrainingParticipantBase(BaseModel):
    schedule_id: int

class TrainingParticipant(TrainingParticipantBase):
    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True

class TrainerSchedule(TrainerScheduleBase):
    id: int
    trainer_id: int
    participants: List[TrainingParticipant] = []

    class Config:
        from_attributes = True

# Схемы для информации о тренере
class TrainerInfoBase(BaseModel):
    specialization: str = Field(min_length=3, max_length=100)
    experience_years: int = Field(ge=0, le=50)
    education: str = Field(min_length=10, max_length=500)
    achievements: Optional[str] = Field(None, max_length=1000)
    description: str = Field(min_length=50, max_length=2000)
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
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=10, max_length=1000)
    
    @validator('comment')
    def comment_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Комментарий не может быть пустым')
        return v

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

class NewsBase(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    content: str = Field(min_length=10, max_length=5000)
    image_url: Optional[str] = Field(None, pattern=r'^https?://.*\.(jpg|jpeg|png|gif)$')
    is_published: bool = True

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    author_id: int

    class Config:
        from_attributes = True

class NewsList(BaseModel):
    total: int
    items: List[News]

class MembershipTypeBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    duration_days: int = Field(gt=0, le=365)
    visits_limit: int = Field(gt=0, le=1000)
    has_pool: bool
    has_sauna: bool
    is_active: bool = True

class MembershipTypeCreate(MembershipTypeBase):
    pass

class MembershipType(MembershipTypeBase):
    id: int

    class Config:
        from_attributes = True

class PriceListBase(BaseModel):
    name: str
    description: str
    price: int = Field(gt=0, description="Цена должна быть больше 0")
    duration_days: int = Field(gt=0, description="Длительность должна быть больше 0")
    visits_limit: int = Field(gt=0, description="Количество посещений должно быть больше 0")

class PriceListCreate(PriceListBase):
    pass

class PriceList(PriceListBase):
    id: int
    membership_type: MembershipType

    class Config:
        from_attributes = True

class MembershipTypeWithPrice(MembershipType):
    price_list: List[PriceList] = []

class PaymentCreate(BaseModel):
    price_id: int
    payment_method: str

class Payment(BaseModel):
    id: int
    user_id: int
    price_id: int
    amount: int
    status: str
    payment_method: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    type: str = Field(pattern='^(training_reminder|membership_expiring|training_cancelled|payment_success)$')
    title: str = Field(min_length=3, max_length=100)
    message: str = Field(min_length=10, max_length=500)

class NotificationCreate(NotificationBase):
    user_id: int

class Notification(NotificationBase):
    id: int
    created_at: datetime
    read: bool

    class Config:
        from_attributes = True