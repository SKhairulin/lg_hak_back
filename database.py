from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
#DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_db_operation(operation):
    try:
        return operation()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка базы данных: {str(e)}"
        )