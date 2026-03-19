"""
Local development server — single FastAPI process backed by local_dev.sqlite3.

Implements all API endpoints the portal needs for manual testing:
  - POST /api/v1/auth/login          password-based login
  - GET  /api/v1/auth/me             current user profile
  - POST /api/v1/auth/token/refresh  refresh JWT
  - POST /api/v1/auth/logout         logout
  - GET  /api/v1/tenant/config       tenant config by domain
  - GET  /api/v1/page/home           home page data

Usage:
    python scripts/dev_server.py

Then in another terminal:
    cd portal && python manage.py runserver

All services point to http://localhost:8001 via portal/.env.local
"""
import hashlib
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "local_dev.sqlite3"
JWT_SECRET = "dev-secret-key-not-for-production"
JWT_ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 30
REFRESH_EXPIRE_DAYS = 7

# ── Ensure DB exists ──────────────────────────────────────────────────────────
if not DB_PATH.exists():
    print(f"[ERROR] {DB_PATH} not found. Run: python scripts/seed_local.py")
    sys.exit(1)

# ── JWT helpers ───────────────────────────────────────────────────────────────
from jose import jwt, JWTError  # noqa: E402


def make_access_token(user_id: int, role: str, tenant_id: int | None) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "institution_id": tenant_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def make_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


# ── DB helpers ────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ── FastAPI app ───────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException, Header, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

app = FastAPI(title="EduForge Dev Server", version="dev")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth endpoints ────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    login_id: str
    password: str


@app.post("/api/v1/auth/login")
def login(body: LoginRequest):
    """Password-based login — accepts mobile, email, or username."""
    pw_hash = hash_password(body.password)
    conn = get_db()
    user = conn.execute(
        """SELECT * FROM users WHERE
           (mobile = ? OR email = ? OR username = ?)
           AND password_hash = ? AND is_active = 1""",
        (body.login_id, body.login_id, body.login_id, pw_hash),
    ).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = make_access_token(user["id"], user["role"], user["tenant_id"])
    refresh = make_refresh_token(user["id"])
    return {"access_token": access, "refresh_token": refresh}


@app.get("/api/v1/auth/me")
def get_me(authorization: str = Header(None)):
    """Return current user profile from JWT."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    data = decode(token)
    if not data or data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (int(data["sub"]),)).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user["id"],
        "mobile": user["mobile"],
        "email": user["email"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "institution_id": user["tenant_id"],
        "is_active": bool(user["is_active"]),
        "profile_complete": bool(user["profile_complete"]),
        "requires_2fa": bool(user["requires_2fa"]),
        "has_multiple_roles": bool(user["has_multiple_roles"]),
        "subscription": user["subscription"],
    }


class RefreshRequest(BaseModel):
    refresh_token: str


@app.post("/api/v1/auth/token/refresh")
def refresh_token(body: RefreshRequest):
    data = decode(body.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ? AND is_active = 1", (int(data["sub"]),)
    ).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = make_access_token(user["id"], user["role"], user["tenant_id"])
    new_refresh = make_refresh_token(user["id"])
    return {"access_token": access, "refresh_token": new_refresh}


@app.post("/api/v1/auth/logout")
def logout():
    return {"message": "Logged out"}


# ── Tenant endpoint ───────────────────────────────────────────────────────────

@app.get("/api/v1/tenant/config")
def tenant_config(domain: str = Query("localhost")):
    """Return tenant branding by domain."""
    conn = get_db()
    # Exact match first, then subdomain match, then default
    tenant = (
        conn.execute("SELECT * FROM tenants WHERE domain = ? AND is_active = 1", (domain,)).fetchone()
        or conn.execute("SELECT * FROM tenants WHERE slug = 'default' AND is_active = 1").fetchone()
    )
    conn.close()

    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "slug": tenant["slug"],
        "name": tenant["name"],
        "portal_group": tenant["portal_group"],
        "domain": tenant["domain"],
        "branding": {
            "primary": tenant["primary_color"] or "#1565C0",
            "logo": tenant["logo_url"] or "",
        },
        "features": {},
        "auth_methods": ["password"],
    }


# ── Home data endpoint ────────────────────────────────────────────────────────

def _build_home_data(portal_group: int, role: str, subscription: str) -> dict:
    """Return sample home data matching what the portal templates expect."""
    now = datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

    base = {
        "portal_group": portal_group,
        "data": {
            "greeting": {"title": greeting, "subtitle": ""},
            "kpis": [],
            "alerts": [],
            "sections": [],
        },
    }

    if portal_group == 6:  # Exam domain
        base["data"]["kpis"] = [
            {"id": "sessions_month", "label": "Sessions This Month", "value": "12",
             "sub": "/30 limit" if subscription == "free" else "Unlimited", "icon": "📚"},
            {"id": "best_air", "label": "Best AIR", "value": "3,421",
             "sub": "Top 5% nationally", "icon": "🏆"},
            {"id": "streak", "label": "Study Streak", "value": "7 days",
             "sub": "Strong — keep going!", "icon": "🔥"},
        ]
        base["data"]["sections"] = [
            {"id": "today_schedule", "criticality": "high"},
            {"id": "kpi_bar", "criticality": "medium"},
        ]
        if subscription == "free":
            base["data"]["sections"].append({"id": "upgrade_banner", "criticality": "static"})
            base["data"]["upgrade_banner"] = {
                "heading": "Unlock your full potential",
                "subheading": "Join 4.8M aspirants on Premium",
                "price_monthly": 299,
                "price_annual": 2499,
                "features": [
                    "Unlimited mock tests",
                    "AI-powered weak topic analysis",
                    "Live doubt sessions",
                    "Previous year papers (10 years)",
                ],
            }

    elif portal_group == 3:  # School
        base["data"]["kpis"] = [
            {"id": "attendance", "label": "Today's Attendance", "value": "94%", "icon": "📋"},
            {"id": "fee_pending", "label": "Fee Pending", "value": "₹12,400", "icon": "💰"},
            {"id": "alerts", "label": "Pending Alerts", "value": "3", "icon": "🔔"},
        ]
        base["data"]["sections"] = [
            {"id": "attendance", "criticality": "high"},
            {"id": "alerts", "criticality": "critical"},
        ]
        if role == "teacher":
            base["data"]["today_schedule"] = [
                {"time": "09:00", "class": "Grade 10A", "subject": "Mathematics"},
                {"time": "10:30", "class": "Grade 11B", "subject": "Physics"},
                {"time": "12:00", "class": "Grade 10C", "subject": "Mathematics"},
            ]

    elif portal_group == 1:  # Platform admin
        base["data"]["kpis"] = [
            {"id": "institutions", "label": "Active Institutions", "value": "12,483", "icon": "🏫"},
            {"id": "users", "label": "Total Users", "value": "3.2M", "icon": "👥"},
            {"id": "uptime", "label": "Platform Uptime", "value": "99.8%", "icon": "⚡"},
        ]

    return base


@app.get("/api/v1/page/home")
def home_data(
    authorization: str = Header(None),
    x_portal_group: str = Header("1", alias="X-Portal-Group"),
    x_user_role: str = Header("student", alias="X-User-Role"),
    x_tenant_slug: str = Header("default", alias="X-Tenant-Slug"),
):
    """Return home page data for the portal group."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    data = decode(token)
    if not data or data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (int(data["sub"]),)).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    portal_group = int(x_portal_group or 1)
    return _build_home_data(portal_group, user["role"], user["subscription"] or "free")


@app.get("/health")
def health():
    return {"status": "ok", "service": "dev-server", "db": str(DB_PATH)}


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn  # noqa: E402

    print("=" * 60)
    print("EduForge Local Dev Server")
    print("=" * 60)
    print(f"DB:      {DB_PATH}")
    print(f"API:     http://localhost:8001")
    print(f"Docs:    http://localhost:8001/docs")
    print()
    print("Test accounts (all password: Test@1234)")
    print("  SSC Student (free):   aspirant1")
    print("  SSC Student (premium): +919876543211")
    print("  School Teacher:        teacher@greenwood.com")
    print("  School Principal:      +910000000003")
    print("  Platform Admin:        platform@eduforge.in")
    print("=" * 60)
    print()

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
