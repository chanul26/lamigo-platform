from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID

from app.models.enums import PreferenceStatus

# ==========================================
# 1. Create Schema (POST Requests)
# ==========================================
class PreferenceCreate(BaseModel):
    package_id: UUID
    target_date: date
    status: PreferenceStatus

# ==========================================
# 2. Update Schema (PATCH Requests)
# ==========================================
class PreferenceUpdate(BaseModel):
    target_date: Optional[date] = None
    status: Optional[PreferenceStatus] = None

# ==========================================
# 3. Response Schema (Output to Frontend)
# ==========================================
class PreferenceResponse(BaseModel):
    preference_id: UUID
    package_id: UUID
    target_date: date
    status: PreferenceStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)