from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import DeliveryContext, DeliveryTask
from app.schemas.context_schemas import ContextCreate, ContextUpdate

def _context_to_dict(context: DeliveryContext) -> dict:
    """Safely converts model to dict to prevent MissingGreenlet errors."""
    ctx_dict = context.__dict__.copy()
    ctx_dict.pop("_sa_instance_state", None)
    return ctx_dict

async def create_context(db: AsyncSession, context_in: ContextCreate) -> dict:
    # Verify the Task exists before attaching metadata
    task = await db.scalar(select(DeliveryTask).where(DeliveryTask.task_id == context_in.task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Delivery Task not found")

    new_context = DeliveryContext(**context_in.model_dump())
    db.add(new_context)
    await db.commit()
    await db.refresh(new_context)
    return _context_to_dict(new_context)

async def get_all_contexts(db: AsyncSession, task_id: Optional[UUID] = None) -> List[dict]:
    query = select(DeliveryContext)
    
    if task_id:
        query = query.where(DeliveryContext.task_id == task_id)
        
    query = query.order_by(DeliveryContext.created_at.desc())
    result = await db.execute(query)
    contexts = result.scalars().all()
    
    return [_context_to_dict(ctx) for ctx in contexts]

async def get_context(db: AsyncSession, metadata_id: UUID) -> dict:
    result = await db.execute(select(DeliveryContext).where(DeliveryContext.metadata_id == metadata_id))
    context = result.scalars().first()
    
    if not context:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery Context not found")
    return _context_to_dict(context)

async def update_context(db: AsyncSession, metadata_id: UUID, context_in: ContextUpdate) -> dict:
    result = await db.execute(select(DeliveryContext).where(DeliveryContext.metadata_id == metadata_id))
    context = result.scalars().first()
    
    if not context:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery Context not found")
        
    update_data = context_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(context, field, value)
        
    await db.commit()
    await db.refresh(context)
    return _context_to_dict(context)