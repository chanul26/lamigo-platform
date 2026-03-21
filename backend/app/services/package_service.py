from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.sql_models import Package, Recipient
from app.models.enums import PackageStatus
from app.schemas.package_schemas import PackageCreate, PackageUpdate
from app.services.utils import generate_package_tracking_id

async def create_package_with_recipient(db: AsyncSession, package_data: PackageCreate, branch_id: UUID) -> Package:
    """Handles the Recipient Upsert, Tracking ID generation, and Package creation."""
    
    # --- 1. THE RECIPIENT UPSERT ---
    result = await db.execute(select(Recipient).where(Recipient.phone_number == package_data.recipient_phone))
    recipient = result.scalars().first()

    if not recipient:
        # Silently create a new recipient profile in the background
        recipient = Recipient(
            name=package_data.recipient_name,
            phone_number=package_data.recipient_phone,
            address=package_data.address,
            location_type=package_data.location_type,
            floor_number=package_data.floor_number,
            gps_lat=package_data.gps_lat,
            gps_lng=package_data.gps_lng,
            is_location_verified=False
        )
        db.add(recipient)
        await db.flush() # Flush generates the recipient_id without fully committing the transaction yet

    # --- 2. THE TRACKING ID ---
    # We use the utility function you already have in app/services/utils.py
    tracking_id = generate_package_tracking_id(branch_id)

    # --- 3. CREATE THE PACKAGE ---
    new_package = Package(
        tracking_id=tracking_id,
        recipient_id=recipient.recipient_id,
        branch_id=branch_id,
        status=PackageStatus.TO_BE_DELIVERED,
        
        sender_name=package_data.sender_name,
        sender_phone=package_data.sender_phone,
        sender_address=package_data.sender_address,
        
        weight=package_data.weight,
        is_cod=package_data.is_cod,
        cod_amount=package_data.cod_amount,
        delivery_charge=package_data.delivery_charge,
        
        # Snapshot Data
        recipient_name=package_data.recipient_name,
        address=package_data.address,
        gps_lat=package_data.gps_lat,
        gps_lng=package_data.gps_lng
    )
    db.add(new_package)
    await db.commit()
    
    # --- 4. RELOAD WITH RELATIONSHIPS ---
    # We must reload the package using `selectinload` so SQLAlchemy attaches the nested 
    # Recipient data for our Pydantic PackageResponse schema to read!
    final_result = await db.execute(
        select(Package).options(selectinload(Package.recipient)).where(Package.package_id == new_package.package_id)
    )
    return final_result.scalars().first()


async def get_all_packages(
    db: AsyncSession, 
    branch_id: Optional[UUID] = None, 
    package_status: Optional[PackageStatus] = None
) -> List[Package]:
    """Fetches packages with the nested recipient attached."""
    query = select(Package).options(selectinload(Package.recipient))
    
    if branch_id:
        query = query.where(Package.branch_id == branch_id)
    if package_status:
        query = query.where(Package.status == package_status)
        
    query = query.order_by(Package.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_package(db: AsyncSession, package_id: UUID) -> Package:
    result = await db.execute(
        select(Package).options(selectinload(Package.recipient)).where(Package.package_id == package_id)
    )
    package = result.scalars().first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return package


async def update_package(db: AsyncSession, package_id: UUID, package_in: PackageUpdate) -> Package:
    package = await get_package(db, package_id)
    update_data = package_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(package, field, value)
    await db.commit()
    
    # Reload to ensure nested relationship is still attached for response
    return await get_package(db, package_id)