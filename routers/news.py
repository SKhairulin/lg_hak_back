from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import News, User, UserRole
from schemas import NewsCreate, News as NewsSchema, NewsList
from dependencies import manager_or_admin
import shutil
import os
from uuid import uuid4
from datetime import datetime

router = APIRouter(prefix="/api/news", tags=["news"])

UPLOAD_DIR = "uploads/news"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=NewsSchema, dependencies=[Depends(manager_or_admin)])
def create_news(
    news: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin)
):
    db_news = News(**news.dict(), author_id=current_user.id)
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.post("/upload-image", dependencies=[Depends(manager_or_admin)])
async def upload_news_image(
    file: UploadFile = File(...),
):
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"image_url": f"/uploads/news/{file_name}"}

@router.get("/", response_model=NewsList)
def get_news_list(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(News)
    
    if search:
        query = query.filter(News.title.ilike(f"%{search}%"))
    
    total = query.count()
    news = query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()
    
    return NewsList(total=total, items=news)

@router.get("/{news_id}", response_model=NewsSchema)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    return news

@router.put("/{news_id}", response_model=NewsSchema, dependencies=[Depends(manager_or_admin)])
def update_news(
    news_id: int,
    news_update: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin)
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    for key, value in news_update.dict().items():
        setattr(db_news, key, value)
    
    db_news.updated_at = datetime.now()
    db.commit()
    db.refresh(db_news)
    return db_news

@router.delete("/{news_id}", dependencies=[Depends(manager_or_admin)])
def delete_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
    
    db.delete(news)
    db.commit()
    return {"message": "Новость удалена"} 