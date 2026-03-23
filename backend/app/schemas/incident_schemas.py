from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.enums import IncidentType, IncidentStatus, ResponseType, ResponseStatus

# ==========================================
# 1. Main Incident Schemas
# ==========================================
class IncidentCreate(BaseModel):
    """Payload sent by the driver. Notice driver_id is missing for security."""
    trip_id: UUID = Field(..., description="The trip during which the incident occurred")
    type: IncidentType = Field(..., description="Type of emergency (e.g., ACCIDENT, VEHICLE_BREAKDOWN)")
    reported_at_lat: float = Field(..., description="Latitude of the incident")
    reported_at_lng: float = Field(..., description="Longitude of the incident")
    description: Optional[str] = Field(None, description="Optional details provided by the driver")

class IncidentUpdate(BaseModel):
    """Payload sent by the manager. Notice handled_by is missing for security."""
    status: IncidentStatus
    description: Optional[str] = None

class IncidentResponse(BaseModel):
    """The fully formatted database record returned to the frontend."""
    incident_id: UUID
    trip_id: UUID
    driver_id: str
    type: IncidentType
    reported_at_lat: float
    reported_at_lng: float
    description: Optional[str]
    status: IncidentStatus
    handled_by: Optional[str]
    handled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 2. Incident Response Assignments (Rescue Missions)
# ==========================================
class AssignmentCreate(BaseModel):
    """Manager dispatches a backup driver."""
    backup_driver_id: str = Field(..., description="Firebase UID of the rescue driver")
    type: ResponseType = Field(..., description="HELP, PACKAGE_RESCUE, or MECHANICAL_AID")

class AssignmentUpdate(BaseModel):
    """Rescue driver updates their mission status."""
    status: ResponseStatus = Field(..., description="E.g., ON_SITE or COMPLETED")

class AssignmentResponse(BaseModel):
    assignment_id: UUID
    incident_id: UUID
    backup_driver_id: str
    assigned_by: str
    type: ResponseType
    status: ResponseStatus
    dispatched_at: datetime
    arrived_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)