from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserRole(str, Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    CLIENT = "client"

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CLIENT

class User(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True

class GymMembershipBase(BaseModel):
    membership_type: str
    start_date: date
    end_date: date
    visits_left: int
    status: str

class GymMembershipCreate(GymMembershipBase):
    user_id: int

class GymMembership(GymMembershipBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

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

class TrainerWithFullInfo(User):
    trainer_info: Optional[TrainerInfo] = None
    schedules: List[TrainerSchedule] = []

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