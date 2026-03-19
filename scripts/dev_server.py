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
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (int(data["sub"]),)
    ).fetchone()
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
        conn.execute(
            "SELECT * FROM tenants WHERE domain = ? AND is_active = 1", (domain,)
        ).fetchone()
        or conn.execute(
            "SELECT * FROM tenants WHERE slug = 'default' AND is_active = 1"
        ).fetchone()
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
    """Return sample home data for all portal groups (1–10 except 8)."""
    now = datetime.now()
    hour = now.hour
    greeting = (
        "Good morning"
        if hour < 12
        else ("Good afternoon" if hour < 17 else "Good evening")
    )

    data: dict = {
        "greeting": {"title": greeting, "subtitle": ""},
        "kpis": [],
        "alerts": [],
        "sections": [],
        "user": {"name": "Demo User", "role_display": role.replace("_", " ").title()},
    }

    # ── Group 1: Platform Admin ───────────────────────────────────────────────
    if portal_group == 1:
        data["kpis"] = [
            {
                "label": "Active Institutions",
                "value": "12,483",
                "trend": "+24 this week",
            },
            {"label": "Total Users", "value": "32,14,890", "trend": "+1,240 today"},
            {"label": "Platform Uptime", "value": "99.8%", "trend": "Last 30 days"},
        ]
        data["services"] = [
            {"name": "Auth Service", "status": "ok"},
            {"name": "Home Service", "status": "ok"},
            {"name": "Tenant Service", "status": "ok"},
            {"name": "CDN / Edge", "status": "ok"},
            {"name": "Database (Primary)", "status": "ok"},
        ]
        data["recent_insts"] = [
            {
                "name": "Delhi Public School — Rohini",
                "type": "school",
                "registered_at": "2 hrs ago",
            },
            {
                "name": "Sunrise B.Ed College",
                "type": "college",
                "registered_at": "5 hrs ago",
            },
            {
                "name": "Victory IAS Academy",
                "type": "coaching",
                "registered_at": "Yesterday",
            },
        ]
        data["alerts"] = [
            {"message": "3 institutions pending KYC verification"},
            {"message": "Scheduled maintenance: Sunday 02:00–04:00 IST"},
        ]

    # ── Group 2: Chain Admin ──────────────────────────────────────────────────
    elif portal_group == 2:
        data["kpis"] = [
            {"label": "Total Branches", "value": "14", "trend": "+2 this year"},
            {"label": "Total Students", "value": "18,420", "trend": "+340 this month"},
            {
                "label": "Avg Attendance",
                "value": "91.4%",
                "trend": "↑ 1.2% vs last week",
            },
        ]
        data["branches"] = [
            {
                "id": 1,
                "name": "EduForge — Connaught Place",
                "student_count": 2340,
                "staff_count": 84,
                "attendance_pct": "93%",
                "status": "active",
            },
            {
                "id": 2,
                "name": "EduForge — Dwarka",
                "student_count": 1980,
                "staff_count": 71,
                "attendance_pct": "89%",
                "status": "active",
            },
            {
                "id": 3,
                "name": "EduForge — Noida Sector 62",
                "student_count": 1560,
                "staff_count": 58,
                "attendance_pct": "94%",
                "status": "active",
            },
            {
                "id": 4,
                "name": "EduForge — Gurugram DLF",
                "student_count": 2100,
                "staff_count": 76,
                "attendance_pct": "88%",
                "status": "review",
            },
        ]
        data["alerts"] = [
            {"message": "Gurugram branch attendance below 90% for 3 consecutive days"},
            {"message": "Chain-wide fee collection report ready for download"},
        ]

    # ── Group 3: School ───────────────────────────────────────────────────────
    elif portal_group == 3:
        data["kpis"] = [
            {
                "label": "Today's Attendance",
                "value": "94%",
                "trend": "892 / 948 students",
            },
            {"label": "Fee Collected", "value": "₹8.4L", "trend": "82% of target"},
            {"label": "Pending Alerts", "value": "3", "trend": "Needs attention"},
        ]
        data["alerts"] = [
            {
                "message": "Parent-Teacher Meeting scheduled on Friday",
                "action_label": "View Details",
                "action_url": "#",
            },
            {
                "message": "Annual Day registrations close in 2 days",
                "action_label": "Manage",
                "action_url": "#",
            },
            {
                "message": "2 staff leave requests pending approval",
                "action_label": "Review",
                "action_url": "#",
            },
        ]
        if role == "teacher":
            data["today_schedule"] = [
                {
                    "time": "08:30",
                    "class": "Grade 10A",
                    "subject": "Mathematics",
                    "room": "Room 12",
                },
                {
                    "time": "10:00",
                    "class": "Grade 11B",
                    "subject": "Physics",
                    "room": "Lab 2",
                },
                {
                    "time": "11:30",
                    "class": "Grade 9C",
                    "subject": "Mathematics",
                    "room": "Room 7",
                },
                {
                    "time": "14:00",
                    "class": "Grade 12A",
                    "subject": "Calculus",
                    "room": "Room 15",
                },
            ]
        elif role == "parent":
            data["ward"] = {
                "name": "Aryan Verma",
                "class": "Grade 10A",
                "attendance_today": "Present",
                "recent_marks": "85/100 (Maths)",
                "fee_due": "₹4,200 due by 31st",
            }

    # ── Group 4: College ──────────────────────────────────────────────────────
    elif portal_group == 4:
        data["kpis"] = [
            {
                "label": "Today's Attendance",
                "value": "87%",
                "trend": "1,240 / 1,424 students",
            },
            {"label": "Faculty on Duty", "value": "94%", "trend": "62 / 66 faculty"},
            {"label": "Exam Results Pending", "value": "2", "trend": "Upload required"},
        ]
        data["depts"] = [
            {"name": "Computer Science", "pct": "91%"},
            {"name": "Electronics", "pct": "88%"},
            {"name": "Mechanical", "pct": "84%"},
            {"name": "Civil", "pct": "79%"},
        ]
        data["dept_stats"] = {
            "attendance_today": "87%",
            "student_count": 1424,
            "faculty_count": 66,
        }
        data["classes"] = [
            {
                "id": 1,
                "time": "09:00",
                "subject": "Data Structures",
                "class_name": "CS-3A",
                "room": "LH-4",
                "faculty": "Dr. Mehta",
            },
            {
                "id": 2,
                "time": "10:30",
                "subject": "Digital Electronics",
                "class_name": "EC-2B",
                "room": "LH-7",
                "faculty": "Prof. Iyer",
            },
            {
                "id": 3,
                "time": "12:00",
                "subject": "Thermodynamics",
                "class_name": "ME-4A",
                "room": "LH-2",
                "faculty": "Dr. Sharma",
            },
            {
                "id": 4,
                "time": "14:00",
                "subject": "Fluid Mechanics",
                "class_name": "CE-3A",
                "room": "LH-10",
                "faculty": "Dr. Kulkarni",
            },
        ]
        data["items"] = [
            {"label": "Exam Schedule", "value": "Mid-Sem: Apr 14–22"},
            {"label": "Next Holiday", "value": "Ram Navami — Apr 17"},
            {"label": "Fee Deadline", "value": "Semester fee due Apr 10"},
        ]
        data["alerts"] = [
            {
                "message": "Internal marks upload due by Apr 8",
                "action_label": "Upload Now",
                "action_url": "#",
            },
        ]

    # ── Group 5: Coaching ─────────────────────────────────────────────────────
    elif portal_group == 5:
        data["kpis"] = [
            {
                "label": "Active Batches",
                "value": "12",
                "trend": "3 batches starting next week",
            },
            {"label": "Students Enrolled", "value": "1,840", "trend": "+60 this month"},
            {
                "label": "Avg Test Score",
                "value": "68.4%",
                "trend": "↑ 3.2% vs last month",
            },
        ]
        data["batches"] = [
            {"name": "SSC CGL Morning", "student_count": 240, "avg_score": "72%"},
            {"name": "SSC CHSL Evening", "student_count": 180, "avg_score": "65%"},
            {"name": "RRB NTPC Weekend", "student_count": 320, "avg_score": "70%"},
            {"name": "Banking Morning", "student_count": 200, "avg_score": "68%"},
        ]
        data["classes"] = [
            {
                "id": 1,
                "time": "07:00",
                "subject": "Quantitative Aptitude",
                "batch": "SSC CGL Morning",
                "room": "Hall A",
                "faculty": "Rajesh Sir",
            },
            {
                "id": 2,
                "time": "09:30",
                "subject": "English Grammar",
                "batch": "SSC CHSL Evening",
                "room": "Hall B",
                "faculty": "Priya Ma'am",
            },
            {
                "id": 3,
                "time": "11:00",
                "subject": "General Awareness",
                "batch": "RRB NTPC Weekend",
                "room": "Hall C",
                "faculty": "Anand Sir",
            },
            {
                "id": 4,
                "time": "14:00",
                "subject": "Reasoning",
                "batch": "Banking Morning",
                "room": "Hall A",
                "faculty": "Meena Ma'am",
            },
        ]
        data["tests"] = [
            {
                "name": "SSC CGL Full Mock #12",
                "date": "Mar 15",
                "score": "142/200",
                "rank": "8 / 240",
            },
            {
                "name": "Reasoning Sprint #6",
                "date": "Mar 12",
                "score": "48/60",
                "rank": "12 / 240",
            },
            {
                "name": "GK Weekly #9",
                "date": "Mar 10",
                "score": "35/50",
                "rank": "5 / 320",
            },
        ]
        data["alerts"] = [
            {"message": "New batch 'UPSC Prelim Foundation' starts April 1"},
        ]

    # ── Group 6: Exam Domain ──────────────────────────────────────────────────
    elif portal_group == 6:
        data["kpis"] = [
            {
                "label": "Sessions This Month",
                "value": "12",
                "sub": "/30 limit" if subscription == "free" else "Unlimited",
                "icon": "📚",
                "trend": "",
            },
            {
                "label": "Best AIR",
                "value": "3,421",
                "sub": "Top 5% nationally",
                "icon": "🏆",
                "trend": "",
            },
            {
                "label": "Study Streak",
                "value": "7 days",
                "sub": "Strong — keep going!",
                "icon": "🔥",
                "trend": "",
            },
        ]
        data["best_air"] = "3,421"
        data["last_month_tests"] = 18
        data["live_tests"] = [
            {
                "name": "SSC CGL Tier-I Full Mock #24",
                "url": "#",
                "remaining": "1h 20m",
                "attempts": 2840,
            },
            {
                "name": "RRB NTPC CBT-1 Sprint #8",
                "url": "#",
                "remaining": "45m",
                "attempts": 1240,
            },
        ]
        data["results"] = [
            {
                "test_name": "SSC CGL Mock #23",
                "score": "142/200",
                "score_label": "71%",
                "air": 3421,
                "date": "Mar 18",
                "analysis_url": "#",
            },
            {
                "test_name": "Quant Sprint #11",
                "score": "48/60",
                "score_label": "80%",
                "air": 890,
                "date": "Mar 16",
                "analysis_url": "#",
            },
            {
                "test_name": "GK Weekly #14",
                "score": "35/50",
                "score_label": "70%",
                "air": 2100,
                "date": "Mar 14",
                "analysis_url": "#",
            },
        ]
        data["ai_recommendation"] = {
            "title": "Focus on Simplification & Approximation",
            "reason": "Your accuracy dropped from 78% → 61% over the last 3 tests",
            "url": "#",
        }
        data["focus_areas"] = [
            {"topic": "Number System", "accuracy": 82},
            {"topic": "Simplification", "accuracy": 61},
            {"topic": "Time & Work", "accuracy": 74},
            {"topic": "Reading Comprehension", "accuracy": 38},
            {"topic": "Static GK", "accuracy": 55},
        ]
        data["alerts"] = [
            {
                "message": "SSC CGL 2024 Notification out — Apply by Apr 15",
                "action_label": "View",
                "action_url": "#",
            },
        ]
        if subscription == "free":
            data["sections"].append({"id": "upgrade_banner", "criticality": "static"})
            data["upgrade_banner"] = {
                "heading": "Unlock your full potential",
                "subheading": "Join 4.8M aspirants on Premium",
                "price_monthly": 299,
                "price_annual": 2499,
                "features": [
                    "Unlimited mock tests (30/month → Unlimited)",
                    "AI-powered weak topic analysis",
                    "Live doubt-clearing sessions",
                    "Previous year papers — 10 years",
                ],
            }

    # ── Group 7: TSP (Tech Service Provider) ─────────────────────────────────
    elif portal_group == 7:
        data["kpis"] = [
            {"label": "Client Institutions", "value": "38", "trend": "+4 this quarter"},
            {
                "label": "API Calls (Today)",
                "value": "2.4M",
                "trend": "Peak 14:00–16:00",
            },
            {"label": "Avg API Latency", "value": "42ms", "trend": "SLA: < 200ms ✓"},
        ]
        data["clients"] = [
            {
                "id": 1,
                "name": "Sunrise Degree College",
                "type": "college",
                "student_count": 1424,
                "status": "active",
            },
            {
                "id": 2,
                "name": "Toppers Coaching Centre",
                "type": "coaching",
                "student_count": 1840,
                "status": "active",
            },
            {
                "id": 3,
                "name": "Greenwood High School",
                "type": "school",
                "student_count": 948,
                "status": "active",
            },
            {
                "id": 4,
                "name": "Victory IAS Academy",
                "type": "coaching",
                "student_count": 620,
                "status": "onboarding",
            },
        ]
        data["api_health"] = [
            {"name": "Auth API", "latency_ms": 38},
            {"name": "Home API", "latency_ms": 55},
            {"name": "Tenant API", "latency_ms": 21},
            {"name": "Exam API", "latency_ms": 142},
        ]
        data["alerts"] = [
            {"message": "Victory IAS onboarding: DNS verification pending"},
        ]

    # ── Group 9: B2B Partner ──────────────────────────────────────────────────
    elif portal_group == 9:
        data["kpis"] = [
            {"label": "Content Views", "value": "1.84L", "trend": "+12% vs last month"},
            {"label": "Revenue (MTD)", "value": "₹48,200", "trend": "↑ 18% vs target"},
            {"label": "Active Titles", "value": "214", "trend": "12 pending review"},
        ]
        data["content_items"] = [
            {
                "title": "SSC CGL Quant Masterclass",
                "type": "Video",
                "views": 24800,
                "revenue": "₹12,400",
            },
            {
                "title": "Banking Awareness Notes 2024",
                "type": "PDF",
                "views": 18600,
                "revenue": "₹9,300",
            },
            {
                "title": "RRB NTPC Previous Papers Pack",
                "type": "Test Set",
                "views": 15200,
                "revenue": "₹7,600",
            },
            {
                "title": "English Grammar for SSC — Vol 2",
                "type": "eBook",
                "views": 9400,
                "revenue": "₹4,700",
            },
        ]
        data["revenue"] = {
            "this_month": "₹48,200",
            "last_month": "₹40,800",
            "pending_payout": "₹22,600",
        }
        data["alerts"] = [
            {
                "message": "2 content titles flagged for quality review — action required"
            },
        ]

    # ── Group 10: Student Unified ─────────────────────────────────────────────
    elif portal_group == 10:
        data["kpis"] = [
            {"label": "My Institutions", "value": "3", "trend": "All active"},
            {"label": "Upcoming Exams", "value": "2", "trend": "Next: Apr 8"},
            {"label": "Pending Tasks", "value": "5", "trend": "2 due today"},
        ]
        data["institutions"] = [
            {
                "name": "Greenwood High School",
                "type": "School",
                "role": "Student",
                "portal_url": "http://localhost:8000",
                "primary_color": "#1B5E20",
            },
            {
                "name": "Toppers Coaching Centre",
                "type": "Coaching",
                "role": "Student",
                "portal_url": "http://localhost:8000",
                "primary_color": "#4A148C",
            },
            {
                "name": "EduForge SSC",
                "type": "Exam",
                "role": "Aspirant",
                "portal_url": "http://localhost:8000",
                "primary_color": "#1565C0",
            },
        ]
        data["today_schedule"] = [
            {
                "title": "Mathematics Class",
                "time": "09:00",
                "type": "class",
                "institution": "Greenwood High School",
            },
            {
                "title": "SSC CGL Mock Test #24",
                "time": "11:00",
                "type": "exam",
                "institution": "EduForge SSC",
            },
            {
                "title": "Quantitative Aptitude",
                "time": "16:00",
                "type": "class",
                "institution": "Toppers Coaching Centre",
            },
        ]
        data["deadlines"] = [
            {
                "title": "Annual Exam Registration",
                "institution": "Greenwood High",
                "days_left": 2,
            },
            {
                "title": "Fee Payment — Semester 2",
                "institution": "Greenwood High",
                "days_left": 5,
            },
            {
                "title": "RRB NTPC Application",
                "institution": "EduForge SSC",
                "days_left": 12,
            },
        ]
        data["alerts"] = [
            {
                "message": "Annual exam registration closes in 2 days — Greenwood High School"
            },
        ]

    return {"portal_group": portal_group, "data": data}


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
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (int(data["sub"]),)
    ).fetchone()
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
