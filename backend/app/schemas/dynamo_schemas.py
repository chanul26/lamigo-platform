"""
LamiGo DynamoDB Schemas
Pydantic models for DynamoDB log entries

These schemas are used for logging delivery events, driver activities,
and system events to DynamoDB for real-time tracking and analytics.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class LogEntryBase(BaseModel):
    """Base schema for DynamoDB log entries."""
    event_type: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class DeliveryLogEntry(LogEntryBase):
    """Log entry for delivery events."""
    package_id: int
    tracking_number: str
    driver_id: Optional[int] = None
    status: str
    location_lat: Optional[float] = None
    location_long: Optional[float] = None


class DriverActivityLog(LogEntryBase):
    """Log entry for driver activities."""
    driver_id: int
    activity_type: str
    location_lat: Optional[float] = None
    location_long: Optional[float] = None
    trip_id: Optional[int] = None


class SystemEventLog(LogEntryBase):
    """Log entry for system events."""
    service_name: str
    level: str
    message: str
    stack_trace: Optional[str] = None


class IncidentLog(LogEntryBase):
    """Log entry for delivery incidents."""
    incident_id: int
    package_id: Optional[int] = None
    driver_id: Optional[int] = None
    incident_type: str
    description: str
    resolution: Optional[str] = None
