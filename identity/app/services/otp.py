"""OTP service — generate, hash, verify. No Redis needed."""
import random
import bcrypt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import OTP
from app.config import settings


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def hash_otp(otp: str) -> str:
    if not otp:
        raise ValueError("OTP must not be empty")
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()


def verify_otp_hash(otp: str, hashed: str) -> bool:
    return bcrypt.checkpw(otp.encode(), hashed.encode())


async def save_otp(db: AsyncSession, mobile: str, otp: str) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    record = OTP(mobile=mobile, otp_hash=hash_otp(otp), expires_at=expires_at)
    db.add(record)
    await db.commit()


async def get_latest_otp(db: AsyncSession, mobile: str) -> OTP | None:
    """Fetch the most recent non-used OTP record for a mobile number."""
    result = await db.execute(
        select(OTP)
        .where(OTP.mobile == mobile)
        .order_by(OTP.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def count_recent_otps(db: AsyncSession, mobile: str) -> int:
    """Count OTPs sent for a mobile in the last 30 minutes."""
    from sqlalchemy import func
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)
    result = await db.execute(
        select(func.count()).select_from(OTP).where(
            OTP.mobile == mobile,
            OTP.created_at > cutoff,
        )
    )
    return result.scalar_one()


async def check_rate_limit(db: AsyncSession, mobile: str) -> None:
    """Raise HTTP 429 if mobile has exceeded 5 OTP requests in 30 minutes."""
    from fastapi import HTTPException
    count = await count_recent_otps(db, mobile)
    if count >= 5:
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")


async def validate_otp(db: AsyncSession, mobile: str, otp: str) -> bool:
    now = datetime.now(timezone.utc)
    record = await get_latest_otp(db, mobile)
    if record is None:
        return False
    if record.used or record.expires_at.replace(tzinfo=timezone.utc) <= now:
        return False
    if not verify_otp_hash(otp, record.otp_hash):
        return False
    record.used = True
    await db.commit()
    return True
