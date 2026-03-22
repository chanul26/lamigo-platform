from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.enums import DriverStatus

# ==========================================
# 1. Shift & Status Management
# ==========================================
class DriverStatusUpdate(BaseModel):
    status: DriverStatus = Field(..., description="The new operational status of the driver")

# ==========================================
# 2. Live GPS Tracking (DynamoDB Aligned)
# ==========================================
class DriverLocationPing(BaseModel):
    """Payload sent every 5 seconds by the mobile background service."""
    timestamp: datetime = Field(..., description="Exact time the GPS coordinate was captured")
    lat: float = Field(..., description="GPS Latitude", ge=-90.0, le=90.0)
    lon: float = Field(..., description="GPS Longitude", ge=-180.0, le=180.0)
    
    # DynamoDB GSIs (Optional because a driver might be driving without an active trip)
    trip_id: Optional[UUID] = None 
    task_id: Optional[UUID] = None 
    status: DriverStatus = Field(..., description="Driver's current operational state")

# ==========================================
# 3. Dashboard & Financials 
# ==========================================
class EarningHistoryRecord(BaseModel):
    date: str 
    amount: Decimal

class NextStopSummary(BaseModel):
    address: str
    eta: str 
    cod_amount: Decimal 

class DriverDashboardResponse(BaseModel):
    driver_name: str
    driver_id: str
    vehicle_type: str
    vehicle_number: str
    completed_tasks_count: int = 0
    total_tasks_count: int = 0
    current_earnings: Decimal 
    earnings_history: List[EarningHistoryRecord] = Field(default_factory=list)
    next_stop: Optional[NextStopSummary] = None

    model_config = ConfigDict(from_attributes=True)