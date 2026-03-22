from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.sql_models import DeliveryPreference, Package
from app.schemas.preference_schemas import PreferenceCreate, PreferenceUpdate

async def create_preference(db: AsyncSession, pref_in: PreferenceCreate) -> DeliveryPreference:
    """Creates a calendar preference. Validates the package_id exists first."""
    
    # Check if the package actually exists
    package_query = await db.execute(select(Package).where(Package.package_id == pref_in.package_id))
    if not package_query.scalars().first():
        raise HTTPException(status_code=404, detail="Package not found")
        
    new_preference = DeliveryPreference(**pref_in.model_dump())
    db.add(new_preference)
    await db.commit()
    await db.refresh(new_preference)
    return new_preference


async def get_preferences_by_package(db: AsyncSession, package_id: UUID) -> List[DeliveryPreference]:
    """Fetches all preference dates for a specific package."""
    query = select(DeliveryPreference).where(DeliveryPreference.package_id == package_id)
    # Order by target date so the closest dates appear first
    query = query.order_by(DeliveryPreference.target_date.asc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_preference(db: AsyncSession, preference_id: UUID, pref_in: PreferenceUpdate) -> DeliveryPreference:
    """Updates an existing preference."""
    query = await db.execute(select(DeliveryPreference).where(DeliveryPreference.preference_id == preference_id))
    preference = query.scalars().first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
        
    update_data = pref_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)
        
    await db.commit()
    await db.refresh(preference)
    return preference