"""Auth endpoints — send OTP, verify OTP, refresh token."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.auth import SendOTPRequest, VerifyOTPRequest, TokenResponse, RefreshRequest
from app.models.user import User, Session
from app.services.otp import generate_otp, save_otp, validate_otp
from app.services.jwt import create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta, timezone
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/send")
async def send_otp(payload: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """Send OTP via WhatsApp (SMS fallback). Step 1 of login."""
    otp = generate_otp()
    await save_otp(db, payload.mobile, otp)

    # TODO: send via WhatsApp / MSG91
    # For development, return otp in response
    return {"message": "OTP sent", "dev_otp": otp if settings.DEBUG else None}


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP and return JWT tokens. Step 2 of login."""
    valid = await validate_otp(db, payload.mobile, payload.otp)
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")

    # Get or create user
    result = await db.execute(select(User).where(User.mobile == payload.mobile))
    user = result.scalar_one_or_none()
    if not user:
        user = User(mobile=payload.mobile, role="student")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(user.id, user.role, user.institution_id)
    refresh_token = create_refresh_token(user.id)

    # Store refresh token
    session = Session(
        user_id=user.id,
        refresh_token_hash=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )
    db.add(session)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange refresh token for new access token."""
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = int(data["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token = create_access_token(user.id, user.role, user.institution_id)
    new_refresh = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
):
    """Revoke refresh token — invalidate session."""
    data = decode_token(credentials.credentials)
    if not data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(data["sub"])
    # Revoke all sessions for this user (simple approach)
    result = await db.execute(select(Session).where(Session.user_id == user_id, Session.is_revoked == False))
    sessions = result.scalars().all()
    for session in sessions:
        session.is_revoked = True
    await db.commit()
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
):
    """Return current user profile."""
    data = decode_token(credentials.credentials)
    if not data or data.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(data["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "mobile": user.mobile,
        "role": user.role,
        "institution_id": user.institution_id,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }
