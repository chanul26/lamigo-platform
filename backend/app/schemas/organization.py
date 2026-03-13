from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

# 1. Base Schema: Shared properties across all Organization requests/responses
class OrganizationBase(BaseModel):
    name: str
    contact_email: str
    website: Optional[str] = None
    logo_url: Optional[str] = None

# 2. Create Schema: Used for POST requests
# Inherits everything from Base, no additional fields needed right now.
class OrganizationCreate(OrganizationBase):
    pass

# 3. Update Schema: Used for PATCH/PUT requests
# Everything is Optional because the admin might only update one field at a time.
class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

# 4. Response Schema: What the API returns to the frontend
class OrganizationResponse(OrganizationBase):
    org_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # This is crucial: It tells Pydantic to read the data from your SQLAlchemy ORM model
    model_config = ConfigDict(from_attributes=True)