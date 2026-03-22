from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.enums import IncidentType, IncidentStatus

class IncidentBase(BaseModel):
    trip_id: UUID = Field(..., description="The trip during which the incident occurred")
    driver_id: str = Field(..., description="The driver reporting the incident")
    type: IncidentType = Field(..., description="Type of emergency (e.g., ACCIDENT, VEHICLE_BREAKDOWN)")
    reported_at_lat: float = Field(..., description="Latitude of the incident")
    reported_at_lng: float = Field(..., description="Longitude of the incident")
    description: Optional[str] = Field(None, description="Optional details provided by the driver or manager")

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    description: Optional[str] = None
    handled_by: Optional[str] = Field(None, description="User ID of the manager handling this")
    handled_at: Optional[datetime] = None

class IncidentResponse(IncidentBase):
    incident_id: UUID
    status: IncidentStatus
    handled_by: Optional[str]
    handled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)