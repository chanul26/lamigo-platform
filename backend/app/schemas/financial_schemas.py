from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ==========================================
# 1. Response Schema (Read-Only)
# ==========================================
class FinancialProfileResponse(BaseModel):
    """Output schema for the driver's financial ledger."""
    driver_id: str
    current_payable_balance: Decimal
    total_lifetime_earnings: Decimal
    total_lifetime_settled: Decimal
    last_settlement_date: Optional[datetime] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)