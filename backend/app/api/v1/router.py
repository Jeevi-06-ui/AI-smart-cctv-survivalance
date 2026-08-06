from fastapi import APIRouter
from app.api.v1.endpoints import auth, cameras, alerts, incidents, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Threat Alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["AI Incidents"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Assistant"])
