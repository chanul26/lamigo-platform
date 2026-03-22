from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole
from app.models.sql_models import User
from app.schemas.financial_schemas import FinancialProfileResponse
from app.services import financial_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.get("/", response_model=List[FinancialProfileResponse])
async def get_all_financial_profiles(
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Managers can view all financial profiles within their own branch."""
    user_role = current_user.get("role")
    branch_id = current_user.get("branch_id") if user_role == UserRole.STATION_MANAGER else None
    
    return await financial_service.get_all_profiles(db, branch_id=branch_id)

@router.get("/{driver_id}", response_model=FinancialProfileResponse)
async def get_financial_profile(
    driver_id: str,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Fetch a specific profile. Drivers can ONLY fetch their own."""
    # Deep IDOR Security
    user_role = current_user.get("role")
    
    if user_role == UserRole.DRIVER:
        if driver_id != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access Denied: You can only view your own financials.")
            
    elif user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        driver_user = await db.scalar(select(User).where(User.user_id == driver_id))
        if not driver_user or driver_user.branch_id != secure_branch:
             raise HTTPException(status_code=403, detail="Access Denied: Driver belongs to a different branch.")

    return await financial_service.get_profile(db, driver_id)