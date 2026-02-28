"""
LamiGo User Schemas
Pydantic models for user data validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base schema for user data."""
    email: Optional[str] = None
    role: str


class UserCreate(UserBase):
    """Schema for creating a new user."""
    firebase_uid: str
    org_id: int


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    """Schema for user response with full details."""
    id: int
    firebase_uid: str
    org_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    """Base schema for organization data."""
    name: str


class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass


class Organization(OrganizationBase):
    """Schema for organization response with full details."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithOrganization(User):
    """Schema for user with organization details."""
    organization: Organization
