from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import Incident
from app.models.enums import IncidentStatus
from app.schemas.incident_schemas import IncidentCreate, IncidentUpdate

async def create_incident(db: AsyncSession, incident_in: IncidentCreate) -> Incident:
    """Creates a new emergency Incident reported by a driver."""
    new_incident = Incident(**incident_in.model_dump())
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return new_incident


async def get_all_incidents(
    db: AsyncSession, 
    trip_id: Optional[UUID] = None,
    driver_id: Optional[str] = None,
    incident_status: Optional[IncidentStatus] = None
) -> List[Incident]:
    """Fetches all incidents with powerful query parameter filtering."""
    query = select(Incident)
    
    # Optional Filters for the Station Manager Dashboard
    if trip_id:
        query = query.where(Incident.trip_id == trip_id)
    if driver_id:
        query = query.where(Incident.driver_id == driver_id)
    if incident_status:
        query = query.where(Incident.status == incident_status)
        
    # CRITICAL: Always return the newest incidents first so emergencies are at the top
    query = query.order_by(Incident.created_at.desc())
        
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_incident(db: AsyncSession, incident_id: UUID) -> Incident:
    """Fetches a specific incident by its UUID."""
    result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    incident = result.scalars().first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Incident not found"
        )
    return incident


async def update_incident(db: AsyncSession, incident_id: UUID, incident_in: IncidentUpdate) -> Incident:
    """Updates an incident (e.g., manager taking responsibility or resolving it)."""
    incident = await get_incident(db, incident_id)
    
    # exclude_unset=True ensures we ONLY update the fields sent in the request
    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
        
    await db.commit()
    await db.refresh(incident)
    return incident