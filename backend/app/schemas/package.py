"""
LamiGo Package Schemas
Pydantic models for package data validation
"""

from pydantic import BaseModel
from typing import Optional, Literal
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
        from_attributes = True  # Allows compatibility with ORMs like SQLAlchemy