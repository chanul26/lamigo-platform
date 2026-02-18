"""
LamiGo Trip Endpoints
POST /trips — Create (dispatch) a trip. Mock logic until DB models exist.
"""
import uuid
from fastapi import APIRouter, HTTPException
from app.schemas.trip import TripCreate, TripResponse
from app.db.enums import TripStatus

router = APIRouter()

# Mock driver name lookup (replace with DB when ready)
MOCK_DRIVER_NAMES: dict[str, str] = {
    "d1": "Saman",
    "d2": "Nimal",
}


@router.post("/", response_model=TripResponse)
def create_trip(payload: TripCreate) -> TripResponse:
    """
    Create (dispatch) a new trip.
    Mock validation and calculation until DB is available.
    """
    # Validation: driver not available
    if payload.driver_id == "busy-driver":
        raise HTTPException(
            status_code=400,
            detail="Driver is not available",
        )

    # Validation: at least one package
    if not payload.package_ids:
        raise HTTPException(
            status_code=400,
            detail="package_ids cannot be empty",
        )

    # Mock calculation: total_cod = len(package_ids) * 500
    total_cod = len(payload.package_ids) * 500.0
    total_packages = len(payload.package_ids)
    driver_name = MOCK_DRIVER_NAMES.get(payload.driver_id, "Unknown Driver")

    return TripResponse(
        trip_id=uuid.uuid4(),
        driver_name=driver_name,
        status=TripStatus.SCHEDULED,
        total_packages=total_packages,
        total_cod=total_cod,
        estimated_time="45 min",  # Mock
    )
