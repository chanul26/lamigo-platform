from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import RoleChecker
from app.models.enums import UserRole
from app.schemas.delivery_preference_schemas import DeliveryPreferenceCreate, DeliveryPreferenceUpdate, DeliveryPreferenceResponse
from app.services import delivery_preference_service

router = APIRouter()

require_manager_or_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER])

@router.post("/", response_model=DeliveryPreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery_preference(
    pref_in: DeliveryPreferenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Log a calendar constraint for a specific package."""
    return await delivery_preference_service.create_preference(db, pref_in)

@router.get("/", response_model=List[DeliveryPreferenceResponse])
async def read_package_preferences(
    package_id: UUID = Query(..., description="The ID of the package to fetch calendar data for"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Get all set calendar preferences for a specific package."""
    return await delivery_preference_service.get_preferences_by_package(db, package_id)

@router.put("/{preference_id}", response_model=DeliveryPreferenceResponse)
async def update_delivery_preference(
    preference_id: UUID,
    pref_in: DeliveryPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Update a previously set preference."""
    return await delivery_preference_service.update_preference(db, preference_id, pref_in)