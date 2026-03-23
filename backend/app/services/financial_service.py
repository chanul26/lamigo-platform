from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.models.sql_models import DriverFinancialProfile, Driver, User

def _profile_to_dict(profile: DriverFinancialProfile) -> dict:
    """Dictionary Rule implementation for async safety."""
    p_dict = profile.__dict__.copy()
    p_dict.pop("_sa_instance_state", None)
    return p_dict

async def get_all_profiles(db: AsyncSession, branch_id: Optional[UUID] = None) -> List[dict]:
    """Fetches all financial profiles, optionally filtered by branch."""
    query = select(DriverFinancialProfile)
    
    if branch_id:
        # Join through Driver -> User to filter by branch
        query = query.join(Driver, DriverFinancialProfile.driver_id == Driver.driver_id)\
                     .join(User, Driver.driver_id == User.user_id)\
                     .where(User.branch_id == branch_id)
                     
    result = await db.execute(query)
    profiles = result.scalars().all()
    
    return [_profile_to_dict(p) for p in profiles]

async def get_profile(db: AsyncSession, driver_id: str) -> dict:
    """Fetches a specific driver's profile, creating a blank one if it doesn't exist (Lazy Init)."""
    result = await db.execute(select(DriverFinancialProfile).where(DriverFinancialProfile.driver_id == driver_id))
    profile = result.scalars().first()
    
    # LAZY INITIALIZATION: If no profile exists, create a 0.00 baseline
    if not profile:
        # First verify the driver actually exists
        driver = await db.scalar(select(Driver).where(Driver.driver_id == driver_id))
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
            
        profile = DriverFinancialProfile(
            driver_id=driver_id,
            current_payable_balance=0.00,
            total_lifetime_earnings=0.00,
            total_lifetime_settled=0.00
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
    return _profile_to_dict(profile)