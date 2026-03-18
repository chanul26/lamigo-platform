from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.enums import TripStatus, TaskStatus, FailureType

# --- Delivery Task Schemas ---
class DeliveryTaskBase(BaseModel):
    sequence_number: int = Field(..., description="Order of the stop (1, 2, 3...)")
    status: TaskStatus = TaskStatus.DRAFT

class DeliveryTaskCreate(DeliveryTaskBase):
    package_id: UUID

class DeliveryTaskResponse(DeliveryTaskBase):
    task_id: UUID
    trip_id: UUID
    package_id: UUID
    estimated_start_time: Optional[datetime] = None
    estimated_arrival_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    failure_type: Optional[FailureType] = None
    failure_note: Optional[str] = None
    proof_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Trip Schemas ---
class TripBase(BaseModel):
    scheduled_start_time: Optional[datetime] = None

class TripCreate(TripBase):
    branch_id: UUID
    # driver_id is optional because a manager can draft a route before assigning a driver
    driver_id: Optional[str] = None 

class TripUpdate(BaseModel):
    driver_id: Optional[str] = None
    status: Optional[TripStatus] = None
    actual_start_time: Optional[datetime] = None
    actual_return_time: Optional[datetime] = None

class TripResponse(TripBase):
    trip_id: UUID
    branch_id: UUID
    driver_id: Optional[str] = None
    status: TripStatus
    total_tasks_count: int
    delivered_count: int
    total_weight: float
    total_cod_to_collect: float
    actual_start_time: Optional[datetime] = None
    estimated_return_time_scheduled: Optional[datetime] = None
    estimated_return_time_actual: Optional[datetime] = None
    actual_return_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
