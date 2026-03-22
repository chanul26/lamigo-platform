from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import DriverSettlement, DriverFinancialProfile, User
from app.schemas.settlement_schemas import SettlementCreate

# --- THE DICTIONARY RULE ENFORCER ---
def _settlement_to_dict(settlement: DriverSettlement) -> dict:
    data = settlement.__dict__.copy()
    data.pop('_sa_instance_state', None)
    return data
# ------------------------------------

async def process_payout(db: AsyncSession, payload: SettlementCreate, manager_id: str, manager_branch_id: UUID) -> dict:
    """Processes a payment, updates the driver's lifetime financials, and logs the settlement."""
    
    # 1. ANTI-IDOR: Ensure the driver belongs to the manager's branch
    driver_user_result = await db.execute(select(User).where(User.user_id == payload.driver_id))
    driver_user = driver_user_result.scalars().first()
    
    if not driver_user or driver_user.branch_id != manager_branch_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: You can only process settlements for drivers in your assigned branch."
        )

    # 2. Fetch the Financial Profile with a ROW LOCK (CRITICAL FOR FINANCE)
    fin_result = await db.execute(
        select(DriverFinancialProfile)
        .where(DriverFinancialProfile.driver_id == payload.driver_id)
        .with_for_update() # Locks the row until db.commit()
    )
    profile = fin_result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Financial profile not found. The driver may not have completed any trips yet."
        )

    # 3. Validate sufficient funds
    if payload.amount_paid > profile.current_payable_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot pay more than the outstanding balance (Rs. {profile.current_payable_balance})."
        )

    # 4. Calculate new balances
    new_balance = profile.current_payable_balance - payload.amount_paid
    
    # 5. Create the immutable Settlement Ledger record
    settlement = DriverSettlement(
        driver_id=payload.driver_id,
        processed_by=manager_id,
        amount_paid=payload.amount_paid,
        balance_at_settlement=new_balance, # Snapshot of what was owed right after this payment
        payment_method=payload.payment_method,
        reference_note=payload.reference_note
    )
    db.add(settlement)

    # 6. Update the Driver's Financial Profile
    profile.current_payable_balance = new_balance
    profile.total_lifetime_settled += payload.amount_paid
    profile.last_settlement_date = datetime.now(timezone.utc)

    # 7. Commit the transaction (Releases the row lock)
    await db.commit()
    await db.refresh(settlement)

    return _settlement_to_dict(settlement)

async def get_settlements(
    db: AsyncSession, 
    driver_id: Optional[str] = None, 
    branch_id: Optional[UUID] = None
) -> List[dict]:
    """Fetches a list of settlements. Securely filtered by the router."""
    
    query = select(DriverSettlement)
    
    # If filtering by branch, we must join the User table to check where the driver works
    if branch_id:
        query = query.join(User, DriverSettlement.driver_id == User.user_id).where(User.branch_id == branch_id)
        
    if driver_id:
        query = query.where(DriverSettlement.driver_id == driver_id)
        
    query = query.order_by(DriverSettlement.created_at.desc())
    result = await db.execute(query)
    
    return [_settlement_to_dict(s) for s in result.scalars().all()]