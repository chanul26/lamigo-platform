from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID

from app.models.sql_models import Organization
from app.schemas.organization import OrganizationCreate

async def create_organization(db: AsyncSession, org_in: OrganizationCreate) -> Organization:
    """Creates a new Organization in the database."""
    
    # 1. Check if an organization with this email already exists
    query = select(Organization).where(Organization.contact_email == org_in.contact_email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="An organization with this contact email already exists."
        )
    
    # 2. Create the new SQLAlchemy model instance
    db_org = Organization(**org_in.model_dump())
    
    # 3. Save to database
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    
    return db_org

async def get_organizations(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Retrieves a list of organizations."""
    query = select(Organization).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_organization_by_id(db: AsyncSession, org_id: UUID) -> Organization:
    """Retrieves a single organization by its ID."""
    query = select(Organization).where(Organization.org_id == org_id)
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Organization not found."
        )
    return org