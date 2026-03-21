from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Any

# --- Security ---
from app.api.deps import RoleChecker
from app.models.enums import UserRole

# --- Schemas & Services ---
from app.schemas.tracking_schemas import LocationUpdate
from app.services.tracking_service import log_driver_location

router = APIRouter()

# 🚨 TEMPORARY: We are using SUPER_ADMIN here so you can test it today.
# Once your teammate finishes the Driver entity, simply change this to UserRole.DRIVER
DRIVER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN]))

@router.post("/location", status_code=202)
async def update_driver_location(
    location_in: LocationUpdate,
    background_tasks: BackgroundTasks,
    current_user: dict = DRIVER_ACCESS
) -> Any:
    """
    Ingest high-velocity GPS coordinates from the driver's mobile app.
    Saves to DynamoDB asynchronously to prevent database locking.
    """
    # Safely extract the ID (using admin_id for now during testing)
    driver_id = current_user.get("user_id") or current_user.get("admin_id", "Unknown")
    
    # Fire and forget the GPS ping to DynamoDB!
    background_tasks.add_task(
        log_driver_location,
        driver_id=driver_id,
        lat=location_in.lat,
        lng=location_in.lng,
        status=location_in.status,
        trip_id=str(location_in.trip_id) if location_in.trip_id else None,
        task_id=str(location_in.task_id) if location_in.task_id else None
    )
    
    return {"message": "Location queued for saving"}