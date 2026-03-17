from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import RoleChecker
from app.models.enums import UserRole
from app.schemas.recipient_schemas import RecipientCreate, RecipientUpdate, RecipientResponse
from app.services import recipient_service

router = APIRouter()

# Security Gate: Only Admins and Station Managers can manage recipients
require_manager_or_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER])

@router.post("/", response_model=RecipientResponse, status_code=status.HTTP_201_CREATED)
async def create_recipient(
    recipient_in: RecipientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Register a new package recipient."""
    return await recipient_service.create_recipient(db, recipient_in)

@router.get("/", response_model=List[RecipientResponse])
async def read_recipients(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Retrieve all recipients."""
    return await recipient_service.get_all_recipients(db)

@router.get("/{recipient_id}", response_model=RecipientResponse)
async def read_recipient(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Get a specific recipient by ID."""
    return await recipient_service.get_recipient(db, recipient_id)

@router.put("/{recipient_id}", response_model=RecipientResponse)
async def update_recipient(
    recipient_id: UUID,
    recipient_in: RecipientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Update a recipient's information."""
    return await recipient_service.update_recipient(db, recipient_id, recipient_in)