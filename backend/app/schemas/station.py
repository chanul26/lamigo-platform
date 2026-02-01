"""
LamiGo Station Schemas
Pydantic models for station/hub data validation
"""

from pydantic import BaseModel
from typing import Optional


class StationBase(BaseModel):
    """Base schema for station data."""
    name: str
    location_code: str  # e.g., COL-01 for Colombo Central
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StationCreate(StationBase):
    """Schema for creating a new station."""
    pass


class Station(StationBase):
    """Schema for station response with full details."""
    id: int
    is_active: bool = True
    package_count: int = 0  # Number of packages at station

    class Config:
        from_attributes = True