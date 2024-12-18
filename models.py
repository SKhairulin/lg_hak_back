from sqlalchemy import Column, Integer, String, Date, ForeignKey, Time, Boolean, func, DateTime
from sqlalchemy.orm import relationship
from database import Base, engine
from enum import Enum as PyEnum

class UserRole(str, PyEnum):
    ADMIN = "admin"
    TRAINER = "trainer"
    CLIENT = "client"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.CLIENT)
    
    membership = relationship("GymMembership", back_populates="user")
    schedules = relationship("TrainerSchedule", back_populates="trainer")
    trainer_info = relationship("TrainerInfo", back_populates="trainer", uselist=False)
    visits = relationship("GymVisit", back_populates="user")

class GymMembership(Base):
    __tablename__ = "gym_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    membership_type = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    visits_left = Column(Integer)
    status = Column(String)
    
    user = relationship("User", back_populates="membership")
    visits = relationship("GymVisit", back_populates="membership")

class TrainerSchedule(Base):
    __tablename__ = "trainer_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True)
    start_time = Column(Time)
    end_time = Column(Time)
    is_available = Column(Boolean, default=True)
    
    trainer = relationship("User", back_populates="schedules")

class TrainerInfo(Base):
    __tablename__ = "trainer_info"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), unique=True)
    specialization = Column(String)
    experience_years = Column(Integer)
    education = Column(String)
    achievements = Column(String)
    description = Column(String)
    photo_url = Column(String, nullable=True)
    
    trainer = relationship("User", back_populates="trainer_info")

class GymVisit(Base):
    __tablename__ = "gym_visits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    check_in = Column(DateTime, default=func.now())  # Время входа
    check_out = Column(DateTime, nullable=True)      # Время выхода
    membership_id = Column(Integer, ForeignKey("gym_memberships.id"))
    
    user = relationship("User", back_populates="visits")
    membership = relationship("GymMembership", back_populates="visits")

# Создание таблиц
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)