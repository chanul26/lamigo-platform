from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LocationType, PackageStatus, PreferenceStatus

# --- Driver DynamoDB ingest (existing) ---
class LocationUpdate(BaseModel):
    lat: float = Field(..., description="Current GPS latitude")
    lng: float = Field(..., description="Current GPS longitude")
    status: str = Field(..., description="Driver's current status (e.g., ON_TRIP, AVAILABLE)")
    trip_id: Optional[UUID] = None
    task_id: Optional[UUID] = None


# --- Public customer portal (no auth) ---
class PublicRecipientOut(BaseModel):
    """Recipient row safe for anonymous tracking pages."""

    recipient_id: UUID
    name: str
    phone_number: str
    address: str
    location_type: Optional[LocationType] = None
    floor_number: Optional[str] = None
    is_location_verified: bool
    gps_lat: Decimal
    gps_lng: Decimal

    model_config = ConfigDict(from_attributes=True)


class PublicCurrentTaskOut(BaseModel):
    """Active stop on the route when the package is out for delivery."""

    estimated_arrival_time: Optional[datetime] = None
    sequence_number: int


class PublicTrackingDetailResponse(BaseModel):
    """Package + nested recipient + optional live task snippet."""

    package_id: UUID
    tracking_id: str
    branch_id: UUID
    status: PackageStatus
    weight: Decimal
    is_cod: bool
    cod_amount: Decimal
    delivery_charge: Decimal
    sender_name: str
    sender_phone: Optional[str] = None
    recipient_name: str
    address: str
    gps_lat: Decimal
    gps_lng: Decimal
    num_of_attempts: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    recipient: Optional[PublicRecipientOut] = None
    current_task: Optional[PublicCurrentTaskOut] = None

    model_config = ConfigDict(from_attributes=True)


class PublicRecipientLocationUpdate(BaseModel):
    """Anonymous customer pin drop / location correction."""

    gps_lat: float = Field(..., description="New latitude for the delivery address")
    gps_lng: float = Field(..., description="New longitude for the delivery address")


class PublicRecipientLocationResponse(BaseModel):
    message: str
    recipient: PublicRecipientOut


class PublicInstructionCreate(BaseModel):
    """Customer-added note for the active delivery stop."""

    content_text: str = Field(..., min_length=1, description="Instruction text for the driver")


class PublicInstructionResponse(BaseModel):
    message: str
    instruction_id: UUID
    task_id: UUID


class PublicPreferenceCreate(BaseModel):
    """Preferred days for this package."""
    target_dates: list[date] = Field(..., description="List of calendar days (YYYY-MM-DD)")
    status: PreferenceStatus = Field(default=PreferenceStatus.AVAILABLE)

class PublicPreferenceResponse(BaseModel):
    message: str

class PublicRejectResponse(BaseModel):
    """Response when a customer rejects a scheduled delivery."""
    message: str