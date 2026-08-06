from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    roles: List[str] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    roles: List[str] = ["OPERATOR"]

class UserResponse(UserBase):
    id: uuid.UUID
    email_verified: bool
    roles: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

# Camera Schemas
class CameraBase(BaseModel):
    name: str
    rtsp_url: str
    location_zone: str
    roi_polygons: dict = {}
    active_detectors: dict = {}

class CameraCreate(CameraBase):
    group_id: Optional[uuid.UUID] = None

class CameraResponse(CameraBase):
    id: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    camera_id: uuid.UUID
    threat_type: str
    severity: str
    confidence: float
    snapshot_url: str
    video_clip_url: Optional[str] = None
    bounding_boxes: dict = {}

class AlertCreate(AlertBase):
    person_id: Optional[uuid.UUID] = None
    license_plate_id: Optional[uuid.UUID] = None

class AlertResponse(AlertBase):
    id: uuid.UUID
    is_acknowledged: bool
    created_at: datetime

    class Config:
        from_attributes = True
