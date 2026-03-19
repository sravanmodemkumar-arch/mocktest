from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(100), unique=True)
    institution_type: Mapped[str] = mapped_column(String(50))  # school|college|coaching|ssc|rrb|state_board
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users: Mapped[list["User"]] = relationship(back_populates="institution")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("identity.institutions.id"), nullable=True)
    mobile: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(50))  # student|staff|admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    institution: Mapped["Institution | None"] = relationship(back_populates="users")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")


class OTP(Base):
    """Replaces Redis for OTP storage."""
    __tablename__ = "otps"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    mobile: Mapped[str] = mapped_column(String(15), index=True)
    otp_hash: Mapped[str] = mapped_column(String(255))  # bcrypt hash — plain OTP never stored
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Session(Base):
    """Stores refresh tokens only. Access tokens are stateless JWT."""
    __tablename__ = "sessions"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("identity.users.id"))
    refresh_token_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="sessions")
