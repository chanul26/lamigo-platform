# LamiGo Schemas Module
from app.schemas.common import (
    Station,
    StationCreate,
    StationBase,
    LocationSchema,
    PaginationParams,
    MessageResponse,
)
from app.schemas.driver_schemas import (
    Driver,
    DriverCreate,
    DriverBase,
    DriverUpdate,
    DriverLocation,
)
from app.schemas.trip_schemas import (
    Package,
    PackageCreate,
    PackageBase,
    Trip,
    TripCreate,
    TripBase,
    TripOptimizationRequest,
    TripOptimizationResponse,
)
from app.schemas.user_schemas import (
    User,
    UserCreate,
    UserBase,
    UserUpdate,
    Organization,
    OrganizationCreate,
    OrganizationBase,
    UserWithOrganization,
)

__all__ = [
    # Common
    "Station",
    "StationCreate",
    "StationBase",
    "LocationSchema",
    "PaginationParams",
    "MessageResponse",
    # Driver
    "Driver",
    "DriverCreate",
    "DriverBase",
    "DriverUpdate",
    "DriverLocation",
    # Trip/Package
    "Package",
    "PackageCreate",
    "PackageBase",
    "Trip",
    "TripCreate",
    "TripBase",
    "TripOptimizationRequest",
    "TripOptimizationResponse",
    # User
    "User",
    "UserCreate",
    "UserBase",
    "UserUpdate",
    "Organization",
    "OrganizationCreate",
    "OrganizationBase",
    "UserWithOrganization",
]
