from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import date

from app.models.sql_models import DeliveryPreference, Package # <-- CHANGED IMPORT
from app.schemas.delivery_preference_schemas import DeliveryPreferenceCreate, DeliveryPreferenceUpdate

async def create_preference(db: AsyncSession, pref_in: DeliveryPreferenceCreate) -> DeliveryPreference:
    # 1. Verify Package exists
    pkg_result = await db.execute(select(Package).where(Package.package_id == pref_in.package_id))
    if not pkg_result.scalars().first():
        raise HTTPException(status_code=404, detail=f"Package with ID {pref_in.package_id} not found.")

    # 2. Prevent duplicate entries for the same package on the same date
    duplicate_check = await db.execute(
        select(DeliveryPreference)
        .where(DeliveryPreference.package_id == pref_in.package_id)
        .where(DeliveryPreference.target_date == pref_in.target_date)
    )
    if duplicate_check.scalars().first():
        raise HTTPException(status_code=400, detail="A preference already exists for this package on this date.")

    # 3. Create record
    new_pref = DeliveryPreference(**pref_in.model_dump())
    db.add(new_pref)
    await db.commit()
    await db.refresh(new_pref)
    
    return new_pref

async def get_preferences_by_package(db: AsyncSession, package_id: UUID) -> list[DeliveryPreference]:
    """Fetch calendar preferences tied to a specific package."""
    result = await db.execute(
        select(DeliveryPreference).where(DeliveryPreference.package_id == package_id)
    )
    return list(result.scalars().all())

async def get_preference(db: AsyncSession, preference_id: UUID) -> DeliveryPreference:
    result = await db.execute(select(DeliveryPreference).where(DeliveryPreference.preference_id == preference_id))
    pref = result.scalars().first()
    if not pref:
        raise HTTPException(status_code=404, detail="Delivery preference not found.")
    return pref

async def update_preference(db: AsyncSession, preference_id: UUID, pref_in: DeliveryPreferenceUpdate) -> DeliveryPreference:
    pref = await get_preference(db, preference_id)
    pref.status = pref_in.status
    await db.commit()
    await db.refresh(pref)
    return pref