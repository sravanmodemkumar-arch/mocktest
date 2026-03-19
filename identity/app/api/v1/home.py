"""Home endpoints — returns role-specific dashboard data."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, Institution
from app.services.jwt import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/home", tags=["home"])
security = HTTPBearer()

# Group → role → home_type mapping
HOME_TYPE_MAP = {
    1: "platform_admin",       # Group 1: EduForge admin
    2: "chain_admin",          # Group 2: Institution chain
    3: "school_portal",        # Group 3: School
    4: "college_portal",       # Group 4: College
    5: "coaching_portal",      # Group 5: Coaching
    6: "exam_domain",          # Group 6: Exam domain
    7: "tsp_operator",         # Group 7: Test series platform
    8: "parent_unified",       # Group 8: Parent
    9: "b2b_partner",          # Group 9: B2B partner
    10: "student_unified",     # Group 10: Student unified
}

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    data = decode_token(credentials.credentials)
    if not data or data.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return data


@router.get("")
async def get_home(
    request: Request,
    token_data: dict = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Returns home page data based on tenant group + user role."""
    tenant = getattr(request.state, "tenant", {})
    portal_group = tenant.get("portal_group", 1)
    user_id = int(token_data["sub"])
    role = token_data.get("role", "student")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")

    home_type = HOME_TYPE_MAP.get(portal_group, "student_unified")

    return {
        "home_type": home_type,
        "portal_group": portal_group,
        "user": {
            "id": user.id,
            "mobile": user.mobile,
            "role": user.role,
        },
        "tenant": {
            "slug": tenant.get("slug"),
            "branding": tenant.get("branding", {}),
            "features": tenant.get("features", {}),
        },
        "sections": _get_sections_for_role(home_type, role),
    }


def _get_sections_for_role(home_type: str, role: str) -> list[str]:
    """Returns which home sections to show for a given home type + role."""
    base = {
        "platform_admin": ["kpi_bar", "activity_feed", "tenant_health", "system_alerts", "revenue"],
        "chain_admin": ["kpi_bar", "branch_map", "branch_cards", "performance_trend", "alerts"],
        "school_portal": {
            "principal": ["kpi_bar", "alerts", "attendance_grid", "fee_summary", "staff_list", "exam_schedule"],
            "teacher": ["class_timetable", "attendance_entry", "marks_entry", "student_list"],
            "student": ["today_schedule", "attendance", "marks", "upcoming_tests", "fee_status"],
            "parent": ["child_cards", "attendance", "marks", "fee_centre", "messages"],
        },
        "college_portal": {
            "principal": ["kpi_bar", "stream_cards", "board_countdown", "faculty_grid", "fee_summary"],
            "faculty": ["timetable", "attendance_entry", "marks_entry", "student_performance"],
            "student": ["today_schedule", "attendance", "marks", "upcoming_exams", "fee_status"],
        },
        "coaching_portal": {
            "director": ["kpi_bar", "batch_grid", "air_leaderboard", "revenue", "faculty_performance"],
            "faculty": ["batch_timetable", "attendance_entry", "marks_entry", "student_ranks"],
            "student": ["today_schedule", "batch_info", "air_rank", "weak_topics", "study_plan"],
        },
        "exam_domain": {
            "free": ["kpi_bar", "upgrade_banner", "test_list_limited", "score_trend_basic", "leaderboard"],
            "premium": ["kpi_bar", "test_list_full", "performance_deep", "weak_topics", "ai_study_plan", "leaderboard"],
        },
        "tsp_operator": ["kpi_bar", "live_tests_monitor", "upcoming_calendar", "content_pipeline", "revenue"],
        "parent_unified": ["greeting", "alerts", "children_cards", "fee_centre", "messages", "upcoming_events"],
        "b2b_partner": ["kpi_bar", "api_health", "usage_analytics", "integration_status", "billing"],
        "student_unified": ["greeting", "alerts", "institution_cards", "exam_domain_cards", "performance", "weak_topics", "upcoming_tests", "ai_study_plan"],
    }

    sections = base.get(home_type, [])

    # If sections is a dict (role-based), pick the right one
    if isinstance(sections, dict):
        # Match role to closest key
        for key in sections:
            if key in role.lower():
                return sections[key]
        # Default to first available
        return list(sections.values())[0] if sections else []

    return sections


@router.get("/tenant-config")
async def get_tenant_config(request: Request):
    """Returns tenant branding + portal group — no auth required (needed before login)."""
    tenant = getattr(request.state, "tenant", {})
    return {
        "slug": tenant.get("slug", "unknown"),
        "portal_group": tenant.get("portal_group", 1),
        "branding": tenant.get("branding", {}),
        "features": tenant.get("features", {}),
    }
