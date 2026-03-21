from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, PackageStatus
from app.schemas.package_schemas import PackageCreate, PackageUpdate, PackageResponse
from app.services import package_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_new_package(
    payload: PackageCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a package, auto-generates tracking ID, and securely handles the Recipient Upsert.
    """
    # SECURE BRANCH ASSIGNMENT (No IDOR vulnerabilities!)
    branch_id = current_user.get("branch_id")
    
    if not branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your profile does not have an assigned branch. Packages must be created by Station Managers."
        )

    return await package_service.create_package_with_recipient(
        db=db, 
        package_data=payload, 
        branch_id=branch_id
    )


@router.get("/", response_model=List[PackageResponse])
async def get_packages(
    branch_id: Optional[UUID] = Query(None, description="Filter packages by branch"),
    package_status: Optional[PackageStatus] = Query(None, description="Filter by status (e.g., TO_BE_DELIVERED)"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # --- SECURITY OVERRIDE: Prevent cross-branch data leakage ---
    user_role = current_user.get("role")
    
    # Force Station Managers and Drivers to ONLY see their own branch's data
    if user_role in [UserRole.STATION_MANAGER, UserRole.DRIVER]:
        secure_user_branch = current_user.get("branch_id")
        
        if not secure_user_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Your profile does not have an assigned branch to view packages."
            )
            
        # CRITICAL FIX: We overwrite the 'branch_id' variable with their secure token value.
        # This completely ignores whatever they tried to send in the URL.
        branch_id = secure_user_branch

    # If the user is a SUPER_ADMIN, they bypass the if-statement above and can see everything.
    return await package_service.get_all_packages(db, branch_id=branch_id, package_status=package_status)


@router.get("/", response_model=List[PackageResponse])
async def get_packages(
    branch_id: Optional[UUID] = Query(None, description="Filter packages by branch"),
    package_status: Optional[PackageStatus] = Query(None, description="Filter by status (e.g., TO_BE_DELIVERED)"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # --- SECURITY OVERRIDE: Prevent cross-branch data leakage ---
    user_role = current_user.get("role")
    
    # 1. Force Station Managers and Drivers to ONLY see their own branch's data
    if user_role in [UserRole.STATION_MANAGER, UserRole.DRIVER]:
        secure_user_branch = current_user.get("branch_id")
        
        if not secure_user_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Your profile does not have an assigned branch to view packages."
            )
            
        # CRITICAL: We overwrite the 'branch_id' variable with their secure token value.
        # This completely ignores whatever they tried to send in the URL.
        branch_id = secure_user_branch

    # 2. If the user is a SUPER_ADMIN, they bypass the if-statement above. 
    # This allows Admins to leave branch_id blank to see all company packages, 
    # or pass a specific branch_id in the URL to filter.
    
    return await package_service.get_all_packages(db, branch_id=branch_id, package_status=package_status)

@router.patch("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: UUID,
    payload: PackageUpdate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch the existing package FIRST to check who owns it
    existing_package = await package_service.get_package(db, package_id)
    
    # 2. SECURITY OVERRIDE: Prevent cross-branch tampering (Write-Level IDOR)
    user_role = current_user.get("role")
    
    if user_role == UserRole.STATION_MANAGER:
        secure_user_branch = current_user.get("branch_id")
        
        # If the package's branch does not match the manager's secure branch token, block them!
        if existing_package.branch_id != secure_user_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You cannot update packages that belong to another branch."
            )

    # 3. If the security check passes (or if they are a SUPER_ADMIN), proceed with the update
    return await package_service.update_package(db, package_id, payload)