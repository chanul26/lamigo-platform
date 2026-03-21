from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import Trip
from app.models.enums import TripStatus
from app.schemas.trip_schemas import TripCreate, TripUpdate

async def create_trip(db: AsyncSession, trip_in: TripCreate) -> Trip:
    """Creates a new Trip manifest in the DRAFT state."""
    new_trip = Trip(**trip_in.model_dump())
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)
    return new_trip


async def get_all_trips(
    db: AsyncSession, 
    branch_id: Optional[UUID] = None, 
    trip_status: Optional[TripStatus] = None
) -> List[Trip]:
    """Fetches all trips. Uses Query Parameters for powerful backend filtering."""
    query = select(Trip)
    
    # Optional Filters triggered by the frontend URL (e.g., ?branch_id=...&status=DRAFT)
    if branch_id:
        query = query.where(Trip.branch_id == branch_id)
    if trip_status:
        query = query.where(Trip.status == trip_status)
        
    # Always return the newest trips first
    query = query.order_by(Trip.created_at.desc())
        
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_trip(db: AsyncSession, trip_id: UUID) -> Trip:
    """Fetches a specific trip by its UUID."""
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    trip = result.scalars().first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Trip not found"
        )
    return trip


async def update_trip(db: AsyncSession, trip_id: UUID, trip_in: TripUpdate) -> Trip:
    """Updates a trip (e.g., assigning a driver later or changing status)."""
    trip = await get_trip(db, trip_id)
    
    # exclude_unset=True ensures we ONLY update the fields the frontend actually sent
    update_data = trip_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
        
    await db.commit()
    await db.refresh(trip)
    return trip