"""Tenant Service — domain to portal config resolution.
CDN caches for 1hr (web). Mobile caches locally. No auth needed — pre-login data.

Static assets (logo, favicon, brand colors) are stored in:
  S3/static/tenants/{tenant-slug}/brand.json
  S3/static/tenants/{tenant-slug}/logo.svg
  S3/static/tenants/{tenant-slug}/favicon.ico

CDN URL: https://cdn.eduforge.in/static/tenants/{slug}/
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
import os, sys, json
import asyncpg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.client import detect_client, is_mobile

DATABASE_URL = os.getenv("DATABASE_URL", "")
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "https://cdn.eduforge.in")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "tenants")


def static_assets(slug: str) -> dict:
    """Return CDN URLs for tenant static assets.
    Falls back to 'default' if tenant folder doesn't exist on CDN.
    Reads brand.json from local static folder for dev; CDN serves in production.
    """
    cdn_base = f"{CDN_BASE_URL}/static/tenants/{slug}"
    brand_path = os.path.join(STATIC_DIR, slug, "brand.json")

    # Load brand.json if present (local dev)
    brand = {}
    if os.path.exists(brand_path):
        with open(brand_path) as f:
            brand = json.load(f)
    else:
        # Fallback to default
        default_path = os.path.join(STATIC_DIR, "default", "brand.json")
        if os.path.exists(default_path):
            with open(default_path) as f:
                brand = json.load(f)

    colors = brand.get("colors", {})
    return {
        "primary": colors.get("primary", "#1A237E"),
        "primary_dark": colors.get("primary_dark", "#0D1B6E"),
        "accent": colors.get("accent", "#FF6F00"),
        "background": colors.get("background", "#FFFFFF"),
        "surface": colors.get("surface", "#F5F7FA"),
        "text": colors.get("text", "#1A1A2E"),
        "text_muted": colors.get("text_muted", "#6B7280"),
        "success": colors.get("success", "#2E7D32"),
        "warning": colors.get("warning", "#F57F17"),
        "error": colors.get("error", "#C62828"),
        # CDN URLs — frontend/mobile use these directly (never hardcode paths)
        "logo": f"{cdn_base}/logo.svg",
        "logo_dark": f"{cdn_base}/logo-dark.svg",
        "favicon": f"{cdn_base}/favicon.ico",
        "og_image": f"{cdn_base}/og-image.png",
        "pwa_icon_192": f"{cdn_base}/favicon-192.png",
        "pwa_icon_512": f"{cdn_base}/favicon-512.png",
        # Font
        "font_family": brand.get("font", {}).get("family", "Inter"),
    }


app = FastAPI(
    title="EduForge Tenant Service",
    description="Domain → tenant config — CDN cached 1hr, mobile cached locally",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["X-Client-Type", "X-App-Version", "If-None-Match"],
)

FIRST_PARTY_DOMAINS = {
    "admin.eduforge.in": {
        "slug": "platform-admin",
        "group": 1,
        "name": "EduForge Admin",
    },
    "app.eduforge.in": {"slug": "chain-admin", "group": 2, "name": "EduForge Chain"},
    "ssc.eduforge.in": {"slug": "ssc-domain", "group": 6, "name": "EduForge SSC"},
    "rrb.eduforge.in": {"slug": "rrb-domain", "group": 6, "name": "EduForge RRB"},
    "upsc.eduforge.in": {"slug": "upsc-domain", "group": 6, "name": "EduForge UPSC"},
    "banking.eduforge.in": {
        "slug": "banking-domain",
        "group": 6,
        "name": "EduForge Banking",
    },
    "ap.eduforge.in": {"slug": "ap-board", "group": 6, "name": "EduForge AP"},
    "ts.eduforge.in": {"slug": "ts-board", "group": 6, "name": "EduForge Telangana"},
    "partners.eduforge.in": {
        "slug": "partner-portal",
        "group": 9,
        "name": "EduForge Partners",
    },
    "student.eduforge.in": {
        "slug": "student-unified",
        "group": 10,
        "name": "EduForge Student",
    },
    "parent.eduforge.in": {
        "slug": "parent-portal",
        "group": 8,
        "name": "EduForge Parent",
    },
    "localhost": {"slug": "default", "group": 1, "name": "Local Dev"},
    "127.0.0.1": {"slug": "default", "group": 1, "name": "Local Dev"},
}


@app.get("/api/v1/tenant/config")
async def get_tenant_config(domain: str, request: Request):
    """
    ONE pre-login call — returns ALL tenant config needed to render login screen.
    Includes CDN URLs for logo, favicon, and brand colors from static/tenants/{slug}/.

    Web:    CDN caches 1hr by ?domain= param.
    Mobile: Cached locally (24hr), busted on app version update.
    """
    client = detect_client(request)
    domain = domain.lower().split(":")[0]

    if domain in FIRST_PARTY_DOMAINS:
        cfg = FIRST_PARTY_DOMAINS[domain]
        slug = cfg["slug"]
        body = {
            "slug": slug,
            "portal_group": cfg["group"],
            "name": cfg["name"],
            # Assets loaded from static/tenants/{slug}/ — CDN served
            "branding": static_assets(slug),
            "features": {},
            "auth_methods": ["whatsapp_otp", "sms_otp"],
            "domain_type": "first_party",
        }
        response = JSONResponse(content=body)
        if is_mobile(client):
            response.headers["Cache-Control"] = (
                "private, max-age=86400, stale-while-revalidate=3600"
            )
            response.headers["Vary"] = "X-Client-Type, X-App-Version"
        else:
            response.headers["Cache-Control"] = (
                "public, s-maxage=3600, stale-while-revalidate=300"
            )
            response.headers["Vary"] = "Accept-Encoding"
        return response

    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        conn = await asyncpg.connect(DATABASE_URL)
        row = await conn.fetchrow(
            """
            SELECT t.slug, t.portal_group, t.name, t.branding, t.features, t.is_active
            FROM identity.tenant_domains td
            JOIN identity.tenants t ON t.id = td.tenant_id
            WHERE td.domain = $1 AND td.is_verified = true
        """,
            domain,
        )
        await conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="Configuration service unavailable")

    if not row:
        raise HTTPException(
            status_code=404, detail=f"Domain '{domain}' not registered with EduForge"
        )
    if not row["is_active"]:
        raise HTTPException(status_code=503, detail="This portal is currently inactive")

    slug = row["slug"]
    # Merge: DB branding overrides static defaults (institution can store custom colors in DB)
    merged_branding = static_assets(slug)
    if row["branding"]:
        merged_branding.update(row["branding"])

    body = {
        "slug": slug,
        "portal_group": row["portal_group"],
        "name": row["name"],
        "branding": merged_branding,
        "features": row["features"] or {},
        "auth_methods": ["whatsapp_otp", "sms_otp"],
        "domain_type": "custom",
    }
    response = JSONResponse(content=body)
    if is_mobile(client):
        response.headers["Cache-Control"] = (
            "private, max-age=86400, stale-while-revalidate=3600"
        )
        response.headers["Vary"] = "X-Client-Type, X-App-Version"
    else:
        response.headers["Cache-Control"] = (
            "public, s-maxage=3600, stale-while-revalidate=300"
        )
        response.headers["Vary"] = "Accept-Encoding"
    return response


@app.get("/health")
async def health():
    return {"status": "ok", "service": "tenant"}


handler = Mangum(app, lifespan="off")
