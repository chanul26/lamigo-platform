from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RoleChecker
from app.models.sql_models import Trip
from app.models.enums import UserRole
from app.schemas.commission_schemas import CommissionCreate, CommissionResponse
from app.services import commission_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=CommissionResponse, status_code=status.HTTP_201_CREATED)
async def create_commission(
    commission_in: CommissionCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Deep IDOR Security: Station Managers can only log commissions for trips in their own branch
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        trip = await db.scalar(select(Trip).where(Trip.trip_id == commission_in.trip_id))
        
        if not trip or trip.branch_id != secure_branch:
             raise HTTPException(
                 status_code=403, 
                 detail="Access Denied: You cannot log commissions for a trip outside your branch."
             )

    return await commission_service.create_commission(db, commission_in)


@router.get("/", response_model=List[CommissionResponse])
async def get_commissions(
    trip_id: Optional[UUID] = Query(None, description="Filter by trip"),
    driver_id: Optional[str] = Query(None, description="Filter by driver"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Deep IDOR Security: Drivers can ONLY see their own commissions
    user_role = current_user.get("role")
    if user_role == UserRole.DRIVER:
        driver_id = current_user.get("uid") # Force the filter to the logged-in driver's ID

    return await commission_service.get_all_commissions(db, trip_id=trip_id, driver_id=driver_id)


@router.get("/{commission_id}", response_model=CommissionResponse)
async def get_commission(
    commission_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    commission = await commission_service.get_commission(db, commission_id)
    
    # Security: If driver, ensure they own it
    if current_user.get("role") == UserRole.DRIVER:
        if commission.get("driver_id") != current_user.get("uid"):
            raise HTTPException(status_code=403, detail="Access Denied")
            
    return commission