from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# --- Security Gatekeepers ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, TripStatus

# --- Schemas & Services ---
from app.schemas.trip_schemas import TripCreate, TripUpdate, TripResponse
from app.services import trip_service

router = APIRouter()

# Define our RBAC (Role-Based Access Control) levels
MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_in: TripCreate,
    # Only Admins and Station Managers can create trips
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new empty Trip manifest.
    Defaults to DRAFT status with 0 packages.
    """
    return await trip_service.create_trip(db, trip_in)


@router.get("/", response_model=List[TripResponse])
async def get_trips(
    # FastAPI automatically catches ?branch_id=... and ?trip_status=... from the URL
    branch_id: Optional[UUID] = Query(None, description="Filter trips by physical branch"),
    trip_status: Optional[TripStatus] = Query(None, description="Filter by trip state (e.g., DRAFT, IN_PROGRESS)"),
    # Drivers need to see their assigned trips, so all roles are allowed
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of trips. Uses Query Parameters for powerful backend filtering.
    """
    return await trip_service.get_all_trips(db, branch_id=branch_id, trip_status=trip_status)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a specific trip by its UUID.
    """
    return await trip_service.get_trip(db, trip_id)


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID,
    trip_in: TripUpdate,
    # Only Managers and Admins can re-assign drivers or manually override status
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a trip (e.g., assigning a driver to a DRAFT trip).
    """
    return await trip_service.update_trip(db, trip_id, trip_in)