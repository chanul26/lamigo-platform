from pydantic import BaseModel, EmailStr, Field, AliasChoices
from typing import Optional, Union
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
    Used for storing device tokens for push notifications or analytics.
    """
    device_id: Optional[str] = None


# ==========================================
# 2. OUTBOUND HIERARCHY (Responses)
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

    class Config:
        from_attributes = True  # Allows reading the SQLAlchemy model


class StationManagerResponse(BranchStaffBase):
    """Final output profile for the NextJS Manager App."""

    class Config:
        from_attributes = True


class DriverResponse(BranchStaffBase):
    """Adds the specific operational data from the drivers table for the Flutter App."""

    license_number: str
    vehicle_number: str
    vehicle_type: VehicleType
    status: DriverStatus
    commission_rate: Optional[float] = None

    class Config:
        from_attributes = True


# ==========================================
# 3. POLYMORPHIC EXPORTS
# ==========================================

# Use this in your API routes so FastAPI knows it could return any of these three
CurrentUserResponse = Union[SuperAdminResponse, StationManagerResponse, DriverResponse]
