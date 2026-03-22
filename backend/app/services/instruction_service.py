from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List, Optional

from app.models.sql_models import TaskInstruction, DeliveryTask
from app.schemas.instruction_schemas import InstructionCreate, InstructionUpdate

def _instruction_to_dict(instruction: TaskInstruction) -> dict:
    """Safely converts model to dict to prevent MissingGreenlet errors."""
    inst_dict = instruction.__dict__.copy()
    inst_dict.pop("_sa_instance_state", None)
    return inst_dict


async def create_instruction(db: AsyncSession, instruction_in: InstructionCreate) -> dict:
    # 1. Verify the Task actually exists
    task = await db.scalar(select(DeliveryTask).where(DeliveryTask.task_id == instruction_in.task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Delivery Task not found")

    # 2. Create Instruction
    new_inst = TaskInstruction(**instruction_in.model_dump())
    db.add(new_inst)
    await db.commit()
    await db.refresh(new_inst)
    return _instruction_to_dict(new_inst)


async def get_all_instructions(db: AsyncSession, task_id: Optional[UUID] = None) -> List[dict]:
    """Fetches instructions, intentionally ignoring soft-deleted ones."""
    query = select(TaskInstruction).where(TaskInstruction.is_deleted == False)
    
    if task_id:
        query = query.where(TaskInstruction.task_id == task_id)
        
    query = query.order_by(TaskInstruction.created_at.asc())
    result = await db.execute(query)
    instructions = result.scalars().all()
    
    return [_instruction_to_dict(inst) for inst in instructions]


async def get_instruction(db: AsyncSession, instruction_id: UUID) -> dict:
    result = await db.execute(
        select(TaskInstruction).where(
            TaskInstruction.instruction_id == instruction_id,
            TaskInstruction.is_deleted == False
        )
    )
    instruction = result.scalars().first()
    
    if not instruction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instruction not found or deleted")
    return _instruction_to_dict(instruction)


async def update_instruction(db: AsyncSession, instruction_id: UUID, instruction_in: InstructionUpdate) -> dict:
    result = await db.execute(
        select(TaskInstruction).where(
            TaskInstruction.instruction_id == instruction_id,
            TaskInstruction.is_deleted == False
        )
    )
    instruction = result.scalars().first()
    
    if not instruction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instruction not found or deleted")
        
    update_data = instruction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instruction, field, value)
        
    await db.commit()
    await db.refresh(instruction)
    return _instruction_to_dict(instruction)


async def delete_instruction(db: AsyncSession, instruction_id: UUID) -> dict:
    """Executes a Soft Delete instead of a hard database removal."""
    result = await db.execute(select(TaskInstruction).where(TaskInstruction.instruction_id == instruction_id))
    instruction = result.scalars().first()
    
    if not instruction or instruction.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instruction not found or already deleted")
        
    # Apply Soft Delete
    instruction.is_deleted = True
    instruction.deleted_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(instruction)
    return _instruction_to_dict(instruction)