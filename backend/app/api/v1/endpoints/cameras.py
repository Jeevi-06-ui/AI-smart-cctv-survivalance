from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.domain.models.database import Camera
from app.domain.schemas.auth_schema import CameraCreate, CameraResponse

router = APIRouter()

@router.get("", response_model=List[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera))
    return result.scalars().all()

@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(camera_in: CameraCreate, db: AsyncSession = Depends(get_db)):
    camera = Camera(
        name=camera_in.name,
        rtsp_url=camera_in.rtsp_url,
        location_zone=camera_in.location_zone,
        group_id=camera_in.group_id,
        roi_polygons=camera_in.roi_polygons,
        active_detectors=camera_in.active_detectors,
        status="ONLINE"
    )
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return camera

@router.put("/{camera_id}/roi", response_model=CameraResponse)
async def update_camera_roi(camera_id: uuid.UUID, roi_polygons: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalars().first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    camera.roi_polygons = roi_polygons
    await db.commit()
    await db.refresh(camera)
    return camera
