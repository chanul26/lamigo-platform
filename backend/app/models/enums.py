"""
LamiGo Shared Enums
Defines all enum types used across the application
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles within the LamiGo platform."""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    STATION_MANAGER = "STATION_MANAGER"
    STAFF = "STAFF"
    DRIVER = "DRIVER"


class PackageStatus(str, Enum):
    """Status of a package/delivery."""
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    RETURNED = "Returned"
    FAILED = "Failed"


class VehicleType(str, Enum):
    """Types of delivery vehicles."""
    BIKE = "Bike"
    VAN = "Van"
    TRUCK = "Truck"
    THREE_WHEELER = "Three Wheeler"


class TripStatus(str, Enum):
    """Status of a delivery trip."""
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class IncidentType(str, Enum):
    """Types of delivery incidents."""
    DELAY = "Delay"
    DAMAGE = "Damage"
    LOST = "Lost"
    CUSTOMER_UNAVAILABLE = "Customer Unavailable"
    ADDRESS_INCORRECT = "Address Incorrect"
    OTHER = "Other"
