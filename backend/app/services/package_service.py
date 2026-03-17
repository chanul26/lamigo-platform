import random
import string
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.sql_models import Package, Recipient, Branch
from app.schemas.package_schemas import PackageCreate, PackageUpdate


def generate_tracking_id() -> str:
    """Generates a unique tracking ID like LMG-A8F9B2"""
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"LMG-{random_str}"


async def create_package(db: AsyncSession, package_in: PackageCreate) -> Package:
    # 1. Verify the Branch exists
    branch_result = await db.execute(select(Branch).where(Branch.branch_id == package_in.branch_id))
    if not branch_result.scalars().first():
        raise HTTPException(status_code=404, detail=f"Branch with ID {package_in.branch_id} not found.")

    # 2. Verify the Recipient exists
    recipient_result = await db.execute(select(Recipient).where(Recipient.recipient_id == package_in.recipient_id))
    recipient = recipient_result.scalars().first()
    if not recipient:
        raise HTTPException(status_code=404, detail=f"Recipient with ID {package_in.recipient_id} not found.")

    # 3. Prepare the package data with generated fields and snapshots
    package_data = package_in.model_dump()
    package_data["tracking_id"] = generate_tracking_id()

    # Take a snapshot of the recipient's current location data
    package_data["recipient_name"] = recipient.name
    package_data["address"] = recipient.address
    package_data["gps_lat"] = float(recipient.gps_lat)
    package_data["gps_lng"] = float(recipient.gps_lng)

    # 4. Save to Database
    new_package = Package(**package_data)
    db.add(new_package)
    await db.commit()
    await db.refresh(new_package)

    return new_package


async def get_all_packages(db: AsyncSession, branch_id: UUID | None = None) -> list[Package]:
    query = select(Package)
    # Optional filtering by branch for the frontend hub view
    if branch_id:
        query = query.where(Package.branch_id == branch_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_package(db: AsyncSession, package_id: UUID) -> Package:
    result = await db.execute(select(Package).where(Package.package_id == package_id))
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
    await db.refresh(package)
    return package
