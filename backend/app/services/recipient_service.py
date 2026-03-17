from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.sql_models import Recipient
from app.schemas.recipient_schemas import RecipientCreate, RecipientUpdate

async def create_recipient(db: AsyncSession, recipient_in: RecipientCreate) -> Recipient:
    new_recipient = Recipient(**recipient_in.model_dump())
    db.add(new_recipient)
    await db.commit()
    await db.refresh(new_recipient)
    return new_recipient

async def get_all_recipients(db: AsyncSession) -> list[Recipient]:
    result = await db.execute(select(Recipient))
    return result.scalars().all()

async def get_recipient(db: AsyncSession, recipient_id: UUID) -> Recipient:
    result = await db.execute(select(Recipient).where(Recipient.recipient_id == recipient_id))
    recipient = result.scalars().first()
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recipient not found"
        )
    return recipient

async def update_recipient(db: AsyncSession, recipient_id: UUID, recipient_in: RecipientUpdate) -> Recipient:
    recipient = await get_recipient(db, recipient_id)
    
    update_data = recipient_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(recipient, field, value)
        
    await db.commit()
    await db.refresh(recipient)
    
    return recipient