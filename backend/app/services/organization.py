from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.models.sql_models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

async def create_organization(db: AsyncSession, org_in: OrganizationCreate) -> Organization:
    """Creates a new organization in the database."""
    
    # Optional but recommended: Check if contact email already exists
    result = await db.execute(select(Organization).where(Organization.contact_email == org_in.contact_email))
    existing_org = result.scalars().first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="An organization with this email already exists."
        )

    # Convert Pydantic schema to SQLAlchemy model
    new_org = Organization(**org_in.model_dump())
    
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    
    return new_org


async def get_all_organizations(db: AsyncSession) -> list[Organization]:
    """Fetches all organizations."""
    # Using modern SQLAlchemy 2.0 syntax
    result = await db.execute(select(Organization))
    return result.scalars().all()


async def get_organization(db: AsyncSession, org_id: UUID) -> Organization:
    """Fetches a single organization by its UUID."""
    result = await db.execute(select(Organization).where(Organization.org_id == org_id))
    org = result.scalars().first()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Organization not found"
        )
    return org


async def update_organization(db: AsyncSession, org_id: UUID, org_in: OrganizationUpdate) -> Organization:
    """Updates specific fields of an organization."""
    org = await get_organization(db, org_id)
    
    # exclude_unset=True ensures we only update fields the user actually sent in the PATCH/PUT request
    update_data = org_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(org, field, value)
        
    await db.commit()
    await db.refresh(org)
    
    return org


async def deactivate_organization(db: AsyncSession, org_id: UUID):
    """Soft deletes an organization by setting is_active to False."""
    org = await get_organization(db, org_id)
    
    if not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is already deactivated"
        )
        
    org.is_active = False
    await db.commit()
    
    return {"message": f"Organization '{org.name}' successfully deactivated"}