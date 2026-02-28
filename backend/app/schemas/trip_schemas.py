"""
LamiGo Trip/Package Schemas
Pydantic models for trip and package data validation
"""

from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime


PackageStatus = Literal["Pending", "In Transit", "Delivered", "Returned"]


class PackageBase(BaseModel):
    """Base schema for package data."""
    tracking_number: str
    recipient_name: str
    delivery_address: str
    status: PackageStatus = "Pending"


class PackageCreate(PackageBase):
    """Schema for creating a new package."""
    station_id: Optional[int] = None


class Package(PackageBase):
    """Schema for package response with full details."""
    id: int
    assigned_driver_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TripBase(BaseModel):
    """Base schema for delivery trip data."""
    driver_id: int
    station_id: int
    scheduled_date: datetime


class TripCreate(TripBase):
    """Schema for creating a new trip."""
    package_ids: List[int] = []


class Trip(TripBase):
    """Schema for trip response with full details."""
    id: int
    status: str = "Planned"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    packages: List[Package] = []

    class Config:
        from_attributes = True


class TripOptimizationRequest(BaseModel):
    """Schema for trip optimization request."""
    package_ids: List[int]
    driver_id: Optional[int] = None


class TripOptimizationResponse(BaseModel):
    """Schema for trip optimization response."""
    status: str
    message: str
    package_ids: List[int]
    optimized_order: List[int]
    estimated_time_minutes: int
    total_distance_km: float
