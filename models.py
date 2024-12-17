from sqlalchemy import Column, Integer, String, Date, ForeignKey
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

# Создание таблиц
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)