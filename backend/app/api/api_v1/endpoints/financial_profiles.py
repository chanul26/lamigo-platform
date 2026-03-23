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
    branch_id = None
    
    if user_role == UserRole.STATION_MANAGER:
        # Bulletproof token extraction
        manager_uid = current_user.get("uid") or current_user.get("user_id")
        manager_user = await db.scalar(select(User).where(User.user_id == manager_uid))
        if manager_user:
            branch_id = manager_user.branch_id
            
    return await financial_service.get_all_profiles(db, branch_id=branch_id)

@router.get("/{driver_id}", response_model=FinancialProfileResponse)
async def get_financial_profile(
    driver_id: str,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Fetch a specific profile. Drivers can ONLY fetch their own."""
    user_role = current_user.get("role")
    
    if user_role == UserRole.DRIVER:
        # Bulletproof token extraction
        token_uid = current_user.get("uid") or current_user.get("user_id")
        if driver_id != token_uid:
            raise HTTPException(status_code=403, detail="Access Denied: You can only view your own financials.")
            
    elif user_role == UserRole.STATION_MANAGER:
        # Bulletproof token extraction
        manager_uid = current_user.get("uid") or current_user.get("user_id")
        
        # 1. Check if Manager exists
        manager_user = await db.scalar(select(User).where(User.user_id == manager_uid))
        if not manager_user:
            raise HTTPException(status_code=404, detail=f"Manager profile not found for token ID: {manager_uid}")
            
        # 2. Check if Driver exists
        driver_user = await db.scalar(select(User).where(User.user_id == driver_id))
        if not driver_user:
             raise HTTPException(status_code=404, detail="Driver profile not found in database.")
             
        # 3. Compare Branches
        if str(manager_user.branch_id) != str(driver_user.branch_id):
             raise HTTPException(
                 status_code=403, 
                 detail=f"Branch Mismatch: Manager ({manager_user.branch_id}) cannot view Driver ({driver_user.branch_id})"
             )

    return await financial_service.get_profile(db, driver_id)