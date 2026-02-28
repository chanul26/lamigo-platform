import uuid
from sqlalchemy import (
    Column, 
    String, 
    Boolean, 
    Integer, 
    Numeric, 
    DateTime, 
    Date, 
    ForeignKey, 
    Text, 
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

# Import all 18 Enums from the LamiGo enums.py file
from app.models.enums import (
    UserRole, VehicleType, DriverStatus, LocationType, PreferenceStatus,
    PackageStatus, TripStatus, TaskStatus, FailureType, InstructionType,
    InstructionCreator, IncidentType, IncidentStatus, ResponseType,
    ResponseStatus, PaymentMethod, SMSCategory, SMSStatus
)

# Base class that all SQLAlchemy models inherit from
Base = declarative_base()

# ==========================================
# I. System Authority & Hierarchy
# ==========================================

class SuperAdmin(Base):
    """System-wide root access."""
    __tablename__ = 'super_admins'

    admin_id = Column(String(128), primary_key=True) # Firebase UID
    email = Column(String(255), nullable=False, unique=True) # Login email synced with Firebase
    name = Column(String(100), nullable=False) # Display name of the administrator
    role = Column(SQLEnum(UserRole), default=UserRole.SUPER_ADMIN) # Fixed role for polymorphism
    last_access_at = Column(DateTime(timezone=True), nullable=True) # Timestamp of last successful login
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Organization(Base):
    """The overarching tenant/company."""
    __tablename__ = 'organizations'

    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Tenant ID
    name = Column(String(100), nullable=False) # Registered name of the company
    contact_email = Column(String(255), nullable=False, unique=True) # Primary administrative contact
    website = Column(String(255), nullable=True)
    logo_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True) # Soft-delete flag. If FALSE, blocks all access.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Branch(Base):
    """Physical hub or station locations."""
    __tablename__ = 'branches'

    branch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.org_id'), nullable=False)
    name = Column(String(100), nullable=False) # e.g., "Galle Main Hub"
    address = Column(Text, nullable=False)
    gps_lat = Column(Numeric(9, 6), nullable=False) # For routing and mapping
    gps_lng = Column(Numeric(9, 6), nullable=False) # For routing and mapping
    default_commission_rate = Column(Numeric(5, 2), server_default="0.00") # Base commission percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(Base):
    """Core identity for Drivers and Managers."""
    __tablename__ = 'users'

    user_id = Column(String(128), primary_key=True) # Firebase UID
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.branch_id'), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True) # Used for Firebase Phone Auth
    role = Column(SQLEnum(UserRole), nullable=False) # STATION_MANAGER or DRIVER
    full_name = Column(String(100), nullable=False) # Legal full name as per NIC
    preferred_name = Column(String(50), nullable=True) # Display name for the app UI
    nic_number = Column(String(20), nullable=False, unique=True) # National Identity Card
    email = Column(String(255), unique=True, nullable=True) # Optional email
    is_active = Column(Boolean, default=True) # Soft-delete flag (e.g., for fired employees)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ==========================================
# II. Personnel & Finance
# ==========================================

class Driver(Base):
    """Operational data for delivery personnel."""
    __tablename__ = 'drivers'

    driver_id = Column(String(128), ForeignKey('users.user_id'), primary_key=True) # Links 1:1 with User
    license_number = Column(String(50), nullable=False, unique=True) # Official Driving License ID
    commission_rate = Column(Numeric(5, 2), nullable=True) # Override Rate (If NULL, use Branch default)
    vehicle_number = Column(String(20), nullable=False) # License plate (e.g., WP CAM-1234)
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False) # Enum class of vehicle
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.OFF_DUTY) # Current operational state
    status_updated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(128), ForeignKey('users.user_id'), nullable=False) # Manager who onboarded them. Enforces accountability.
    current_lat = Column(Numeric(9, 6), nullable=True) # Placeholder for real-time GPS
    current_lng = Column(Numeric(9, 6), nullable=True) # Placeholder for real-time GPS
    location_updated_at = Column(DateTime(timezone=True), nullable=True)

class DriverFinancialProfile(Base):
    """Tracks lifetime earnings and current owed balances."""
    __tablename__ = 'driver_financial_profiles'

    driver_id = Column(String(128), ForeignKey('drivers.driver_id'), primary_key=True)
    current_payable_balance = Column(Numeric(10, 2), server_default="0.00") # Total amount Station owes Driver
    total_lifetime_earnings = Column(Numeric(12, 2), server_default="0.00") # Sum of all TripCommission records
    total_lifetime_settled = Column(Numeric(12, 2), server_default="0.00") # Sum of all DriverSettlement records
    last_settlement_date = Column(DateTime(timezone=True), nullable=True) # Last time balance was cleared
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TripCommission(Base):
    """Immutable ledger of earnings per completed trip."""
    __tablename__ = 'trip_commissions'

    commission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey('trips.trip_id'), nullable=False) # Completed trip link
    driver_id = Column(String(128), ForeignKey('drivers.driver_id'), nullable=False) # Earner
    amount_earned = Column(Numeric(10, 2), nullable=False) # Calculated commission (e.g., 500.00 LKR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DriverSettlement(Base):
    """Ledger of payouts made to drivers."""
    __tablename__ = 'driver_settlements'

    settlement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(String(128), ForeignKey('drivers.driver_id'), nullable=False)
    processed_by = Column(String(128), ForeignKey('users.user_id'), nullable=False) # Manager who paid
    amount_paid = Column(Numeric(10, 2), nullable=False) # Actual amount transferred
    balance_at_settlement = Column(Numeric(10, 2), nullable=False) # Snapshot of outstanding balance at payout
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False) # CASH, BANK_TRANSFER, CHEQUE
    reference_note = Column(Text, nullable=True) # Transaction ID or cheque number
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# III. Logistics & Customer Data
# ==========================================

class Recipient(Base):
    """End customers receiving packages."""
    __tablename__ = 'recipients'

    recipient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    location_type = Column(SQLEnum(LocationType), default=LocationType.HOME) # Hint for driver (Apartment, Office)
    floor_number = Column(String(10), nullable=True) # Crucial for APARTMENT or OFFICE
    is_location_verified = Column(Boolean, default=False) # TRUE if GPS confirmed by past delivery
    gps_lat = Column(Numeric(9, 6), nullable=False)
    gps_lng = Column(Numeric(9, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Package(Base):
    """Core unit of delivery."""
    __tablename__ = 'packages'

    package_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id = Column(String(20), nullable=False, unique=True) # Public ID (e.g., LMG-8921)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey('recipients.recipient_id')) # Linked profile
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.branch_id'), nullable=False) # Strictly enforces physical accountability
    status = Column(SQLEnum(PackageStatus), default=PackageStatus.TO_BE_DELIVERED) # Current state
    
    sender_name = Column(String(100), nullable=False)
    sender_phone = Column(String(20), nullable=True)
    sender_address = Column(Text, nullable=True)
    package_photo_url = Column(Text, nullable=True) # Proof of pickup image
    weight = Column(Numeric(6, 2), nullable=False) # Weight in kg
    is_cod = Column(Boolean, default=False) # Cash on Delivery flag
    cod_amount = Column(Numeric(10, 2), server_default="0.00") # Amount driver must collect
    delivery_charge = Column(Numeric(10, 2), nullable=False) # Service fee
    num_of_attempts = Column(Integer, server_default="0") # Failed delivery attempts counter
    
    recipient_name = Column(String(100), nullable=False) # Snapshot data
    address = Column(Text, nullable=False) # Snapshot data
    gps_lat = Column(Numeric(9, 6), nullable=False) # Snapshot data
    gps_lng = Column(Numeric(9, 6), nullable=False) # Snapshot data
    
    completed_at = Column(DateTime(timezone=True), nullable=True) # When status became COMPLETED or FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DeliveryPreference(Base):
    """Calendar constraints set by recipients."""
    __tablename__ = 'delivery_preferences'

    preference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey('recipients.recipient_id'), nullable=False)
    target_date = Column(Date, nullable=False) # Specific day on the calendar
    status = Column(SQLEnum(PreferenceStatus), nullable=False) # Available, Unavailable, Neutral
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ==========================================
# IV. Operational Manifest (The Trip)
# ==========================================

class Trip(Base):
    """Route manifest containing multiple delivery tasks."""
    __tablename__ = 'trips'

    trip_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey('branches.branch_id'), nullable=False)
    driver_id = Column(String(128), ForeignKey('drivers.driver_id'), nullable=True) # Assigned driver
    status = Column(SQLEnum(TripStatus), default=TripStatus.DRAFT)
    
    total_tasks_count = Column(Integer, server_default="0") # Total stops
    delivered_count = Column(Integer, server_default="0") # Successful deliveries
    total_weight = Column(Numeric(8, 2), server_default="0.00") # Sum of package weights
    total_cod_to_collect = Column(Numeric(10, 2), server_default="0.00") # Expected cash return
    
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True) # Plan: Manager's expected dispatch
    actual_start_time = Column(DateTime(timezone=True), nullable=True) # Reality: Driver clicked "Start"
    estimated_return_time_scheduled = Column(DateTime(timezone=True), nullable=True) # Baseline prediction
    estimated_return_time_actual = Column(DateTime(timezone=True), nullable=True) # Live dynamic prediction
    actual_return_time = Column(DateTime(timezone=True), nullable=True) # Reality: Trip finished
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DeliveryTask(Base):
    """Individual stops/packages within a Trip manifest."""
    __tablename__ = 'delivery_tasks'

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey('trips.trip_id'), nullable=False)
    package_id = Column(UUID(as_uuid=True), ForeignKey('packages.package_id'), nullable=False)
    sequence_number = Column(Integer, nullable=False) # Order in the route (1, 2, 3...)
    status = Column(SQLEnum(TaskStatus), nullable=False)
    
    estimated_start_time = Column(DateTime(timezone=True), nullable=True) # Plan
    actual_start_time = Column(DateTime(timezone=True), nullable=True) # ML Feature: Timestamp entered PREVIOUS H3 Hexagon
    estimated_arrival_time = Column(DateTime(timezone=True), nullable=True) # ML Prediction: Calculated ETA
    actual_arrival_time = Column(DateTime(timezone=True), nullable=True) # Auto-Trigger: Entered THIS H3 Hexagon
    actual_completion_time = Column(DateTime(timezone=True), nullable=True) # Manual: Driver clicks Complete/Failed
    
    failure_type = Column(SQLEnum(FailureType), nullable=True) # Required if status == FAILED
    failure_note = Column(Text, nullable=True) # Manager/Driver notes
    proof_image_url = Column(Text, nullable=True) # Photo proof for audit
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TaskInstruction(Base):
    """Micro-notes and guidance for specific tasks (Voice, Text, Image)."""
    __tablename__ = 'task_instructions'

    instruction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('delivery_tasks.task_id'), nullable=False)
    type = Column(SQLEnum(InstructionType), nullable=False) # TEXT, IMAGE, VOICE_NOTE
    creator_role = Column(SQLEnum(InstructionCreator), nullable=False) # RECIPIENT, STATION_MANAGER, DRIVER
    
    content_text = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True) # URL for images or voice notes
    
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DeliveryContext(Base):
    """Stores ML baselines and environmental metadata for ETA predictions."""
    __tablename__ = 'delivery_contexts'

    metadata_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('delivery_tasks.task_id'), nullable=False) # Context without a task is invalid
    
    # External API data fields (nullable to prevent system failures during 3rd-party outages)
    google_eta_seconds = Column(Integer, nullable=True) # Baseline raw duration from Google Routes API
    google_dist_meters = Column(Integer, nullable=True) # Baseline distance from previous stop
    rain_volume_1h = Column(Numeric(5, 2), nullable=True) # ML Feature: Rainfall in last hour
    weather_code = Column(Integer, nullable=True) # ML Feature: Weather Condition ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# V. Support & Incident Management
# ==========================================

class Incident(Base):
    """Real-time disruptions reported by drivers on the road."""
    __tablename__ = 'incidents'

    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey('trips.trip_id'), nullable=False)
    driver_id = Column(String(128), ForeignKey('drivers.driver_id'), nullable=False)
    type = Column(SQLEnum(IncidentType), nullable=False) # ACCIDENT, BREAKDOWN, etc.
    description = Column(Text, nullable=True) # Manager's detailed log
    
    reported_at_lat = Column(Numeric(9, 6), nullable=False) # GPS Latitude where button was pressed
    reported_at_lng = Column(Numeric(9, 6), nullable=False) # GPS Longitude where button was pressed
    
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.REPORTED)
    handled_by = Column(String(128), ForeignKey('users.user_id'), nullable=True) # Manager who accepted the ticket
    handled_at = Column(DateTime(timezone=True), nullable=True) # Response time
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class IncidentResponseAssignment(Base):
    """Tracks rescue missions and backup drivers assigned to active incidents."""
    __tablename__ = 'incident_assignments'

    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey('incidents.incident_id'), nullable=False)
    backup_driver_id = Column(String(128), ForeignKey('drivers.driver_id'), nullable=False) # Driver sent to rescue
    assigned_by = Column(String(128), ForeignKey('users.user_id'), nullable=False) # Manager who ordered rescue
    
    type = Column(SQLEnum(ResponseType), nullable=False) # HELP, PACKAGE_RESCUE, MECHANICAL_AID
    status = Column(SQLEnum(ResponseStatus), default=ResponseStatus.DISPATCHED)
    
    dispatched_at = Column(DateTime(timezone=True), server_default=func.now()) # When backup driver was notified
    arrived_at = Column(DateTime(timezone=True), nullable=True) # When backup driver reached location
    completed_at = Column(DateTime(timezone=True), nullable=True) # When mission finished