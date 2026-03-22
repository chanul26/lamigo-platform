from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

# --- The Gatekeepers & Security ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole

# --- Schemas & Services ---
from app.schemas.recipient_schemas import RecipientUpdate, RecipientResponse
from app.services import recipient_service

router = APIRouter()

# Centralized dependency for the required roles
# This ensures only Super Admins can access these routes
ADMIN_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN]))

@router.get("/", response_model=List[RecipientResponse])
async def get_recipients(
    current_user: dict = ADMIN_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all recipients.
    Requires SUPER_ADMIN privileges.
    """
    return await recipient_service.get_all_recipients(db)


@router.get("/{recipient_id}", response_model=RecipientResponse)
async def get_recipient(
    recipient_id: UUID,
    current_user: dict = ADMIN_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a specific recipient by their UUID.
    Requires SUPER_ADMIN privileges.
    """
    return await recipient_service.get_recipient_by_id(db, recipient_id)


@router.patch("/{recipient_id}", response_model=RecipientResponse)
async def update_recipient(
    recipient_id: UUID,
    recipient_in: RecipientUpdate,
    current_user: dict = ADMIN_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Update specific fields of a recipient profile.
    Requires SUPER_ADMIN privileges.
    """
    return await recipient_service.update_recipient(db, recipient_id, recipient_in)