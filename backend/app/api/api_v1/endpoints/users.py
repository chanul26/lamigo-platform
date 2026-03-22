from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.api import deps
from app.models.enums import UserRole
from app.schemas.user_schemas import (
    UserCreate, 
    UserUpdate, 
    DriverCreate, 
    DriverUpdate,
    StationManagerResponse,
    DriverResponse,
    CurrentUserResponse
)
from app.services import user_service

router = APIRouter()

# ==========================================
# 1. ONBOARDING (POST)
# ==========================================

@router.post("/managers", response_model=StationManagerResponse, status_code=status.HTTP_201_CREATED)
async def create_manager(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db),
    _ = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN]))
):
    """Onboard a new Station Manager and assign them to a branch."""
    if user_in.role != UserRole.STATION_MANAGER:
        raise HTTPException(status_code=400, detail="Use the /drivers endpoint to create drivers.")
    
    # SECURITY: Super Admins don't belong to a branch, so they MUST explicitly provide one for the new manager
    if not user_in.branch_id:
        raise HTTPException(status_code=400, detail="Super Admins must specify a branch_id when creating a manager.")
    
    return await user_service.create_user(db, user_in)


@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_in: DriverCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: dict = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
):
    """Onboard a new Driver, linking their identity and vehicle details simultaneously."""
    if driver_in.role != UserRole.DRIVER:
        raise HTTPException(status_code=400, detail="Role must be DRIVER.")
    
    # --- THE SECURITY OVERRIDE ---
    # Safely extract the ID whether they are a Manager (user_id) or a Super Admin (admin_id)
    current_uid = current_user.get("user_id") or current_user.get("admin_id")
    
    # Since deps.py already fetched the profile, we can read the dictionary directly!
    if current_user.get("role") == UserRole.STATION_MANAGER:
        # Force the driver into the manager's exact hub, ignoring anything the frontend sent
        driver_in.branch_id = current_user.get("branch_id")
        
    elif current_user.get("role") == UserRole.SUPER_ADMIN:
        # Super Admins must provide it manually
        if not driver_in.branch_id:
            raise HTTPException(status_code=400, detail="Super Admins must specify a branch_id in the payload.")
    
    return await user_service.create_driver(db, driver_in, created_by_id=current_uid)


# ==========================================
# 2. FETCHING (GET)
# ==========================================

@router.get("/", response_model=List[CurrentUserResponse])
async def get_users(
    branch_id: UUID,
    role: Optional[UserRole] = None,
    db: AsyncSession = Depends(deps.get_db),
    _ = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
):
    """
    Fetch staff for a specific branch. 
    Uses the polymorphic 'CurrentUserResponse' so Swagger dynamically shows 
    either Manager or Driver data depending on who it finds.
    """
    return await user_service.get_users_by_branch(db, branch_id, role)


@router.get("/{uid}", response_model=CurrentUserResponse)
async def get_user(
    uid: str,
    db: AsyncSession = Depends(deps.get_db),
    _ = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
):
    """Fetch a specific user by their Firebase UID."""
    return await user_service.get_user(db, uid)


# ==========================================
# 3. UPDATING & SOFT-DELETING (PATCH)
# ==========================================

@router.patch("/managers/{uid}", response_model=StationManagerResponse)
async def update_manager(
    uid: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    # SECURITY: Only Super Admins can edit or fire Station Managers
    _ = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN]))
):
    """Update a Station Manager's profile, or fire them by sending is_active=False."""
    return await user_service.update_user(db, uid, user_in)


@router.patch("/drivers/{uid}", response_model=DriverResponse)
async def update_driver(
    uid: str,
    driver_in: DriverUpdate,
    db: AsyncSession = Depends(deps.get_db),
    # SECURITY: Managers can update or fire their own drivers
    _ = Depends(deps.RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
):
    """Update a Driver's identity or operational details (vehicle, commission)."""
    return await user_service.update_driver(db, uid, driver_in)