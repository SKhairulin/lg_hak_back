from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import GymMembership, User
from schemas import MembershipCreate, GymMembership as MembershipSchema
from dependencies import get_current_user, manager_or_admin
from services.membership import MembershipService

router = APIRouter(prefix="/api/membership", tags=["membership"])

@router.post("/create", response_model=MembershipSchema)
async def create_membership(
    membership: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin)
):
    membership_service = MembershipService(db)
    return await membership_service.create_membership(
        membership.user_id,
        membership.membership_type_id,
        membership.payment_id
    )

@router.post("/{membership_id}/extend", response_model=MembershipSchema)
async def extend_membership(
    membership_id: int,
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership_service = MembershipService(db)
    return await membership_service.extend_membership(membership_id, payment_id)

@router.post("/{membership_id}/freeze", response_model=MembershipSchema)
async def freeze_membership(
    membership_id: int,
    days: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership_service = MembershipService(db)
    return await membership_service.freeze_membership(membership_id, days, reason)

@router.post("/{membership_id}/unfreeze", response_model=MembershipSchema)
async def unfreeze_membership(
    membership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership_service = MembershipService(db)
    return await membership_service.unfreeze_membership(membership_id)

@router.get("/my", response_model=MembershipSchema)
async def get_my_membership(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership_service = MembershipService(db)
    membership = membership_service.get_active_membership(current_user.id)
    if not membership:
        raise HTTPException(status_code=404, detail="Активный абонемент не найден")
    return membership

@router.get("/all", response_model=List[MembershipSchema])
async def get_all_memberships(
    db: Session = Depends(get_db),
    current_user: User = Depends(manager_or_admin)
):
    return db.query(GymMembership).all() 