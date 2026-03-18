from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime

from app.models.enums import PreferenceStatus

class DeliveryPreferenceBase(BaseModel):
    target_date: date
    status: PreferenceStatus

class DeliveryPreferenceCreate(DeliveryPreferenceBase):
    package_id: UUID  # <-- CHANGED

class DeliveryPreferenceUpdate(BaseModel):
    status: PreferenceStatus

class DeliveryPreferenceResponse(DeliveryPreferenceBase):
    preference_id: UUID
    package_id: UUID  # <-- CHANGED
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)