from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.enums import InstructionType, InstructionCreator

# ==========================================
# 1. Base Schema (Shared attributes)
# ==========================================
class InstructionBase(BaseModel):
    task_id: UUID = Field(..., description="The specific delivery task this note belongs to")
    type: InstructionType = Field(..., description="TEXT, IMAGE, or VOICE_NOTE")
    creator_role: InstructionCreator = Field(..., description="RECIPIENT, STATION_MANAGER, or DRIVER")
    
    content_text: Optional[str] = None
    media_url: Optional[str] = None

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class InstructionCreate(InstructionBase):
    """Payload for adding a new note to a task."""
    pass

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class InstructionUpdate(BaseModel):
    """Payload for modifying a note."""
    content_text: Optional[str] = None
    media_url: Optional[str] = None

# ==========================================
# 4. Response Schema (Output to Frontend)
# ==========================================
class InstructionResponse(InstructionBase):
    instruction_id: UUID
    
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)