from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, RoleChecker
from app.models.enums import UserRole, IncidentStatus
from app.schemas.incident_schemas import IncidentCreate, IncidentUpdate, IncidentResponse
from app.services import incident_service

router = APIRouter()

MANAGER_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER]))
ALL_ACCESS = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.STATION_MANAGER, UserRole.DRIVER]))

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await incident_service.create_incident(db, incident_in)

@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    trip_id: Optional[UUID] = Query(None, description="Filter by a specific trip"),
    driver_id: Optional[str] = Query(None, description="Filter by a specific driver"),
    incident_status: Optional[IncidentStatus] = Query(None, description="Filter by state (e.g., REPORTED, RESOLVED)"),
    current_user: dict = ALL_ACCESS,
    db: AsyncSession = Depends(get_db)
):
    return await incident_service.get_all_incidents(
        db, trip_id=trip_id, driver_id=driver_id, incident_status=incident_status
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
    return await incident_service.update_incident(db, incident_id, incident_in)