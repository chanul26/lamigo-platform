from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.enums import PaymentMethod

class SettlementCreate(BaseModel):
    """Payload sent by the Station Manager to process a payout."""
    driver_id: str = Field(..., description="Firebase UID of the driver being paid")
    amount_paid: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="Must be greater than 0")
    payment_method: PaymentMethod
    reference_note: Optional[str] = Field(None, description="Cheque number or bank transfer ID")

class SettlementResponse(BaseModel):
    """The formatted output for a payout record."""
    settlement_id: UUID
    driver_id: str
    processed_by: str
    amount_paid: Decimal
    balance_at_settlement: Decimal
    payment_method: PaymentMethod
    reference_note: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)