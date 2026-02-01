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
    vehicle_type: str  # e.g., Bike, Van, Truck
    is_active: bool = True


class DriverCreate(DriverBase):
    """Schema for creating a new driver."""
    pass


class Driver(DriverBase):
    """Schema for driver response with full details."""
    id: int
    current_location_lat: Optional[float] = None
    current_location_long: Optional[float] = None

    class Config:
        from_attributes = True