"""Home Service — aggregates ALL home page data in one response.
CDN caches for web. Mobile caches locally with versioning + criticality flags.
Lambda runs once per unique (tenant+role) combo — CDN/mobile cache serves the rest.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from typing import Optional
import sys, os
import hashlib
import httpx

# Add shared to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.client import (
    detect_client, is_mobile, ClientType,
    compute_page_cache_ttl, make_cache_headers, SECTION_CRITICALITY,
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

app = FastAPI(
    title="EduForge Home Service",
    description="Aggregated home page data — CDN cached (web) / local cache (mobile)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Authorization", "X-Client-Type", "X-App-Version", "X-Tenant-Slug", "X-User-Role", "X-Portal-Group", "If-None-Match"],
)

# ── Section definitions per portal group + role ─────────────────────────────

HOME_SECTIONS = {
    1: {
        "default": {
            "greeting": {"title": "Platform Control Center", "subtitle": "EduForge operations dashboard"},
            "kpis": [
                {"id": "total_institutions", "label": "Total Institutions", "value": 0, "trend": "+0%"},
                {"id": "active_students",    "label": "Active Students",    "value": 0, "trend": "+0%"},
                {"id": "revenue_mtd",        "label": "Revenue MTD",        "value": "₹0", "trend": "+0%"},
                {"id": "api_calls_today",    "label": "API Calls Today",    "value": 0, "trend": "+0%"},
            ],
            "sections": ["kpi_bar", "system_health", "activity_feed", "tenant_list", "revenue_chart"],
        }
    },
    2: {
        "default": {
            "greeting": {"title": "Institution Chain Dashboard"},
            "kpis": [
                {"id": "total_branches",  "label": "Total Branches",  "value": 0},
                {"id": "total_students",  "label": "Total Students",  "value": 0},
                {"id": "avg_attendance",  "label": "Avg Attendance",  "value": "0%"},
                {"id": "revenue_mtd",     "label": "Revenue MTD",     "value": "₹0"},
            ],
            "sections": ["kpi_bar", "branch_map", "branch_cards", "performance_trend", "alerts"],
        }
    },
    3: {
        "principal": {
            "greeting": {"title": "Principal's Dashboard"},
            "kpis": [
                {"id": "total_students",   "label": "Total Students",       "value": 0},
                {"id": "attendance_today", "label": "Attendance Today",     "value": "0%"},
                {"id": "fees_collected",   "label": "Fees Collected MTD",   "value": "₹0"},
                {"id": "exams_this_week",  "label": "Exams This Week",      "value": 0},
            ],
            "sections": ["kpi_bar", "alerts", "attendance_grid", "fee_summary", "exam_schedule", "staff_grid"],
        },
        "teacher": {
            "greeting": {"title": "Teacher Dashboard"},
            "kpis": [
                {"id": "my_classes_today",   "label": "Classes Today",         "value": 0},
                {"id": "attendance_pending", "label": "Attendance Pending",    "value": 0},
                {"id": "assignments_due",    "label": "Assignments Due",       "value": 0},
            ],
            "sections": ["timetable", "attendance_entry", "marks_entry", "student_list", "alerts"],
        },
        "student": {
            "greeting": {"title": "Student Dashboard"},
            "kpis": [
                {"id": "attendance",      "label": "My Attendance",  "value": "0%"},
                {"id": "last_marks",      "label": "Last Test Score","value": "0/0"},
                {"id": "fee_status",      "label": "Fee Status",     "value": "Paid"},
                {"id": "upcoming_exams",  "label": "Upcoming Exams", "value": 0},
            ],
            "sections": ["today_schedule", "attendance", "marks", "upcoming_tests", "fee_status"],
        },
        "parent": {
            "greeting": {"title": "Parent Dashboard"},
            "sections": ["children_cards", "alerts", "attendance", "marks", "fee_centre", "messages"],
        },
    },
    4: {
        "principal": {
            "greeting": {"title": "Principal's Dashboard"},
            "kpis": [
                {"id": "total_students",  "label": "Total Students",     "value": 0},
                {"id": "attendance_today","label": "Attendance Today",   "value": "0%"},
                {"id": "board_countdown", "label": "Days to Board Exam", "value": 0},
                {"id": "fees_collected",  "label": "Fees Collected",     "value": "₹0"},
            ],
            "sections": ["kpi_bar", "stream_cards", "board_countdown", "alerts", "faculty_grid", "fee_summary"],
        },
        "faculty": {
            "greeting": {"title": "Faculty Dashboard"},
            "sections": ["timetable", "attendance_entry", "marks_entry", "student_performance"],
        },
        "student": {
            "greeting": {"title": "Student Dashboard"},
            "sections": ["today_schedule", "attendance", "marks", "upcoming_exams", "fee_status"],
        },
    },
    5: {
        "director": {
            "greeting": {"title": "Director's Dashboard"},
            "kpis": [
                {"id": "active_batches", "label": "Active Batches",       "value": 0},
                {"id": "total_students", "label": "Total Students",       "value": 0},
                {"id": "avg_air",        "label": "Avg AIR (Last Test)",  "value": 0},
                {"id": "revenue_mtd",    "label": "Revenue MTD",          "value": "₹0"},
            ],
            "sections": ["kpi_bar", "batch_grid", "air_leaderboard", "revenue", "faculty_performance", "alerts"],
        },
        "faculty": {
            "greeting": {"title": "Faculty Dashboard"},
            "sections": ["batch_timetable", "attendance_entry", "marks_entry", "student_ranks"],
        },
        "student": {
            "greeting": {"title": "Student Dashboard"},
            "sections": ["today_schedule", "batch_info", "air_rank", "weak_topics", "study_plan"],
        },
    },
    6: {
        "free": {
            "greeting": {"title": "Welcome Back"},
            "kpis": [
                {"id": "tests_used", "label": "Tests This Month", "value": "0/5"},
                {"id": "best_air",   "label": "Best AIR",         "value": 0},
                {"id": "streak",     "label": "Study Streak",     "value": "0 days"},
            ],
            "sections": ["kpi_bar", "upgrade_banner", "live_tests", "test_list_limited", "score_trend_basic", "leaderboard"],
            "upgrade_banner": {
                "heading": "Upgrade to Premium",
                "price_monthly": 299,
                "price_yearly": 1999,
                "features": ["Unlimited mock tests", "AI-powered study plan", "Detailed topic analysis", "Rank among 2L+ aspirants"],
            },
        },
        "premium": {
            "greeting": {"title": "Welcome Back"},
            "kpis": [
                {"id": "tests_taken",  "label": "Tests This Month",     "value": 0},
                {"id": "best_air",     "label": "Best AIR",             "value": 0},
                {"id": "streak",       "label": "Study Streak",         "value": "0 days"},
                {"id": "percentile",   "label": "Current Percentile",   "value": "0%"},
            ],
            "sections": ["kpi_bar", "live_tests", "test_list_full", "performance_deep", "weak_topics", "ai_study_plan", "leaderboard"],
        },
    },
    7: {
        "default": {
            "greeting": {"title": "Test Series Platform"},
            "kpis": [
                {"id": "total_subscribers", "label": "Total Subscribers",       "value": 0},
                {"id": "revenue_mtd",       "label": "Revenue MTD",             "value": "₹0"},
                {"id": "tests_published",   "label": "Tests Published",         "value": 0},
                {"id": "avg_score",         "label": "Avg Score (Last Test)",   "value": "0%"},
            ],
            "sections": ["kpi_bar", "live_tests_monitor", "upcoming_calendar", "content_pipeline", "student_acquisition", "revenue"],
        }
    },
    8: {
        "default": {
            "greeting": {"title": "Parent Dashboard"},
            "sections": ["greeting", "alerts", "children_cards", "fee_centre", "messages", "upcoming_events"],
        }
    },
    9: {
        "default": {
            "greeting": {"title": "Partner Dashboard"},
            "kpis": [
                {"id": "api_calls_today", "label": "API Calls Today", "value": 0},
                {"id": "success_rate",    "label": "Success Rate",    "value": "0%"},
                {"id": "students_synced", "label": "Students Synced", "value": 0},
                {"id": "monthly_usage",   "label": "Monthly Usage",   "value": "0%"},
            ],
            "sections": ["kpi_bar", "api_health", "usage_analytics", "integration_status", "billing"],
        }
    },
    10: {
        "default": {
            "greeting": {"title": "My Dashboard"},
            "sections": ["greeting", "alerts", "institution_cards", "exam_domain_cards", "performance", "weak_topics", "upcoming_tests", "ai_study_plan"],
        }
    },
}


async def verify_token(token: str) -> Optional[dict]:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{AUTH_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=3.0,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return None


def get_page_data(portal_group: int, role: str) -> dict:
    group = HOME_SECTIONS.get(portal_group, HOME_SECTIONS[10])
    for key in group:
        if key != "default" and key.lower() in role.lower():
            return group[key]
    return group.get("default") or list(group.values())[0]


def annotate_sections_with_criticality(page_data: dict) -> dict:
    """Add criticality level to each section name so mobile knows what to cache."""
    sections = page_data.get("sections", [])
    annotated = []
    for section in sections:
        level = SECTION_CRITICALITY.get(section, "medium")
        annotated.append({"id": section, "criticality": level})
    result = dict(page_data)
    result["sections"] = annotated
    return result


@app.get("/api/v1/page/home")
async def get_home_page(request: Request):
    """
    ONE call for the entire home page.

    Web:    CDN caches by (X-Tenant-Slug + X-User-Role). s-maxage = page TTL.
    Mobile: Response includes criticality flags per section.
            Mobile SDK caches locally, uses ETag + If-None-Match.
            Critical sections → mobile always refetches those sections separately.

    Cache-Control is set based on minimum criticality of all sections on the page.
    If ANY section is critical (live test, fee due today) → no-cache for whole response.
    """
    client = detect_client(request)
    app_version = request.headers.get("X-App-Version", "1.0")
    portal_group = int(request.headers.get("X-Portal-Group", "1"))
    tenant_slug = request.headers.get("X-Tenant-Slug", "unknown")

    # Auth
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header required")

    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    role = user.get("role", "student")
    page_data = get_page_data(portal_group, role)

    # Annotate sections with criticality (mobile needs this to decide local cache TTL)
    annotated_data = annotate_sections_with_criticality(page_data)

    # Compute page-level cache TTL from section criticality (7-level system)
    section_ids = [s["id"] if isinstance(s, dict) else s for s in annotated_data.get("sections", [])]
    ttl, criticality = compute_page_cache_ttl(section_ids)

    # Generate ETag for mobile cache validation
    etag_source = f"{portal_group}:{role}:{tenant_slug}:{app_version}"
    etag = f'"{hashlib.md5(etag_source.encode()).hexdigest()[:16]}"'

    # 304 Not Modified for mobile if ETag matches (skip for critical/realtime)
    from shared.client import Criticality
    if_none_match = request.headers.get("If-None-Match", "")
    cacheable = criticality not in (Criticality.CRITICAL, Criticality.REALTIME)
    if if_none_match and if_none_match == etag and cacheable:
        from fastapi.responses import Response
        r = Response(status_code=304)
        r.headers["ETag"] = etag
        r.headers["Cache-Control"] = f"private, max-age={ttl}"
        r.headers["X-Criticality"] = criticality
        return r

    # Group sections by criticality bucket for mobile SDK
    section_by_level: dict[str, list[str]] = {
        "critical": [], "realtime": [], "high": [], "medium": [],
        "low": [], "offpeak": [], "static": [],
    }
    for sid in section_ids:
        lvl = SECTION_CRITICALITY.get(sid, "medium")
        section_by_level.setdefault(lvl, []).append(sid)

    response_body = {
        "page": "home",
        "portal_group": portal_group,
        "tenant_slug": tenant_slug,
        "user": {"id": user["id"], "role": role},
        "data": annotated_data,
        "cache_meta": {
            "page_criticality": criticality,   # worst (most urgent) level on this page
            "ttl": ttl,
            "etag": etag,
            "app_version": app_version,
            # Per-level section groups — mobile SDK uses these to schedule refreshes
            "sections_by_level": section_by_level,
            # Convenience shortcuts for mobile SDK
            "always_live":     section_by_level["critical"] + section_by_level["realtime"],
            "background_sync": section_by_level["high"] + section_by_level["medium"],
            "idle_sync":       section_by_level["low"],
            "offpeak_sync":    section_by_level["offpeak"],   # refresh 00:00–06:00 IST
            "app_bust_only":   section_by_level["static"],
        },
        "client_type": client.value,
    }

    cache_headers = make_cache_headers(ttl, criticality, client, app_version)
    response = JSONResponse(content=response_body)
    for k, v in cache_headers.items():
        response.headers[k] = v
    response.headers["ETag"] = etag

    return response


@app.get("/health")
async def health():
    return {"status": "ok", "service": "home"}


handler = Mangum(app, lifespan="off")
