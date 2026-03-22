from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.sql_models import Incident
from app.models.enums import IncidentStatus
from app.schemas.incident_schemas import IncidentCreate, IncidentUpdate

def _incident_to_dict(incident: Incident) -> dict:
    """Safely converts an Incident model to a dict to prevent MissingGreenlet errors."""
    inc_dict = incident.__dict__.copy()
    inc_dict.pop("_sa_instance_state", None)
    return inc_dict

async def create_incident(db: AsyncSession, incident_in: IncidentCreate) -> dict:
    new_incident = Incident(**incident_in.model_dump())
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    return _incident_to_dict(new_incident)

async def get_all_incidents(
    db: AsyncSession, 
    trip_id: Optional[UUID] = None,
    driver_id: Optional[str] = None,
    incident_status: Optional[IncidentStatus] = None
) -> List[dict]:
    query = select(Incident)
    
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

async def update_incident(db: AsyncSession, incident_id: UUID, incident_in: IncidentUpdate) -> dict:
    result = await db.execute(select(Incident).where(Incident.incident_id == incident_id))
    incident = result.scalars().first()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
        
    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
        
    await db.commit()
    await db.refresh(incident)
    return _incident_to_dict(incident)