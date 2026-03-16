from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# 1. Base Schema: Shared properties across all Branch requests/responses
class BranchBase(BaseModel):
    name: str
    address: str
    # Geospatial data for the Simulated Annealing engine
    gps_lat: float = Field(..., description="Latitude coordinate")
    gps_lng: float = Field(..., description="Longitude coordinate")
    # Base fallback for driver payroll (e.g., 0.10 for 10%)
    default_commission_rate: Optional[float] = Field(default=0.00)

# 2. Create Schema: Used for POST requests
class BranchCreate(BranchBase):
    # org_id is required strictly upon creation to link it to the parent tenant
    org_id: UUID

# 3. Update Schema: Used for PATCH/PUT requests
class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    default_commission_rate: Optional[float] = None
    # Notice: org_id is intentionally omitted. A branch cannot change organizations once built.

# 4. Response Schema: What the API returns to the frontend
class BranchResponse(BranchBase):
    branch_id: UUID
    org_id: UUID
    created_at: datetime
    updated_at: datetime

    # Binds the schema strictly to the SQLAlchemy ORM model
    model_config = ConfigDict(from_attributes=True)