from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.enums import TaskStatus, FailureType

# ==========================================
# 1. Base Schema (Shared attributes)
# ==========================================
class TaskBase(BaseModel):
    sequence_number: int = Field(..., description="The order of this stop in the driver's route (1, 2, 3...)")
    estimated_start_time: Optional[datetime] = None
    estimated_arrival_time: Optional[datetime] = None

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class TaskCreate(TaskBase):
    """Payload for Station Managers assigning a package to a trip."""
    trip_id: UUID
    package_id: UUID

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class TaskUpdate(BaseModel):
    """Payload for Drivers updating the status on the road."""
    status: Optional[TaskStatus] = None
    sequence_number: Optional[int] = None
    
    actual_start_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    
    failure_type: Optional[FailureType] = None
    failure_note: Optional[str] = None
    proof_image_url: Optional[str] = None

# ==========================================
# 4. Response Schema (Output to Frontend)
# ==========================================
class TaskResponse(TaskBase):
    task_id: UUID
    trip_id: UUID
    package_id: UUID
    status: TaskStatus
    
    actual_start_time: Optional[datetime] = None
    actual_arrival_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    
    failure_type: Optional[FailureType] = None
    failure_note: Optional[str] = None
    proof_image_url: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)