from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, PackageStatus
from app.schemas.package_schemas import PackageCreate, PackageUpdate, PackageResponse
from app.services import package_service, communication_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_new_package(
    payload: PackageCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a package, auto-generates tracking ID, and fires the Customer SMS.
    """
    branch_id = current_user.get("branch_id")
    
    if not branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your profile does not have an assigned branch. Packages must be created by Station Managers."
        )

    # 1. Create the package in PostgreSQL
    package = await package_service.create_package_with_recipient(
        db=db, 
        package_data=payload, 
        branch_id=branch_id
    )
    
    # 2. Auto-Trigger the 2-in-1 SMS Link
    tracking_url = f"http://localhost:3001/track/{package['tracking_id']}"
    sms_message = f"LamiGo: Your package has arrived at our hub! Please confirm your availability and drop your GPS pin here: {tracking_url}"
    
    # Send the SMS in the background
    background_tasks.add_task(
        communication_service.log_sms,
        package_id=str(package['package_id']),
        recipient_phone=payload.recipient_phone,
        message_body=sms_message,
        category="DELIVERY_UPDATE",
        status="QUEUED"
    )

    return package


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
        branch_id = secure_user_branch

    # 2. If the user is a SUPER_ADMIN, they bypass the if-statement above. 
    return await package_service.get_all_packages(db, branch_id=branch_id, package_status=package_status)


@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Fetches a single package by ID (with Read-Level IDOR protection)."""
    package = await package_service.get_package(db, package_id)
    
    user_role = current_user.get("role")
    if user_role in [UserRole.STATION_MANAGER, UserRole.DRIVER]:
        # Dictionary syntax used because package is now a dict from the service
        if package.get("branch_id") != current_user.get("branch_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You cannot view packages that belong to another branch."
            )
            
    return package


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
        
        # Dictionary syntax used because existing_package is now a dict
        if existing_package.get("branch_id") != secure_user_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You cannot update packages that belong to another branch."
            )

    # 3. If the security check passes, proceed with the update
    return await package_service.update_package(db, package_id, payload)