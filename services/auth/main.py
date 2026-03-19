"""Auth Service — Lambda function. OTP + JWT only. CDN bypassed for all routes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.v1.auth import router as auth_router

app = FastAPI(
    title="EduForge Auth Service",
    description="OTP authentication and JWT token management",
    version="1.0.0",
    root_path="/auth",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth"}


# Lambda handler
handler = Mangum(app, lifespan="off")
