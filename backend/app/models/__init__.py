# app/models/__init__.py

# 1. Import the Base
from .sql_models import Base

# 2. Import ALL your Enums
from .enums import (
    UserRole, VehicleType, DriverStatus, LocationType, PreferenceStatus,
    PackageStatus, TripStatus, TaskStatus, FailureType, InstructionType,
    InstructionCreator, IncidentType, IncidentStatus, ResponseType,
    ResponseStatus, PaymentMethod, SMSCategory, SMSStatus
)

# 3. Import ALL 17 of your Entities so Alembic can "see" them
from .sql_models import (
    SuperAdmin, Organization, Branch, User, Driver, 
    DriverFinancialProfile, TripCommission, DriverSettlement,
    Recipient, Package, DeliveryPreference, Trip, DeliveryTask,
    TaskInstruction, DeliveryContext, Incident, IncidentResponseAssignment
)