from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.deps import RoleChecker
from app.models.enums import UserRole
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services import organization_service

router = APIRouter()

# SECURITY GATE: Only SuperAdmins can access these routes
require_super_admin = RoleChecker([UserRole.SUPER_ADMIN])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    # The moment this depends is hit, FastAPI checks Firebase + checks the SUPER_ADMIN role
    current_user: dict = Depends(require_super_admin) 
):
    """
    Create a new overarching Organization.
    **Requires Role:** SUPER_ADMIN
    """
    return await organization_service.create_organization(db, org_in)

@router.get("/", response_model=List[OrganizationResponse])
async def read_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """
    Retrieve all organizations in the system.
    **Requires Role:** SUPER_ADMIN
    """
    return await organization_service.get_organizations(db, skip=skip, limit=limit)

@router.get("/{org_id}", response_model=OrganizationResponse)
async def read_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_super_admin)
):
    """
    Get a specific organization by its UUID.
    **Requires Role:** SUPER_ADMIN
    """
    return await organization_service.get_organization_by_id(db, org_id)