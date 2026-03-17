from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.enums import PackageStatus

class PackageBase(BaseModel):
    sender_name: str = Field(..., max_length=100)
    sender_phone: Optional[str] = Field(None, max_length=20)
    sender_address: Optional[str] = None
    package_photo_url: Optional[str] = None
    weight: float = Field(..., gt=0, description="Weight in kg")
    is_cod: bool = False
    cod_amount: float = 0.00
    delivery_charge: float

class PackageCreate(PackageBase):
    """Payload required to create a new package."""
    recipient_id: UUID
    branch_id: UUID

class PackageUpdate(BaseModel):
    """Allows partial updates for managers/drivers."""
    status: Optional[PackageStatus] = None
    package_photo_url: Optional[str] = None
    is_cod: Optional[bool] = None
    cod_amount: Optional[float] = None
    delivery_charge: Optional[float] = None
    num_of_attempts: Optional[int] = None

class PackageResponse(PackageBase):
    """The full data structure returned to the frontend."""
    package_id: UUID
    tracking_id: str
    recipient_id: UUID
    branch_id: UUID
    status: PackageStatus
    num_of_attempts: int

    # Snapshot data from the Recipient
    recipient_name: str
    address: str
    gps_lat: float
    gps_lng: float

    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
