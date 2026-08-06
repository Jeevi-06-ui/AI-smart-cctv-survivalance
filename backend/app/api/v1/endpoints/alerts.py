from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.domain.models.database import Alert
from app.domain.schemas.auth_schema import AlertCreate, AlertResponse

router = APIRouter()

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    threat_type: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    query = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    if threat_type:
        query = query.where(Alert.threat_type == threat_type)
    if severity:
        query = query.where(Alert.severity == severity)
    if acknowledged is not None:
        query = query.where(Alert.is_acknowledged == acknowledged)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=AlertResponse)
async def create_alert(alert_in: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = Alert(
        camera_id=alert_in.camera_id,
        person_id=alert_in.person_id,
        license_plate_id=alert_in.license_plate_id,
        threat_type=alert_in.threat_type,
        severity=alert_in.severity,
        confidence=alert_in.confidence,
        snapshot_url=alert_in.snapshot_url,
        video_clip_url=alert_in.video_clip_url,
        bounding_boxes=alert_in.bounding_boxes,
        is_acknowledged=False
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert

@router.post("/{alert_id}/ack", response_model=AlertResponse)
async def acknowledge_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalars().first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = True
    await db.commit()
    await db.refresh(alert)
    return alert
