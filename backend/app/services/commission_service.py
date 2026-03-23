from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import TripCommission, Trip, Driver, DriverFinancialProfile
from app.schemas.commission_schemas import CommissionCreate

def _commission_to_dict(commission: TripCommission) -> dict:
    """Safely converts model to dict to prevent MissingGreenlet errors."""
    comm_dict = commission.__dict__.copy()
    comm_dict.pop("_sa_instance_state", None)
    return comm_dict


async def create_commission(db: AsyncSession, commission_in: CommissionCreate) -> dict:
    # 1. Verify Trip exists
    trip = await db.scalar(select(Trip).where(Trip.trip_id == commission_in.trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # 2. Verify Driver exists
    driver = await db.scalar(select(Driver).where(Driver.driver_id == commission_in.driver_id))
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # 3. Create the Immutable Commission Record
    new_comm = TripCommission(**commission_in.model_dump())
    db.add(new_comm)

    # 4. ATOMIC UPDATE: Sync Driver's Financial Profile (if it exists)
    profile = await db.scalar(
        select(DriverFinancialProfile).where(DriverFinancialProfile.driver_id == commission_in.driver_id)
    )
    if profile:
        profile.current_payable_balance += commission_in.amount_earned
        profile.total_lifetime_earnings += commission_in.amount_earned

    await db.commit()
    await db.refresh(new_comm)
    return _commission_to_dict(new_comm)


async def get_all_commissions(
    db: AsyncSession, 
    trip_id: Optional[UUID] = None, 
    driver_id: Optional[str] = None
) -> List[dict]:
    query = select(TripCommission)
    
    if trip_id:
        query = query.where(TripCommission.trip_id == trip_id)
    if driver_id:
        query = query.where(TripCommission.driver_id == driver_id)
        
    query = query.order_by(TripCommission.created_at.desc())
    result = await db.execute(query)
    commissions = result.scalars().all()
    
    return [_commission_to_dict(comm) for comm in commissions]


async def get_commission(db: AsyncSession, commission_id: UUID) -> dict:
    result = await db.execute(select(TripCommission).where(TripCommission.commission_id == commission_id))
    commission = result.scalars().first()
    
    if not commission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission record not found")
    return _commission_to_dict(commission)