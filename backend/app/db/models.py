"""LamiGo multi-tenant schema: organizations and users."""
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base


class Organization(Base):
    """Tenant organization (e.g. CityPack)."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")


class User(Base):
    """User linked to Firebase UID and an organization with a role."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), nullable=False, unique=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(64), nullable=False)  # e.g. SUPER_ADMIN, ADMIN, STAFF
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
