import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.domain.models.database import Base
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    print("[GuardianAI Backend] Starting FastAPI Server...")
    # Initialize DB Tables if not created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[GuardianAI Backend] Database tables synchronized successfully.")

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs": "/docs"
    }

# Active WebSocket Connection Registry
active_connections: list[WebSocket] = []

@app.websocket("/ws/v1/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keepalive ping/pong
            data = await websocket.receive_text()
            await websocket.send_text(f"PONG: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
