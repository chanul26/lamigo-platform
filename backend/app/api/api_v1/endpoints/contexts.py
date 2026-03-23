from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RoleChecker
from app.models.sql_models import DeliveryTask, Trip
from app.models.enums import UserRole
from app.schemas.context_schemas import ContextCreate, ContextUpdate, ContextResponse
from app.services import context_service

router = APIRouter()

# Typically, system services or Admins/Managers update ML context
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.post("/", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def create_context(
    context_in: ContextCreate,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Deep IDOR Security: Prevent Managers from attaching context to tasks in other branches
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        
        # Join DeliveryTask -> Trip to check branch ownership
        query = select(DeliveryTask).join(Trip).where(
            DeliveryTask.task_id == context_in.task_id,
            Trip.branch_id == secure_branch
        )
        task_in_branch = await db.scalar(query)
        
        if not task_in_branch:
             raise HTTPException(status_code=403, detail="Access Denied: Task belongs to a different branch.")

    return await context_service.create_context(db, context_in)

@router.get("/", response_model=List[ContextResponse])
async def get_contexts(
    task_id: Optional[UUID] = Query(None, description="Filter metadata by specific task"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await context_service.get_all_contexts(db, task_id=task_id)

@router.get("/{metadata_id}", response_model=ContextResponse)
async def get_context(
    metadata_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await context_service.get_context(db, metadata_id)

@router.patch("/{metadata_id}", response_model=ContextResponse)
async def update_context(
    metadata_id: UUID,
    context_in: ContextUpdate,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await context_service.update_context(db, metadata_id, context_in)