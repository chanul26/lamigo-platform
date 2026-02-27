"""
LamiGo Driver Endpoints
Handles all driver-related API operations
"""

from fastapi import APIRouter
from app.schemas.driver_schemas import Driver

router = APIRouter()

MOCK_DRIVERS: list[Driver] = [
    Driver(
        id=1,
        name="Sunil Bandara",
        phone_number="+94 77 123 4567",
        vehicle_type="Bike",
        is_active=True,
        current_location_lat=6.9271,
        current_location_long=79.8612,
    ),
    Driver(
        id=2,
        name="Chaminda Rathnayake",
        phone_number="+94 76 234 5678",
        vehicle_type="Van",
        is_active=True,
        current_location_lat=6.8649,
        current_location_long=79.8997,
    ),
    Driver(
        id=3,
        name="Priyantha Kumara",
        phone_number="+94 71 345 6789",
        vehicle_type="Truck",
        is_active=False,
        current_location_lat=None,
        current_location_long=None,
    ),
]


@router.get("/", response_model=list[Driver])
def get_drivers():
    """
    Retrieve all drivers.
    Returns a list of all registered drivers.
    """
    return MOCK_DRIVERS


@router.get("/active", response_model=list[Driver])
def get_active_drivers():
    """
    Retrieve only active drivers.
    Used by Station Manager for assignment operations.
    """
    return [driver for driver in MOCK_DRIVERS if driver.is_active]


@router.get("/{driver_id}", response_model=Driver)
def get_driver(driver_id: int):
    """
    Retrieve a specific driver by ID.
    """
    for driver in MOCK_DRIVERS:
        if driver.id == driver_id:
            return driver
    return {"error": "Driver not found"}
