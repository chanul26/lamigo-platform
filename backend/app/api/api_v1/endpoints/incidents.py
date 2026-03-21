from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# --- Security Gatekeepers ---
from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, IncidentStatus

# --- Schemas & Services ---
from app.schemas.incident_schemas import IncidentCreate, IncidentUpdate, IncidentResponse
from app.services import incident_service

router = APIRouter()

# Define our RBAC (Role-Based Access Control) levels
MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    # Drivers hitting the SOS app button need access to this
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Report a new emergency/incident (e.g., Accident, Breakdown).
    """
    return await incident_service.create_incident(db, incident_in)


@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    # Query parameters for the Manager's emergency dashboard
    trip_id: Optional[UUID] = Query(None, description="Filter by a specific trip"),
    driver_id: Optional[str] = Query(None, description="Filter by a specific driver"),
    incident_status: Optional[IncidentStatus] = Query(None, description="Filter by state (e.g., REPORTED, RESOLVED)"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of incidents with powerful filtering.
    """
    return await incident_service.get_all_incidents(
        db, 
        trip_id=trip_id, 
        driver_id=driver_id, 
        incident_status=incident_status
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve details of a specific incident by its UUID.
    """
    return await incident_service.get_incident(db, incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_in: IncidentUpdate,
    # CRITICAL: Only Managers and Admins can update or resolve an incident
    current_user: dict = MANAGER_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an incident (e.g., Manager assigning themselves or resolving the ticket).
    """
    return await incident_service.update_incident(db, incident_id, incident_in)