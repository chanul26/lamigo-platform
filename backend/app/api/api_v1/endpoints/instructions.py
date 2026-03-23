from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RoleChecker
from app.models.sql_models import DeliveryTask, Trip
from app.models.enums import UserRole
from app.schemas.instruction_schemas import InstructionCreate, InstructionUpdate, InstructionResponse
from app.services import instruction_service

router = APIRouter()

ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=InstructionResponse, status_code=status.HTTP_201_CREATED)
async def create_instruction(
    instruction_in: InstructionCreate,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # Deep IDOR Security: Prevent Managers from adding notes to tasks in other branches
    user_role = current_user.get("role")
    if user_role == UserRole.STATION_MANAGER:
        secure_branch = current_user.get("branch_id")
        
        # We must join DeliveryTask -> Trip to check the branch ownership
        query = select(DeliveryTask).join(Trip).where(
            DeliveryTask.task_id == instruction_in.task_id,
            Trip.branch_id == secure_branch
        )
        task_in_branch = await db.scalar(query)
        
        if not task_in_branch:
             raise HTTPException(status_code=403, detail="Access Denied: Task belongs to a different branch.")

    return await instruction_service.create_instruction(db, instruction_in)


@router.get("/", response_model=List[InstructionResponse])
async def get_instructions(
    task_id: Optional[UUID] = Query(None, description="Filter notes by specific task"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await instruction_service.get_all_instructions(db, task_id=task_id)


@router.get("/{instruction_id}", response_model=InstructionResponse)
async def get_instruction(
    instruction_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await instruction_service.get_instruction(db, instruction_id)


@router.patch("/{instruction_id}", response_model=InstructionResponse)
async def update_instruction(
    instruction_id: UUID,
    instruction_in: InstructionUpdate,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await instruction_service.update_instruction(db, instruction_id, instruction_in)


@router.delete("/{instruction_id}", status_code=status.HTTP_200_OK)
async def delete_instruction(
    instruction_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Soft deletes an instruction."""
    return await instruction_service.delete_instruction(db, instruction_id)