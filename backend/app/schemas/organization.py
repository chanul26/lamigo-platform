from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Shared properties
class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=100, description="Registered name of the company")
    contact_email: EmailStr = Field(..., description="Primary administrative contact")
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = None
    is_active: bool = True

# Properties to receive on creation (POST)
class OrganizationCreate(OrganizationBase):
    pass

# Properties to receive on update (PUT/PATCH)
class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

# Properties to return to the client (GET/Responses)
class OrganizationResponse(OrganizationBase):
    org_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read from SQLAlchemy models