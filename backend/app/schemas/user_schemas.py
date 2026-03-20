from pydantic import BaseModel, ConfigDict, Field, EmailStr, AliasChoices
from typing import Optional, Union
from datetime import datetime
from uuid import UUID

# Import the enums you defined in your database
from app.models.enums import UserRole, VehicleType, DriverStatus

# ==========================================
# 1. INTAKE SCHEMAS (Requests)
# ==========================================

class TokenRequest(BaseModel):
    """The payload sent by the Flutter/NextJS app to log in."""
    firebase_token: str = Field(..., description="The JWT token from Firebase Auth")

class LoginRequest(BaseModel):
    """
    Optional payload sent by the frontend immediately after Firebase login.
    """
    # --- ADDED LATER: Changed from device_id to fcm_token for push notifications ---
    fcm_token: Optional[str] = Field(None, description="Added later for Firebase push notifications")

# ==========================================
# 2. CRUD SCHEMAS (Creating & Updating Users)
# ==========================================

class UserBase(BaseModel):
    """Base attributes required for any branch staff (Manager or Driver)."""
    phone_number: str = Field(..., description="Phone number used for Firebase Auth")
    full_name: str = Field(..., description="Legal full name as per NIC")
    preferred_name: Optional[str] = None
    nic_number: str = Field(..., description="National Identity Card number")
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    """
    Payload for onboarding a new Station Manager or Driver.
    Used strictly by Super Admins or Station Managers.
    """
    # --- CORE LINKING: Enforcing relationship to Firebase and physical hub ---
    user_id: str = Field(..., description="Firebase UID")
    # Super Admins must send it, but Station Managers have it auto-injected.
    branch_id: Optional[UUID] = Field(None, description="The physical hub they are assigned to")
    role: UserRole = Field(..., description="STATION_MANAGER or DRIVER")


class DriverCreate(UserCreate):
    """
    Payload for onboarding a new Driver.
    Inherits all base identity requirements (NIC, phone, branch, UID) from UserCreate,
    and adds the specific vehicle/license data needed for the drivers table.
    """
    license_number: str = Field(..., description="Official Driving License ID")
    vehicle_number: str = Field(..., description="License plate number (e.g., WP CAM-1234)")
    vehicle_type: VehicleType = Field(..., description="MOTORCYCLE, THREE_WHEEL, or LORRY")
    commission_rate: Optional[float] = Field(
        None, 
        description="Override Rate. If left null, backend uses Branch default."
    )

class UserUpdate(BaseModel):
    """
    Payload for editing an existing user.
    """
    # --- SECURITY REASONING: Intentionally excluding user_id, nic_number, and role from updates ---
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    fcm_token: Optional[str] = None

class DriverUpdate(UserUpdate):
    """
    Payload for updating an existing Driver.
    Inherits base updates (phone, name, is_active) and adds driver-specific fields.
    Intentionally excludes driver_id to prevent database relationship breaks.
    """
    license_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    commission_rate: Optional[float] = None
    status: Optional[DriverStatus] = None

# ==========================================
# 3. OUTBOUND HIERARCHY (Responses)
# ==========================================

# --- Level 1: The Grandparent (Identity) ---
class AuthIdentityBase(BaseModel):
    """The absolute root for anyone who logs in."""
    role: UserRole
    # MAGIC: Tells Pydantic to look for 'user_id' OR 'admin_id' in the database,
    # but it will always output as 'uid' in the final JSON for the frontend.
    uid: str = Field(validation_alias=AliasChoices("user_id", "admin_id"))

# --- Level 2: The Parents (Database Mappers) ---
class SuperAdminBase(AuthIdentityBase):
    """Maps to the super_admins table."""
    email: EmailStr
    name: str

class BranchStaffBase(AuthIdentityBase):
    """Maps to the users table (Shared DNA for Managers and Drivers)."""
    branch_id: UUID
    phone_number: str
    full_name: str
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool

# --- Level 3: The Children (Final API Responses) ---
class SuperAdminResponse(SuperAdminBase):
    """Final output profile for Swagger/Admin Dashboard."""
    # --- UPGRADED: Pydantic V2 syntax ---
    model_config = ConfigDict(from_attributes=True) 

class StationManagerResponse(BranchStaffBase):
    """Final output profile for the NextJS Manager App."""
    model_config = ConfigDict(from_attributes=True)

class DriverResponse(BranchStaffBase):
    """Adds the specific operational data from the drivers table for the Flutter App."""
    license_number: str
    vehicle_number: str
    vehicle_type: VehicleType
    status: DriverStatus
    commission_rate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 4. POLYMORPHIC EXPORTS
# ==========================================

# Use this in your API routes so FastAPI knows it could return any of these three
CurrentUserResponse = Union[SuperAdminResponse, StationManagerResponse, DriverResponse]