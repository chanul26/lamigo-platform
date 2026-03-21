from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# Import the Enums from your database models
from app.models.enums import IncidentType, IncidentStatus

# ==========================================
# 1. Base Schema (Shared fields)
# ==========================================
class IncidentBase(BaseModel):
    trip_id: UUID = Field(..., description="The trip during which the incident occurred")
    driver_id: str = Field(..., description="The driver reporting the incident")
    type: IncidentType = Field(..., description="Type of emergency (e.g., ACCIDENT, VEHICLE_BREAKDOWN)")
    
    # Precise GPS coordinates of where the SOS button was pressed
    reported_at_lat: float = Field(..., description="Latitude of the incident")
    reported_at_lng: float = Field(..., description="Longitude of the incident")
    
    description: Optional[str] = Field(None, description="Optional details provided by the driver or manager")

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class IncidentCreate(IncidentBase):
    """
    Payload sent by the Driver App when hitting the SOS button.
    Status defaults to REPORTED in the database.
    """
    pass

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class IncidentUpdate(BaseModel):
    """
    Payload used by Station Managers to update the situation.
    All fields are optional to allow partial updates.
    """
    status: Optional[IncidentStatus] = None
    description: Optional[str] = None
    
    # When a manager takes responsibility for the ticket
    handled_by: Optional[str] = Field(None, description="User ID of the manager handling this")
    handled_at: Optional[datetime] = None

# ==========================================
# 4. Response Schema (Output to Frontend)
# ==========================================
class IncidentResponse(IncidentBase):
    """
    The exact JSON payload returned to the frontend.
    """
    incident_id: UUID
    status: IncidentStatus
    
    handled_by: Optional[str]
    handled_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime

    # Binds the schema strictly to the SQLAlchemy ORM model
    model_config = ConfigDict(from_attributes=True)