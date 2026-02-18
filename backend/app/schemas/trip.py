"""
LamiGo Trip Schemas
Pydantic models for trip creation and response (dispatch contract).
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import List

from app.db.enums import TripStatus


class TripCreate(BaseModel):
    """Schema for creating a new trip (dispatch input)."""
    driver_id: str
    package_ids: List[str]
    scheduled_start_time: datetime


class TripResponse(BaseModel):
    """Schema for trip response after creation (dispatch output)."""
    trip_id: UUID
    driver_name: str
    status: TripStatus
    total_packages: int
    total_cod: float
    estimated_time: str  # e.g. "45 min"

    class Config:
        from_attributes = True
