from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole
from app.schemas.package_schemas import PackageCreate, PackageUpdate, PackageResponse
from app.services import package_service

router = APIRouter()

require_manager_or_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER])


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_in: PackageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Create a new package and generate a tracking ID."""
    return await package_service.create_package(db, package_in)


@router.get("/", response_model=List[PackageResponse])
async def read_packages(
    branch_id: Optional[UUID] = Query(None, description="Filter packages by a specific Branch ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Retrieve all packages, optionally filtered by branch."""
    return await package_service.get_all_packages(db, branch_id)


@router.get("/{package_id}", response_model=PackageResponse)
async def read_package(
    package_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Get a specific package by its exact ID."""
    return await package_service.get_package(db, package_id)


@router.put("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: UUID,
    package_in: PackageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_manager_or_admin)
):
    """Update a package's status or details."""
    return await package_service.update_package(db, package_id, package_in)
