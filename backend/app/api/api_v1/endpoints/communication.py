from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List
from uuid import UUID

# Security & Enums
from app.api.deps import RoleChecker
from app.models.enums import UserRole

# Schemas & Services
from app.schemas.communication_schemas import SMSCreate, CallCreate, SMSResponse, CallResponse
from app.services import communication_service

router = APIRouter()

# Allow Super Admins and Station Managers to access these routes
MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))

@router.post("/sms", status_code=202)
async def log_sms_endpoint(
    payload: SMSCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = MANAGER_ACCESS
):
    """Log an SMS message to DynamoDB asynchronously."""
    background_tasks.add_task(
        communication_service.log_sms,
        package_id=str(payload.package_id),
        recipient_phone=payload.recipient_phone,
        message_body=payload.message_body,
        category=payload.category,
        status=payload.status
    )
    return {"message": "SMS log queued successfully."}

@router.get("/sms/{package_id}", response_model=List[SMSResponse])
async def get_package_sms_history(
    package_id: UUID,
    current_user: dict = MANAGER_ACCESS
):
    """Fetch SMS history for a specific package."""
    return communication_service.get_sms_history_by_package(str(package_id))

@router.post("/call", status_code=202)
async def log_call_endpoint(
    payload: CallCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = MANAGER_ACCESS
):
    """Log a phone call to DynamoDB asynchronously."""
    # Securely extract the logged-in user's ID and role
    user_id = current_user.get("user_id") or current_user.get("admin_id", "Unknown")
    role = current_user.get("role", "UNKNOWN")
    
    background_tasks.add_task(
        communication_service.log_call,
        user_id=user_id,
        recipient_phone=payload.recipient_phone,
        task_id=str(payload.task_id),
        role=role,
        duration_seconds=payload.duration_seconds
    )
    return {"message": "Call log queued successfully."}

@router.get("/calls/{user_id}", response_model=List[CallResponse])
async def get_user_call_history(
    user_id: str,
    current_user: dict = MANAGER_ACCESS
):
    """Fetch Call history for a specific employee."""
    return communication_service.get_call_history_by_user(user_id)