"""
LamiGo Package Endpoints
Handles all package-related API operations
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
from app.schemas import Package

router = APIRouter()

# Mock data for 5 LamiGo packages
MOCK_PACKAGES: list[Package] = [
    Package(
        id=1,
        tracking_number="LMG-2026-001",
        recipient_name="Kamal Perera",
        delivery_address="45 Galle Road, Colombo 03",
        status="In Transit",
        assigned_driver_id=1,
        created_at=datetime.now() - timedelta(days=2),
    ),
    Package(
        id=2,
        tracking_number="LMG-2026-002",
        recipient_name="Nimal Silva",
        delivery_address="123 Kandy Road, Kadawatha",
        status="Pending",
        assigned_driver_id=None,
        created_at=datetime.now() - timedelta(days=1),
    ),
    Package(
        id=3,
        tracking_number="LMG-2026-003",
        recipient_name="Samanthi Fernando",
        delivery_address="78 Beach Road, Mount Lavinia",
        status="Delivered",
        assigned_driver_id=2,
        created_at=datetime.now() - timedelta(days=5),
    ),
    Package(
        id=4,
        tracking_number="LMG-2026-004",
        recipient_name="Ruwan Jayawardena",
        delivery_address="56 Temple Road, Nugegoda",
        status="In Transit",
        assigned_driver_id=3,
        created_at=datetime.now() - timedelta(hours=6),
    ),
    Package(
        id=5,
        tracking_number="LMG-2026-005",
        recipient_name="Dilini Wickramasinghe",
        delivery_address="92 Station Road, Dehiwala",
        status="Pending",
        assigned_driver_id=None,
        created_at=datetime.now() - timedelta(hours=2),
    ),
]


@router.get("/", response_model=list[Package])
def get_packages():
    """
    Retrieve all packages.
    Returns a list of all packages in the system.
    """
    return MOCK_PACKAGES


@router.get("/{package_id}", response_model=Package)
def get_package(package_id: int):
    """
    Retrieve a specific package by ID.
    """
    for package in MOCK_PACKAGES:
        if package.id == package_id:
            return package
    return {"error": "Package not found"}


@router.get("/tracking/{tracking_number}", response_model=Package)
def get_package_by_tracking(tracking_number: str):
    """
    Retrieve a package by its tracking number.
    Used by Customer Portal for package tracking.
    """
    for package in MOCK_PACKAGES:
        if package.tracking_number == tracking_number:
            return package
    return {"error": "Package not found"}
