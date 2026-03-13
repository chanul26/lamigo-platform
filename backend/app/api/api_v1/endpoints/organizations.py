from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

# --- The Gatekeepers & Security ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole

# --- Schemas & Services ---
from app.schemas.organization_schemas import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.services import organization_service

router = APIRouter()

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    # RBAC Gatekeeper: Strictly Super Admin only
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new organization. 
    Requires SUPER_ADMIN privileges.
    """
    return await organization_service.create_organization(db, org_in)


@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all organizations.
    Requires SUPER_ADMIN privileges.
    """
    return await organization_service.get_all_organizations(db)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a specific organization by its UUID.
    Requires SUPER_ADMIN privileges.
    """
    return await organization_service.get_organization(db, org_id)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_in: OrganizationUpdate,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update specific fields of an organization.
    Requires SUPER_ADMIN privileges.
    """
    # We use PATCH here because OrganizationUpdate allows partial updates (exclude_unset=True)
    return await organization_service.update_organization(db, org_id, org_in)


@router.delete("/{org_id}", status_code=status.HTTP_200_OK)
async def deactivate_organization(
    org_id: UUID,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate an organization (Soft Delete).
    Requires SUPER_ADMIN privileges.
    """
    return await organization_service.deactivate_organization(db, org_id)