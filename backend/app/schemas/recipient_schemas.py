from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.enums import LocationType

class RecipientBase(BaseModel):
    name: str = Field(..., max_length=100)
    phone_number: str = Field(..., max_length=20)
    address: str
    location_type: LocationType = LocationType.HOME
    floor_number: Optional[str] = Field(None, max_length=10)
    is_location_verified: bool = False
    gps_lat: float
    gps_lng: float

class RecipientCreate(RecipientBase):
    pass

class RecipientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    location_type: Optional[LocationType] = None
    floor_number: Optional[str] = Field(None, max_length=10)
    is_location_verified: Optional[bool] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None

class RecipientResponse(RecipientBase):
    recipient_id: UUID
    created_at: datetime
    updated_at: datetime

    # Using Pydantic V2 syntax as requested
    model_config = ConfigDict(from_attributes=True)