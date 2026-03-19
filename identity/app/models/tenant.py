"""Tenant model — maps custom domains to EduForge institutions."""
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # e.g. "xyz-school"
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("identity.institutions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    portal_group: Mapped[int] = mapped_column()  # 1-10 matching group number
    branding: Mapped[dict] = mapped_column(JSON, default=dict)  # logo_url, primary_color, etc.
    features: Mapped[dict] = mapped_column(JSON, default=dict)  # feature flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    domains: Mapped[list["TenantDomain"]] = relationship(back_populates="tenant")


class TenantDomain(Base):
    __tablename__ = "tenant_domains"
    __table_args__ = {"schema": "identity"}

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("identity.tenants.id"))
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # www.school.com
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship(back_populates="domains")
