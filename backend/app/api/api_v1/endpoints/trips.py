from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, TripStatus
from app.schemas.trip_schemas import TripCreate, TripUpdate, TripResponse
from app.services import trip_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_in: TripCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Security Override
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        if trip_in.branch_id != secure_branch:
            raise HTTPException(status_code=403, detail="You can only create trips for your own branch.")
            
    return await trip_service.create_trip(db, trip_in)

@router.get("/", response_model=List[TripResponse])
async def get_trips(
    branch_id: Optional[UUID] = Query(None, description="Filter trips by physical branch"),
    trip_status: Optional[TripStatus] = Query(None, description="Filter by trip state"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Security Override
    user_role = current_user.get("role")
    if user_role in [UserRole.STATION_MANAGER, UserRole.DRIVER]:
        secure_branch = current_user.get("branch_id")
        if not secure_branch:
            raise HTTPException(status_code=403, detail="No branch assigned.")
        branch_id = secure_branch # Force the filter

    return await trip_service.get_all_trips(db, branch_id=branch_id, trip_status=trip_status)

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    trip = await trip_service.get_trip(db, trip_id)
    
    # Security Override
    user_role = current_user.get("role")
    if user_role in [UserRole.STATION_MANAGER, UserRole.DRIVER]:
        if trip.get("branch_id") != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="Access Denied.")
            
    return trip

@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID,
    trip_in: TripUpdate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    existing_trip = await trip_service.get_trip(db, trip_id)
    
    # Security Override
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        if existing_trip.get("branch_id") != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="Access Denied.")

    return await trip_service.update_trip(db, trip_id, trip_in)