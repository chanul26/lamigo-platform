from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, BackgroundTasks # <-- NEW: Imported BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

# --- The Gatekeepers & Security ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole

# --- Schemas & Services ---
from app.schemas.recipient_schemas import RecipientUpdate, RecipientResponse
from app.services import recipient_service
from app.services.audit_service import log_audit_action # <-- NEW: Imported your Audit Service

router = APIRouter()

# Centralized dependency for the required roles
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
    background_tasks: BackgroundTasks, # <-- NEW: Injected BackgroundTasks
    current_user: dict = ADMIN_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Update specific fields of a recipient profile.
    Requires SUPER_ADMIN privileges.
    """
    # 1. Update the database via PostgreSQL
    updated_recipient = await recipient_service.update_recipient(db, recipient_id, recipient_in)
    
    # 2. Safely extract the Admin's ID
    actor_id = current_user.get("user_id") or current_user.get("admin_id", "Unknown")
    
    # 3. Fire and forget the DynamoDB log!
    background_tasks.add_task(
        log_audit_action,
        actor_id=actor_id,
        action="UPDATE",
        resource_id=str(updated_recipient.recipient_id),
        resource_type="Recipient",
        # exclude_unset=True ensures we ONLY log the specific fields the Admin changed
        details=recipient_in.model_dump(exclude_unset=True) 
    )
    
    return updated_recipient