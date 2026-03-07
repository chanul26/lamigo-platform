from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole, VehicleType, DriverStatus

class SuperAdminProfile(BaseModel):
    admin_id: str
    email: str
    name: str
    role: UserRole
    last_access_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    user_id: str
    phone_number: str
    role: UserRole
    full_name: str
    preferred_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DriverProfile(BaseModel):
    user_id: str
    phone_number: str
    role: UserRole
    full_name: str
    preferred_name: Optional[str] = None
    is_active: bool
    license_number: str
    vehicle_number: str
    vehicle_type: VehicleType
    status: DriverStatus
    created_at: datetime

    class Config:
        from_attributes = True