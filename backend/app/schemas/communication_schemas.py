from pydantic import BaseModel, Field
from uuid import UUID

# --- Input Schemas (For POST requests) ---
class SMSCreate(BaseModel):
    package_id: UUID
    recipient_phone: str = Field(..., max_length=20)
    message_body: str
    category: str
    status: str

class CallCreate(BaseModel):
    recipient_phone: str = Field(..., max_length=20)
    task_id: UUID
    duration_seconds: int = 0

# --- Output Schemas (For GET requests) ---
class SMSResponse(BaseModel):
    sms_id: str
    package_id: str
    recipient_phone: str
    message_body: str
    category: str
    status: str
    created_at: str

class CallResponse(BaseModel):
    call_id: str
    user_id: str
    task_id: str
    recipient_phone: str
    role: str
    duration_seconds: int
    created_at: str