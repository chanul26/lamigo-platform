from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.preference_schemas import PreferenceCreate, PreferenceUpdate, PreferenceResponse
from app.services import preference_service

router = APIRouter()

@router.post("/", response_model=PreferenceResponse, status_code=status.HTTP_201_CREATED)
async def create_preference(
    payload: PreferenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint: Customer submits a date preference for their package.
    Requires only the exact package_id (UUID).
    """
    return await preference_service.create_preference(db, payload)


@router.get("/{package_id}", response_model=List[PreferenceResponse])
async def get_package_preferences(
    package_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint: Fetches all set preferences for a specific package.
    """
    return await preference_service.get_preferences_by_package(db, package_id)


@router.patch("/{preference_id}", response_model=PreferenceResponse)
async def update_preference(
    preference_id: UUID,
    payload: PreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint: Update a specific preference entry.
    """
    return await preference_service.update_preference(db, preference_id, payload)