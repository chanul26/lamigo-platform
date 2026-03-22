from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import Trip
from app.models.enums import TripStatus
from app.schemas.trip_schemas import TripCreate, TripUpdate

def _trip_to_dict(trip: Trip) -> dict:
    """Safely converts a Trip model to a dict per the architecture rules."""
    trip_dict = trip.__dict__.copy()
    trip_dict.pop("_sa_instance_state", None)
    return trip_dict

async def create_trip(db: AsyncSession, trip_in: TripCreate) -> dict:
    new_trip = Trip(**trip_in.model_dump())
    db.add(new_trip)
    await db.commit()
    await db.refresh(new_trip)
    return _trip_to_dict(new_trip)

async def get_all_trips(
    db: AsyncSession, 
    branch_id: Optional[UUID] = None, 
    trip_status: Optional[TripStatus] = None
) -> List[dict]:
    query = select(Trip)
    if branch_id:
        query = query.where(Trip.branch_id == branch_id)
    if trip_status:
        query = query.where(Trip.status == trip_status)
        
    query = query.order_by(Trip.created_at.desc())
    result = await db.execute(query)
    trips = result.scalars().all()
    return [_trip_to_dict(trip) for trip in trips]

async def get_trip(db: AsyncSession, trip_id: UUID) -> dict:
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return _trip_to_dict(trip)

async def update_trip(db: AsyncSession, trip_id: UUID, trip_in: TripUpdate) -> dict:
    result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
    trip = result.scalars().first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        
    update_data = trip_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
        
    await db.commit()
    await db.refresh(trip)
    return _trip_to_dict(trip)