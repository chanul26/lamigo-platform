from enum import Enum

# --- 1.1.1. Enum: UserRole ---
class UserRole(str, Enum):
    SUPER_ADMIN = 'SUPER_ADMIN'
    STATION_MANAGER = 'STATION_MANAGER'
    DRIVER = 'DRIVER'

# --- 1.1.2. Enum: VehicleType ---
class VehicleType(str, Enum):
    MOTORCYCLE = 'MOTORCYCLE'
    THREE_WHEEL = 'THREE_WHEEL'
    LORRY = 'LORRY'

# --- 1.1.3. Enum: DriverStatus ---
class DriverStatus(str, Enum):
    OFF_DUTY = 'OFF_DUTY'
    AVAILABLE = 'AVAILABLE'
    TRIP_SCHEDULED = 'TRIP_SCHEDULED'
    ON_TRIP = 'ON_TRIP'
    ON_INCIDENT = 'ON_INCIDENT'
    INCIDENT_RESPONSE = 'INCIDENT_RESPONSE'

# --- 1.1.4. Enum: LocationType ---
class LocationType(str, Enum):
    HOME = 'HOME'
    APARTMENT = 'APARTMENT'
    OFFICE = 'OFFICE'
    WAREHOUSE = 'WAREHOUSE'
    RETAIL_STORE = 'RETAIL_STORE'
    OTHER = 'OTHER'

# --- 1.1.5. Enum: PreferenceStatus ---
class PreferenceStatus(str, Enum):
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'
    NEUTRAL = 'NEUTRAL'

# --- 1.1.6. Enum: PackageStatus ---
class PackageStatus(str, Enum):
    TO_BE_DELIVERED = 'TO_BE_DELIVERED'
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    ON_TRIP = 'ON_TRIP'
    DELIVERING_NOW = 'DELIVERING_NOW'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

# --- 1.1.7. Enum: TripStatus ---
class TripStatus(str, Enum):
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

# --- 1.1.8. Enum: TaskStatus ---
class TaskStatus(str, Enum):
    DRAFT = 'DRAFT'
    SCHEDULED = 'SCHEDULED'
    ON_TRIP = 'ON_TRIP'
    DELIVERING_NOW = 'DELIVERING_NOW'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

# --- 1.1.9. Enum: FailureType ---
class FailureType(str, Enum):
    NOT_HOME = 'NOT_HOME'
    UNREACHABLE = 'UNREACHABLE'
    RECIPIENT_REJECTED = 'RECIPIENT_REJECTED'
    CANCELLED_BY_RECIPIENT = 'CANCELLED_BY_RECIPIENT'
    CANCELLED_BY_MANAGER = 'CANCELLED_BY_MANAGER'
    CANCELLED_BY_DRIVER = 'CANCELLED_BY_DRIVER'

# --- 1.1.10. Enum: InstructionType ---
class InstructionType(str, Enum):
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    VOICE_NOTE = 'VOICE_NOTE'

# --- 1.1.11. Enum: InstructionCreator ---
class InstructionCreator(str, Enum):
    RECIPIENT = 'RECIPIENT'
    STATION_MANAGER = 'STATION_MANAGER'
    DRIVER = 'DRIVER'

# --- 1.1.12 Enum: IncidentType ---
class IncidentType(str, Enum):
    VEHICLE_BREAKDOWN = 'VEHICLE_BREAKDOWN'
    ACCIDENT = 'ACCIDENT'
    TRAFFIC_POLICE = 'TRAFFIC_POLICE'
    MEDICAL_EMERGENCY = 'MEDICAL_EMERGENCY'
    OTHER = 'OTHER'

# --- 1.1.13. Enum: IncidentStatus ---
class IncidentStatus(str, Enum):
    REPORTED = 'REPORTED'
    INVESTIGATING = 'INVESTIGATING'
    RESOLVED = 'RESOLVED'

# --- 1.1.14. Enum: ResponseType ---
class ResponseType(str, Enum):
    HELP = 'HELP'
    PACKAGE_RESCUE = 'PACKAGE_RESCUE'
    MECHANICAL_AID = 'MECHANICAL_AID'
    OTHER = 'OTHER'

# --- 1.1.15. Enum: ResponseStatus ---
class ResponseStatus(str, Enum):
    DISPATCHED = 'DISPATCHED'
    ON_SITE = 'ON_SITE'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

# --- 1.1.16. Enum: PaymentMethod ---
class PaymentMethod(str, Enum):
    CASH = 'CASH'
    BANK_TRANSFER = 'BANK_TRANSFER'
    CHEQUE = 'CHEQUE'

# --- 1.1.17. Enum: SMSCategory ---
class SMSCategory(str, Enum):
    PIN_VERIFICATION = 'PIN_VERIFICATION'
    DELIVERY_UPDATE = 'DELIVERY_UPDATE'
    INCIDENT_ALERT = 'INCIDENT_ALERT'
    OTHER = 'OTHER'

# --- 1.1.18. Enum: SMSStatus ---
class SMSStatus(str, Enum):
    QUEUED = 'QUEUED'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    FAILED = 'FAILED'
    UNDELIVERED = 'UNDELIVERED'
