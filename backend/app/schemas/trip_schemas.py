from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# Import your Enums from the existing models
from app.models.enums import TripStatus

# ==========================================
# 1. Base Schema (Shared fields)
# ==========================================
class TripBase(BaseModel):
    branch_id: UUID = Field(..., description="The physical branch this trip originates from")
    driver_id: Optional[str] = Field(None, description="Assigned driver (can be null for DRAFT trips)")
    scheduled_start_time: Optional[datetime] = Field(None, description="When the manager expects the trip to leave")

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class TripCreate(TripBase):
    """
    Payload for creating a new Trip. 
    Notice we don't include status, counts, or actual times here because 
    the backend automatically sets them to defaults (DRAFT, 0, etc.)
    """
    pass

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class TripUpdate(BaseModel):
    """
    Payload for modifying a trip (e.g., assigning a driver later, or updating status).
    All fields are optional to allow partial updates.
    """
    driver_id: Optional[str] = None
    status: Optional[TripStatus] = None
    scheduled_start_time: Optional[datetime] = None
    
    # These are typically updated by the system, but included in schema for manual manager overrides
    actual_start_time: Optional[datetime] = None
    actual_return_time: Optional[datetime] = None

# ==========================================
# 4. Response Schema (Output to Frontend)
# ==========================================
class TripResponse(TripBase):
    """
    The exact JSON payload the frontend receives.
    """
    trip_id: UUID
    status: TripStatus
    
    # Aggregated Counters (Updated later when DeliveryTasks are attached)
    total_tasks_count: int
    delivered_count: int
    total_weight: float
    total_cod_to_collect: float
    
    # Timestamps
    actual_start_time: Optional[datetime]
    estimated_return_time_scheduled: Optional[datetime]
    estimated_return_time_actual: Optional[datetime]
    actual_return_time: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime

    # Tells Pydantic to read directly from your SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)