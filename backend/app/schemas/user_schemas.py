from pydantic import BaseModel, ConfigDict, Field, EmailStr, AliasChoices
from typing import Optional, Union
from datetime import datetime
from uuid import UUID

# Import your strict Enums
from app.models.enums import UserRole, VehicleType, DriverStatus

# ==========================================
# 1. AUTHENTICATION & LOGIN SCHEMAS
# ==========================================

class TokenRequest(BaseModel):
    """The payload sent by the Flutter/NextJS app to log in."""
    firebase_token: str = Field(..., description="The JWT token from Firebase Auth")

class LoginRequest(BaseModel):
    """Optional payload sent by the frontend immediately after Firebase login."""
    fcm_token: Optional[str] = Field(None, description="Added later for Firebase push notifications")


# ==========================================
# 2. CRUD SCHEMAS (Creating & Updating Users)
# ==========================================

class UserBase(BaseModel):
    phone_number: str = Field(..., description="Phone number used for Firebase Auth")
    full_name: str = Field(..., description="Legal full name as per NIC")
    preferred_name: Optional[str] = None
    nic_number: str = Field(..., description="National Identity Card number")
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    """Payload for onboarding a new Station Manager or Driver"""
    user_id: str = Field(..., description="Firebase UID")
    branch_id: UUID = Field(..., description="The physical hub they are assigned to")
    role: UserRole = Field(..., description="STATION_MANAGER or DRIVER")

class UserUpdate(BaseModel):
    """Payload for editing an existing user. Core identity fields excluded."""
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    fcm_token: Optional[str] = None


# ==========================================
# 3. POLYMORPHIC RESPONSES (What the API returns)
# ==========================================

# --- The Grandparent Identity ---
class AuthIdentityBase(BaseModel):
    role: UserRole
    # Standardizes user_id (Drivers/Managers) and admin_id (SuperAdmins) into 'uid'
    uid: str = Field(validation_alias=AliasChoices("user_id", "admin_id"))

# --- The Parent Mappers ---
class SuperAdminBase(AuthIdentityBase):
    email: EmailStr
    name: str

class BranchStaffBase(AuthIdentityBase):
    branch_id: UUID
    phone_number: str
    full_name: str
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool

# --- The Final Output Models (Pydantic V2) ---
class SuperAdminResponse(SuperAdminBase):
    model_config = ConfigDict(from_attributes=True)

class StationManagerResponse(BranchStaffBase):
    model_config = ConfigDict(from_attributes=True)

class DriverResponse(BranchStaffBase):
    """Includes specific operational data joined from the drivers table."""
    license_number: str
    vehicle_number: str
    vehicle_type: VehicleType
    status: DriverStatus
    commission_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# Use this in your API routes so FastAPI knows it could return any of these three
CurrentUserResponse = Union[SuperAdminResponse, StationManagerResponse, DriverResponse]