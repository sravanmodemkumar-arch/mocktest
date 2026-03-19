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
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()


def verify_otp_hash(otp: str, hashed: str) -> bool:
    return bcrypt.checkpw(otp.encode(), hashed.encode())


async def save_otp(db: AsyncSession, mobile: str, otp: str) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    record = OTP(mobile=mobile, otp_hash=hash_otp(otp), expires_at=expires_at)
    db.add(record)
    await db.commit()


async def validate_otp(db: AsyncSession, mobile: str, otp: str) -> bool:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(OTP)
        .where(OTP.mobile == mobile, OTP.used == False, OTP.expires_at > now)
        .order_by(OTP.created_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if not record or not verify_otp_hash(otp, record.otp_hash):
        return False
    record.used = True
    await db.commit()
    return True
