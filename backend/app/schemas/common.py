"""
LamiGo Common Schemas
Shared Pydantic models used across the application
"""

from pydantic import BaseModel
from typing import Optional


class StationBase(BaseModel):
    """Base schema for station data."""
    name: str
    location_code: str
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
    package_count: int = 0

    class Config:
        from_attributes = True


class LocationSchema(BaseModel):
    """Schema for geographic location."""
    latitude: float
    longitude: float
    address: Optional[str] = None


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    page: int = 1
    page_size: int = 20


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
    status: str = "success"
