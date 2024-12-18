from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from routers import membership, auth, users, schedule, trainer
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Монтируем статические файлы для доступа к фотографиям
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(membership.router)
app.include_router(users.router)
app.include_router(schedule.router)
app.include_router(trainer.router)

