from typing import List, Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.domain.models.database import Incident

router = APIRouter()

class IncidentCreate(BaseModel):
    title: str
    description: str
    priority: str = "HIGH"
    assigned_to_user_id: Optional[uuid.UUID] = None
    timeline_events: dict = {}

class IncidentResponse(IncidentCreate):
    id: uuid.UUID
    incident_code: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=IncidentResponse)
async def create_incident(inc_in: IncidentCreate, db: AsyncSession = Depends(get_db)):
    code = f"INC-{int(datetime.utcnow().timestamp())}"
    incident = Incident(
        incident_code=code,
        title=inc_in.title,
        description=inc_in.description,
        priority=inc_in.priority,
        assigned_to_user_id=inc_in.assigned_to_user_id,
        timeline_events=inc_in.timeline_events,
        status="OPEN"
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident
