"""
LamiGo Driver Schemas
Pydantic models for driver data validation
"""

from pydantic import BaseModel
from typing import Optional


class DriverBase(BaseModel):
    """Base schema for driver data."""
    name: str
    phone_number: str
    vehicle_type: str
    is_active: bool = True


class DriverCreate(DriverBase):
    """Schema for creating a new driver."""
    pass


class DriverUpdate(BaseModel):
    """Schema for updating a driver."""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    is_active: Optional[bool] = None


class Driver(DriverBase):
    """Schema for driver response with full details."""
    id: int
    current_location_lat: Optional[float] = None
    current_location_long: Optional[float] = None

    class Config:
        from_attributes = True


class DriverLocation(BaseModel):
    """Schema for driver location update."""
    driver_id: int
    latitude: float
    longitude: float
