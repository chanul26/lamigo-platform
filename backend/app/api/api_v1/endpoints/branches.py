from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# --- The Gatekeepers & Security ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole

# --- Schemas & Services ---
from app.schemas.branch_schemas import BranchCreate, BranchUpdate, BranchResponse
from app.services import branch_service

router = APIRouter()

@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    branch_in: BranchCreate,
    # RBAC Gatekeeper: Strictly Super Admin only
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new physical branch hub under an organization.
    Requires SUPER_ADMIN privileges.
    """
    return await branch_service.create_branch(db, branch_in)


@router.get("/", response_model=List[BranchResponse])
async def get_branches(
    org_id: Optional[UUID] = Query(None, description="Filter branches by their parent organization UUID"),
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all branches, optionally filtered by organization.
    Requires SUPER_ADMIN privileges.
    """
    return await branch_service.get_all_branches(db, org_id)


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: UUID,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a specific branch by its UUID.
    Requires SUPER_ADMIN privileges.
    """
    return await branch_service.get_branch(db, branch_id)


@router.patch("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: UUID,
    branch_in: BranchUpdate,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update specific fields of a branch (e.g., address, GPS coordinates).
    Requires SUPER_ADMIN privileges.
    """
    return await branch_service.update_branch(db, branch_id, branch_in)


@router.delete("/{branch_id}", status_code=status.HTTP_200_OK)
async def delete_branch(
    branch_id: UUID,
    admin_user: dict = Depends(RoleChecker([UserRole.SUPER_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete a branch.
    Requires SUPER_ADMIN privileges.
    """
    return await branch_service.delete_branch(db, branch_id)


@router.get("/my-branch/info", response_model=BranchResponse)
async def get_my_branch(
    current_user: dict = Depends(RoleChecker([UserRole.STATION_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Station Managers can securely fetch their own branch details."""
    branch_id = current_user.get("branch_id")
    if not branch_id:
        raise HTTPException(status_code=400, detail="No branch assigned to this manager.")
    return await branch_service.get_branch(db, branch_id)


@router.patch("/my-branch/info", response_model=BranchResponse)
async def update_my_branch(
    branch_in: BranchUpdate,
    current_user: dict = Depends(RoleChecker([UserRole.STATION_MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Station Managers can securely update their own branch settings (e.g., commission rate)."""
    branch_id = current_user.get("branch_id")
    if not branch_id:
        raise HTTPException(status_code=400, detail="No branch assigned to this manager.")
    return await branch_service.update_branch(db, branch_id, branch_in)


