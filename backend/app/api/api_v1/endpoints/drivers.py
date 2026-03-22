from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole
from app.schemas.driver_ops_schemas import (
    DriverStatusUpdate, 
    DriverLocationPing, 
    DriverDashboardResponse
)
from app.services import driver_service

router = APIRouter()

DRIVER_ACCESS = Depends(RoleChecker([UserRole.DRIVER]))

@router.get("/dashboard", response_model=DriverDashboardResponse)
async def get_dashboard(
    current_user: dict = DRIVER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Fetches all data required to populate Pages 6 & 8 of the Mobile App."""
    # Securely extract the driver_id from the token
    driver_id = current_user.get("user_id")
    return await driver_service.get_driver_dashboard(db, driver_id)


@router.patch("/status")
async def update_status(
    payload: DriverStatusUpdate,
    current_user: dict = DRIVER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Driver toggles their shift status (e.g., starting a ride)."""
    driver_id = current_user.get("user_id")
    return await driver_service.update_driver_status(db, driver_id, payload)


@router.post("/location", status_code=status.HTTP_202_ACCEPTED)
async def ping_location(
    payload: DriverLocationPing,
    background_tasks: BackgroundTasks, # We use background tasks so the app doesn't wait for AWS
    current_user: dict = DRIVER_ACCESS
):
    """
    High-frequency endpoint called every 5 seconds.
    Writes directly to DynamoDB in the background. Does NOT touch Postgres.
    """
    driver_id = current_user.get("user_id")
    
    # We pass the DynamoDB write to a background task so the API returns 
    # a 202 Accepted to the Flutter app almost instantly (<50ms).
    background_tasks.add_task(driver_service.log_driver_location, driver_id, payload)
    
    return {"message": "Ping received"}