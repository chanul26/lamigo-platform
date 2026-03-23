from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, IncidentStatus
from app.schemas.incident_schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse,
    AssignmentCreate, AssignmentUpdate, AssignmentResponse
)
from app.services import incident_service

router = APIRouter()

DRIVER_ACCESS = Depends(RoleChecker([UserRole.DRIVER]))
MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    current_user: dict = DRIVER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Driver reports an emergency."""
    # SECURITY PATCH: Extract driver_id from token, not the payload
    driver_id = current_user.get("user_id")
    return await incident_service.create_incident(db, incident_in, driver_id)

@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    trip_id: Optional[UUID] = Query(None, description="Filter by a specific trip"),
    incident_status: Optional[IncidentStatus] = Query(None, description="Filter by state (e.g., REPORTED, RESOLVED)"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Fetch incidents with strict IDOR data isolation."""
    user_role = current_user.get("role")
    branch_id = None
    driver_id = None
    
    if user_role == UserRole.DRIVER:
        # Drivers can only see their own panics
        driver_id = current_user.get("user_id")
    elif user_role == UserRole.STATION_MANAGER:
        # Managers can only see panics in their own branch
        branch_id = current_user.get("branch_id")
        
    return await incident_service.get_all_incidents(
        db, branch_id=branch_id, trip_id=trip_id, driver_id=driver_id, incident_status=incident_status
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await incident_service.get_incident(db, incident_id)

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_in: IncidentUpdate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Manager updates incident status."""
    # SECURITY PATCH: Record the actual manager making the update
    manager_id = current_user.get("user_id")
    return await incident_service.update_incident(db, incident_id, incident_in, manager_id)

# ==========================================
# Assignments (Rescue Missions)
# ==========================================

@router.post("/{incident_id}/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def dispatch_rescue(
    incident_id: UUID,
    payload: AssignmentCreate,
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """Station Manager dispatches a backup driver to an active incident."""
    manager_id = current_user.get("user_id")
    return await incident_service.assign_backup(db, incident_id, payload, manager_id)


@router.patch("/assignments/{assignment_id}/status", response_model=AssignmentResponse)
async def update_rescue_status(
    assignment_id: UUID,
    payload: AssignmentUpdate,
    current_user: dict = ALL_ACCESS, # Both managers and the rescue driver can update this
    db: AsyncSession = Depends(get_db)
):
    """Rescue Driver clicks 'Arrived' or 'Completed' on their app."""
    return await incident_service.update_assignment_status(db, assignment_id, payload)