from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class LocationUpdate(BaseModel):
    lat: float = Field(..., description="Current GPS latitude")
    lng: float = Field(..., description="Current GPS longitude")
    status: str = Field(..., description="Driver's current status (e.g., ON_TRIP, AVAILABLE)")
    trip_id: Optional[UUID] = None
    task_id: Optional[UUID] = None