from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import RoleChecker
from app.models.enums import UserRole
from app.schemas.trip_schemas import TripCreate, TripResponse, DeliveryTaskCreate, DeliveryTaskResponse
from app.services import trip_service

router = APIRouter()

# Security Gate
require_manager_or_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER])

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_new_trip(
    trip_in: TripCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Create a new route manifest (Trip) for a branch."""
    return await trip_service.create_trip(db, trip_in)

@router.get("/{trip_id}", response_model=TripResponse)
async def read_trip(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Get the core details and total aggregates of a specific trip."""
    return await trip_service.get_trip(db, trip_id)

@router.post("/{trip_id}/tasks", response_model=DeliveryTaskResponse, status_code=status.HTTP_201_CREATED)
async def add_delivery_task(
    trip_id: UUID,
    task_in: DeliveryTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Assign a package to a trip. This automatically recalculates the route's total weight and COD."""
    return await trip_service.add_task_to_trip(db, trip_id, task_in)

@router.get("/{trip_id}/tasks", response_model=List[DeliveryTaskResponse])
async def read_trip_tasks(
    trip_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Get all package stops assigned to this route, ordered by sequence."""
    return await trip_service.get_trip_tasks(db, trip_id)
