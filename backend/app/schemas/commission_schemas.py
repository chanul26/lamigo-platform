from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

# ==========================================
# 1. Base Schema
# ==========================================
class CommissionBase(BaseModel):
    trip_id: UUID = Field(..., description="The completed trip this commission is for")
    driver_id: str = Field(..., description="The driver who earned this commission")
    amount_earned: float = Field(..., description="Calculated commission amount (e.g., 500.00 LKR)")

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class CommissionCreate(CommissionBase):
    """Payload for logging a new driver commission."""
    pass

# Note: No CommissionUpdate schema. Financial ledgers are strictly immutable!

# ==========================================
# 3. Response Schema (Output to Frontend)
# ==========================================
class CommissionResponse(CommissionBase):
    commission_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)