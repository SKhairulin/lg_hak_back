from pydantic import BaseModel
from typing import Optional
from datetime import date
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