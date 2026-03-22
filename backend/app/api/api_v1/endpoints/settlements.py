from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole
from app.schemas.settlement_schemas import SettlementCreate, SettlementResponse
from app.services import settlement_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.post("/", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def process_driver_payout(
    payload: SettlementCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Station Manager processes a payout for a driver in their branch."""
    manager_id = current_user.get("user_id")
    manager_branch_id = current_user.get("branch_id")
    
    return await settlement_service.process_payout(db, payload, manager_id, manager_branch_id)


@router.get("/", response_model=List[SettlementResponse])
async def list_settlements(
    driver_id_filter: Optional[str] = Query(None, description="Filter by a specific driver"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Audit trail of payments. Securely scopes data based on user role."""
    user_role = current_user.get("role")
    
    secure_branch_id = None
    secure_driver_id = driver_id_filter

    if user_role == UserRole.DRIVER:
        # Drivers can ONLY see their own payouts, completely ignoring any filter they try to pass
        secure_driver_id = current_user.get("user_id")
        
    elif user_role == UserRole.STATION_MANAGER:
        # Managers can only see payouts for drivers inside their own branch
        secure_branch_id = current_user.get("branch_id")

    return await settlement_service.get_settlements(
        db=db, 
        driver_id=secure_driver_id, 
        branch_id=secure_branch_id
    )