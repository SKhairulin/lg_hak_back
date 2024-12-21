from sqlalchemy import Column, Integer, String, Date, ForeignKey, Time, Boolean, func, DateTime
from sqlalchemy.orm import relationship
from database import Base, engine
from enum import Enum as PyEnum
from datetime import datetime, timezone

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
    phone = Column(String, nullable=True)
    
    membership = relationship("GymMembership", back_populates="user")
    schedules = relationship("TrainerSchedule", back_populates="trainer")
    trainer_info = relationship("TrainerInfo", back_populates="trainer", uselist=False)
    visits = relationship("GymVisit", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    news = relationship("News", back_populates="author")
    payments = relationship("Payment", back_populates="user")

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

class TrainingType(str, PyEnum):
    PERSONAL = "personal"
    GROUP = "group"

class TrainerSchedule(Base):
    __tablename__ = "trainer_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    is_available = Column(Boolean, default=True)
    training_type = Column(String)  # personal/group
    max_participants = Column(Integer, nullable=True)  # NULL для персональных
    name = Column(String, nullable=True)  # Название для групповой тренировки
    description = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    trainer = relationship("User", back_populates="schedules")
    participants = relationship("TrainingParticipant", back_populates="schedule")

    def get_local_datetime(self):
        return datetime.combine(self.date, self.start_time).replace(tzinfo=timezone.utc)

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

class TrainerReview(Base):
    __tablename__ = "trainer_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    trainer_id = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # Оценка от 1 до 5
    comment = Column(String)
    created_at = Column(DateTime, default=func.now())
    is_approved = Column(Boolean, default=False)  # Модерация отзывов
    
    trainer = relationship("User", foreign_keys=[trainer_id], backref="received_reviews")
    user = relationship("User", foreign_keys=[user_id], backref="written_reviews")

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Boolean, default=True)
    
    author = relationship("User", back_populates="news")

class MembershipType(Base):
    __tablename__ = "membership_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Название типа абонемента
    description = Column(String)
    duration_days = Column(Integer)      # Длительность абонемента в днях
    visits_limit = Column(Integer)       # Количество посещений
    has_pool = Column(Boolean, default=False)
    has_sauna = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class PriceList(Base):
    __tablename__ = "price_list"
    
    id = Column(Integer, primary_key=True, index=True)
    membership_type_id = Column(Integer, ForeignKey("membership_types.id"))
    price = Column(Integer)
    is_active = Column(Boolean, default=True)
    
    membership_type = relationship("MembershipType")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    price_id = Column(Integer, ForeignKey("price_list.id"))
    amount = Column(Integer)
    status = Column(String)  # pending, completed, failed
    payment_method = Column(String)  # card, cash
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="payments")
    price = relationship("PriceList")

class TrainingParticipant(Base):
    __tablename__ = "training_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("trainer_schedules.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # confirmed, cancelled
    
    schedule = relationship("TrainerSchedule", back_populates="participants")
    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # training_reminder, membership_expiring, training_cancelled, etc
    title = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=func.now())
    read = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="notifications")

# Создание таблиц
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)