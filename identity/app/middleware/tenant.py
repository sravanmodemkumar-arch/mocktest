"""Tenant middleware — resolves incoming Host header to a tenant config."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from app.database import SessionLocal
from app.models.tenant import Tenant, TenantDomain

# EduForge's own domains — skip tenant resolution for these
PLATFORM_DOMAINS = {
    "api.eduforge.in",
    "admin.eduforge.in",
    "partners.eduforge.in",
    "student.eduforge.in",
    "parent.eduforge.in",
    "localhost",
    "127.0.0.1",
}

# Map EduForge subdomain → portal group
EDUFORGE_SUBDOMAIN_MAP = {
    "admin.eduforge.in": {"group": 1, "slug": "platform-admin"},
    "app.eduforge.in": {"group": 2, "slug": "chain-admin"},
    "ssc.eduforge.in": {"group": 6, "slug": "ssc-domain"},
    "rrb.eduforge.in": {"group": 6, "slug": "rrb-domain"},
    "upsc.eduforge.in": {"group": 6, "slug": "upsc-domain"},
    "banking.eduforge.in": {"group": 6, "slug": "banking-domain"},
    "ap.eduforge.in": {"group": 6, "slug": "ap-board"},
    "ts.eduforge.in": {"group": 6, "slug": "ts-board"},
    "partners.eduforge.in": {"group": 9, "slug": "partner-portal"},
    "student.eduforge.in": {"group": 10, "slug": "student-unified"},
    "parent.eduforge.in": {"group": 8, "slug": "parent-portal"},
}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0].lower()

        # Skip tenant resolution for health + docs
        if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        # EduForge subdomain — resolve from map
        if host in EDUFORGE_SUBDOMAIN_MAP:
            info = EDUFORGE_SUBDOMAIN_MAP[host]
            request.state.tenant = {
                "slug": info["slug"],
                "portal_group": info["group"],
                "branding": {},
                "features": {},
                "domain": host,
            }
            return await call_next(request)

        # localhost / platform domains — set default tenant
        if host in PLATFORM_DOMAINS or host == "":
            request.state.tenant = {
                "slug": "localhost",
                "portal_group": 1,
                "branding": {},
                "features": {},
                "domain": host,
            }
            return await call_next(request)

        # Custom domain (e.g. www.school.com) — look up in DB
        async with SessionLocal() as db:
            result = await db.execute(
                select(TenantDomain).where(TenantDomain.domain == host)
            )
            td = result.scalar_one_or_none()

            if not td:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Domain '{host}' is not registered with EduForge."},
                )

            tenant_result = await db.execute(
                select(Tenant).where(Tenant.id == td.tenant_id, Tenant.is_active == True)
            )
            tenant = tenant_result.scalar_one_or_none()

            if not tenant:
                return JSONResponse(
                    status_code=503,
                    content={"detail": "This portal is currently inactive. Contact your administrator."},
                )

            request.state.tenant = {
                "id": tenant.id,
                "slug": tenant.slug,
                "portal_group": tenant.portal_group,
                "branding": tenant.branding,
                "features": tenant.features,
                "domain": host,
            }

        return await call_next(request)
