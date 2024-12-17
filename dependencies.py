from fastapi import Depends, HTTPException, status
from functools import wraps
from typing import List
from models import UserRole, User
from routers.auth import get_current_user

def check_roles(allowed_roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этой операции"
            )
        return current_user
    return role_checker

admin_only = check_roles([UserRole.ADMIN])
trainer_or_admin = check_roles([UserRole.ADMIN, UserRole.TRAINER])
all_roles = check_roles([UserRole.ADMIN, UserRole.TRAINER, UserRole.CLIENT]) 