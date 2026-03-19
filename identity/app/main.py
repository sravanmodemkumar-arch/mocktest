from fastapi import FastAPI
from app.api.v1.auth import router as auth_router

app = FastAPI(
    title="EduForge — Identity Service",
    description="Authentication & user management for EduForge platform",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "identity"}
