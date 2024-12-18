from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import GymMembership, User, UserRole
from schemas import GymMembershipCreate, GymMembership as GymMembershipSchema, GymMembershipBase
from .auth import get_current_user
from dependencies import admin_only, trainer_or_admin, all_roles

router = APIRouter(prefix="/api/membership", tags=["membership"])

@router.post("/", response_model=GymMembershipSchema, dependencies=[Depends(trainer_or_admin)])
def create_membership(
    membership: GymMembershipCreate,
    db: Session = Depends(get_db)
):
    db_membership = GymMembership(**membership.dict())
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

@router.get("/my", response_model=GymMembershipSchema, dependencies=[Depends(all_roles)])
def get_my_membership(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(GymMembership).filter(GymMembership.user_id == current_user.id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Абонемент не найден")
    return membership

@router.get("/all", response_model=List[GymMembershipSchema], dependencies=[Depends(trainer_or_admin)])
def get_all_memberships(db: Session = Depends(get_db)):
    return db.query(GymMembership).all()

@router.put("/{membership_id}", response_model=GymMembershipSchema, dependencies=[Depends(trainer_or_admin)])
def update_membership(
    membership_id: int,
    membership_data: GymMembershipBase,
    db: Session = Depends(get_db)
):
    membership = db.query(GymMembership).filter(GymMembership.id == membership_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Абонемент не найден")
    
    for key, value in membership_data.dict().items():
        setattr(membership, key, value)
    
    db.commit()
    db.refresh(membership)
    return membership 