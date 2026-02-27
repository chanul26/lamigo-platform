"""
LamiGo Incident Endpoints
Handles delivery incident reporting and management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


class IncidentCreate(BaseModel):
    """Schema for creating an incident report."""
    package_id: Optional[int] = None
    driver_id: Optional[int] = None
    incident_type: str
    description: str


class Incident(BaseModel):
    """Schema for incident response."""
    id: int
    package_id: Optional[int] = None
    driver_id: Optional[int] = None
    incident_type: str
    description: str
    status: str = "Open"
    created_at: datetime
    resolved_at: Optional[datetime] = None


MOCK_INCIDENTS: List[Incident] = [
    Incident(
        id=1,
        package_id=4,
        driver_id=3,
        incident_type="Delay",
        description="Traffic congestion on Galle Road causing 30-minute delay",
        status="Open",
        created_at=datetime.now(),
    ),
]


@router.get("/", response_model=List[Incident])
def get_incidents():
    """
    Retrieve all incidents.
    """
    return MOCK_INCIDENTS


@router.get("/{incident_id}", response_model=Incident)
def get_incident(incident_id: int):
    """
    Retrieve a specific incident by ID.
    """
    for incident in MOCK_INCIDENTS:
        if incident.id == incident_id:
            return incident
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Incident not found"
    )


@router.post("/", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentCreate):
    """
    Create a new incident report.
    
    TODO: Implement with database persistence
    """
    new_incident = Incident(
        id=len(MOCK_INCIDENTS) + 1,
        package_id=incident.package_id,
        driver_id=incident.driver_id,
        incident_type=incident.incident_type,
        description=incident.description,
        status="Open",
        created_at=datetime.now(),
    )
    MOCK_INCIDENTS.append(new_incident)
    return new_incident


@router.patch("/{incident_id}/resolve")
def resolve_incident(incident_id: int, resolution: str):
    """
    Mark an incident as resolved.
    
    TODO: Implement with database persistence
    """
    for incident in MOCK_INCIDENTS:
        if incident.id == incident_id:
            incident.status = "Resolved"
            incident.resolved_at = datetime.now()
            return {"status": "success", "message": "Incident resolved"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Incident not found"
    )
