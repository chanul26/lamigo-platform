from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# Import Enums
from app.models.enums import PackageStatus, LocationType

# ==========================================
# 1. Nested Output Schema (For the Frontend Dashboard)
# ==========================================
class RecipientSummary(BaseModel):
    """A mini-schema to return nested recipient data without making a second API call."""
    recipient_id: UUID
    phone_number: str
    location_type: Optional[LocationType] = None
    is_location_verified: bool
    gps_lat: Decimal
    gps_lng: Decimal
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 2. Input Schema (POST Requests - The "Upsert" Payload)
# ==========================================
class PackageCreate(BaseModel):
    """
    Notice what is MISSING: No branch_id, no tracking_id, no recipient_id.
    The backend handles all of that securely and automatically!
    """
    # 1. Package Specifics
    weight: Decimal = Field(..., max_digits=6, decimal_places=2, description="Weight in KG")
    is_cod: bool = False
    cod_amount: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    delivery_charge: Decimal = Field(..., max_digits=10, decimal_places=2)

    # 2. Sender Details
    sender_name: str
    sender_phone: Optional[str] = None
    sender_address: Optional[str] = None

    # 3. Recipient Upsert Details (The manager just types this in)
    recipient_name: str
    recipient_phone: str = Field(..., description="Used to lookup or create the recipient")
    address: str
    location_type: Optional[LocationType] = LocationType.HOME
    floor_number: Optional[str] = None
    gps_lat: float
    gps_lng: float

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class PackageUpdate(BaseModel):
    status: Optional[PackageStatus] = None
    package_photo_url: Optional[str] = None
    num_of_attempts: Optional[int] = None

# ==========================================
# 4. Final Output Schema (What the API returns)
# ==========================================
class PackageResponse(BaseModel):
    package_id: UUID
    tracking_id: str
    branch_id: UUID
    status: PackageStatus
    weight: Decimal
    is_cod: bool
    cod_amount: Decimal
    delivery_charge: Decimal
    
    # Snapshot Data
    sender_name: str
    sender_phone: Optional[str]
    recipient_name: str
    address: str
    gps_lat: Decimal
    gps_lng: Decimal

    # The Nested Relationship!
    recipient: Optional[RecipientSummary] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)