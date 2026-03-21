from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# Import your Enum
from app.models.enums import LocationType

# 1. Base Schema: Shared properties across all Recipient requests/responses
class RecipientBase(BaseModel):
    name: str = Field(..., description="Full name of the recipient")
    phone_number: str = Field(..., description="Contact phone number")
    address: str = Field(..., description="Full street address")
    location_type: Optional[LocationType] = Field(default=LocationType.HOME)
    floor_number: Optional[str] = Field(default=None, description="Crucial for APARTMENT or OFFICE")
    
    # Strictly typed as floats for JSON transport
    gps_lat: float = Field(..., description="Latitude coordinate")
    gps_lng: float = Field(..., description="Longitude coordinate")

# 2. Update Schema: Used for PATCH/PUT requests
# All fields are optional to allow partial updates (e.g., just updating the phone number)
class RecipientUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    location_type: Optional[LocationType] = None
    floor_number: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    is_location_verified: Optional[bool] = None

# 3. Response Schema: What the API returns to the frontend
class RecipientResponse(RecipientBase):
    recipient_id: UUID
    is_location_verified: bool
    created_at: datetime
    updated_at: datetime

    # Binds the schema strictly to the SQLAlchemy ORM model (Pydantic V2 syntax)
    model_config = ConfigDict(from_attributes=True)