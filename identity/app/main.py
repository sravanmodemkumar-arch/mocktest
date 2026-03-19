from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.home import router as home_router
from app.middleware.tenant import TenantMiddleware

app = FastAPI(
    title="EduForge — Identity Service",
    description="Authentication & user management for EduForge platform",
    version="1.0.0",
)

app.add_middleware(TenantMiddleware)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(home_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "identity"}
