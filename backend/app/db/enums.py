"""LamiGo database enums (placeholders until DB models are finalised)."""
from enum import Enum


class TripStatus(str, Enum):
    """Status of a delivery trip."""
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
