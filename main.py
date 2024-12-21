from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from routers import membership, auth, users, schedule, trainer, occupancy, reviews
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:3000",  # Replace with the URL of your frontend
    "http://127.0.0.1:3000", #  or with other URL
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы для доступа к фотографиям
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(membership.router)
app.include_router(users.router)
app.include_router(schedule.router)
app.include_router(trainer.router)
app.include_router(occupancy.router)
app.include_router(reviews.router)



