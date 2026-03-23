from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import Incident, Trip, IncidentResponseAssignment
from app.models.enums import IncidentStatus, ResponseStatus
from app.schemas.incident_schemas import IncidentCreate, IncidentUpdate, AssignmentCreate, AssignmentUpdate

# --- THE DICTIONARY RULE ENFORCERS ---
def _incident_to_dict(incident: Incident) -> dict:
    inc_dict = incident.__dict__.copy()
    inc_dict.pop("_sa_instance_state", None)
    return inc_dict

def _assignment_to_dict(assignment: IncidentResponseAssignment) -> dict:
    data = assignment.__dict__.copy()
    data.pop("_sa_instance_state", None)
    return data
# -------------------------------------

async def create_incident(db: AsyncSession, incident_in: IncidentCreate, driver_id: str) -> dict:
    # Safely inject the driver_id from the router
    new_incident = Incident(driver_id=driver_id, **incident_in.model_dump())
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return _incident_to_dict(new_incident)

async def get_all_incidents(
    db: AsyncSession, 
    branch_id: Optional[UUID] = None,
    trip_id: Optional[UUID] = None,
    driver_id: Optional[str] = None,
    incident_status: Optional[IncidentStatus] = None
) -> List[dict]:
    # Join the Trip table so we can securely filter incidents by branch_id for Managers
    query = select(Incident).outerjoin(Trip, Incident.trip_id == Trip.trip_id)
    
    if branch_id:
        query = query.where(Trip.branch_id == branch_id)
    if trip_id:
        query = query.where(Incident.trip_id == trip_id)
    if driver_id:
        query = query.where(Incident.driver_id == driver_id)
    if incident_status:
        query = query.where(Incident.status == incident_status)
        
    query = query.order_by(Incident.created_at.desc())
    result = await db.execute(query)
    incidents = result.scalars().all()
    return [_incident_to_dict(inc) for inc in incidents]

async def get_incident(db: AsyncSession, incident_id: UUID) -> dict:
    result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    incident = result.scalars().first()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return _incident_to_dict(incident)

async def update_incident(db: AsyncSession, incident_id: UUID, incident_in: IncidentUpdate, manager_id: str) -> dict:
    result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    incident = result.scalars().first()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
        
    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
        
    # Auto-log which manager handled it and when, preventing spoofing
    if incident_in.status != IncidentStatus.REPORTED and incident.handled_by is None:
        incident.handled_by = manager_id
        incident.handled_at = datetime.now(timezone.utc)
        
    await db.commit()
    await db.refresh(incident)
    return _incident_to_dict(incident)

# ==========================================
# Incident Response Assignments (Rescue Missions)
# ==========================================

async def assign_backup(db: AsyncSession, incident_id: UUID, payload: AssignmentCreate, manager_id: str) -> dict:
    """Creates a rescue mission and assigns it to a backup driver."""
    inc_result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    if not inc_result.scalars().first():
        raise HTTPException(status_code=404, detail="Incident not found.")

    assignment = IncidentResponseAssignment(
        incident_id=incident_id,
        assigned_by=manager_id,
        **payload.model_dump()
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    
    return _assignment_to_dict(assignment)

async def update_assignment_status(db: AsyncSession, assignment_id: UUID, payload: AssignmentUpdate) -> dict:
    """Updates the rescue mission status and auto-logs arrival/completion times."""
    result = await db.execute(select(IncidentResponseAssignment).where(IncidentResponseAssignment.assignment_id == assignment_id))
    assignment = result.scalars().first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found.")

    assignment.status = payload.status
    
    # Auto-handle timestamps so we don't trust the client's clock
    if payload.status == ResponseStatus.ON_SITE and assignment.arrived_at is None:
        assignment.arrived_at = datetime.now(timezone.utc)
    elif payload.status == ResponseStatus.COMPLETED and assignment.completed_at is None:
        assignment.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(assignment)
    return _assignment_to_dict(assignment)