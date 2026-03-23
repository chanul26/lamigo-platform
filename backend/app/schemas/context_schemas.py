from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

# ==========================================
# 1. Base Schema (Shared attributes)
# ==========================================
class ContextBase(BaseModel):
    task_id: UUID = Field(..., description="The specific delivery task this metadata belongs to")
    google_eta_seconds: Optional[int] = Field(None, description="Baseline raw duration from Google Routes API")
    google_dist_meters: Optional[int] = Field(None, description="Baseline distance from previous stop")
    rain_volume_1h: Optional[float] = Field(None, description="Rainfall in the last hour")
    weather_code: Optional[int] = Field(None, description="Weather Condition ID")

# ==========================================
# 2. Create Schema (POST Requests)
# ==========================================
class ContextCreate(ContextBase):
    """Payload for creating ML metadata for a task."""
    pass

# ==========================================
# 3. Update Schema (PATCH Requests)
# ==========================================
class ContextUpdate(BaseModel):
    """Payload for updating ML metadata (e.g., refreshing weather)."""
    google_eta_seconds: Optional[int] = None
    google_dist_meters: Optional[int] = None
    rain_volume_1h: Optional[float] = None
    weather_code: Optional[int] = None

# ==========================================
# 4. Response Schema (Output to Frontend)
# ==========================================
class ContextResponse(ContextBase):
    metadata_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)