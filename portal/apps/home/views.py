"""Home views — shell page + HTMX data loader."""
import httpx
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse


# Map portal group → template partial.
# Parents (role=parent) and students (role=student) access via institution portals (groups 3/4/5).
# Group 10 is only for student.eduforge.in — multi-institution aggregation.
# Group 8 does NOT have a standalone home; parents login through their child's institution portal.
GROUP_TEMPLATES = {
    1:  "home/partials/group1_platform_admin.html",
    2:  "home/partials/group2_chain_admin.html",
    3:  "home/partials/group3_school.html",
    4:  "home/partials/group4_college.html",
    5:  "home/partials/group5_coaching.html",
    6:  "home/partials/group6_exam_domain.html",
    7:  "home/partials/group7_tsp.html",
    9:  "home/partials/group9_b2b_partner.html",
    10: "home/partials/group10_student.html",
}


def home_shell(request):
    """Render the home page shell. HTMX loads data separately."""
    return render(request, "home/home.html")


def home_data(request):
    """HTMX: fetch home data from home service and render correct group partial."""
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
    tenant = getattr(request, "tenant", {})
    portal_group = tenant.get("portal_group", 1)
    user = getattr(request, "user_data", {}) or {}

    # Fetch aggregated home data from home service (one call)
    home_data = {}
    try:
        resp = httpx.get(
            f"{settings.HOME_SERVICE_URL}/api/v1/page/home",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Portal-Group": str(portal_group),
                "X-Tenant-Slug": tenant.get("slug", "default"),
                "X-User-Role": user.get("role", "student"),
                "X-Client-Type": "web",
            },
            timeout=5.0,
        )
        if resp.status_code == 200:
            home_data = resp.json()
    except Exception:
        pass

    # Determine template — group 8 (parent) has no standalone home; fallback to group 3 (school)
    template = GROUP_TEMPLATES.get(portal_group, GROUP_TEMPLATES[3])

    # Build time-of-day greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting_time = "morning"
    elif hour < 17:
        greeting_time = "afternoon"
    else:
        greeting_time = "evening"

    ctx = {
        "home": home_data,
        "greeting_time": greeting_time,
        "today_date": datetime.now().strftime("%A, %d %B %Y"),
        "kpis": home_data.get("data", {}).get("kpis", []),
        "alerts": home_data.get("data", {}).get("alerts", []),
        "sections": home_data.get("data", {}).get("sections", []),
        "is_premium": user.get("subscription") == "premium",
        "institution_name": tenant.get("name", ""),
        "domain_name": tenant.get("name", "EduForge"),
        **home_data.get("data", {}),
    }

    return render(request, template, ctx)


def nav_links(request):
    """HTMX: return sidebar nav links based on role + portal group."""
    tenant = getattr(request, "tenant", {})
    portal_group = tenant.get("portal_group", 1)
    user = getattr(request, "user_data", {}) or {}
    role = user.get("role", "student")

    nav_items = _get_nav_items(portal_group, role)
    return render(request, "partials/nav_links.html", {"nav_items": nav_items})


def _get_nav_items(portal_group: int, role: str) -> list:
    """Return nav items for a given portal group + role."""
    base = [{"label": "Home", "url": "/home/", "icon": "🏠"}]

    if portal_group == 1:  # Platform Admin
        return base + [
            {"label": "Institutions", "url": "/institutions/", "icon": "🏛️"},
            {"label": "Chain Admins", "url": "/chain-admins/", "icon": "🔗"},
            {"label": "Billing", "url": "/billing/", "icon": "💳"},
            {"label": "Audit Logs", "url": "/audit-logs/", "icon": "📋"},
            {"label": "Settings", "url": "/settings/", "icon": "⚙️"},
        ]

    if portal_group == 2:  # Chain Admin
        return base + [
            {"label": "Branches", "url": "/branches/", "icon": "🏫"},
            {"label": "Fee Collection", "url": "/fee-collection/", "icon": "💰"},
            {"label": "Staff Transfer", "url": "/staff-transfer/", "icon": "🔄"},
            {"label": "Exam Schedule", "url": "/exam-schedule/", "icon": "📝"},
            {"label": "Reports", "url": "/reports/", "icon": "📊"},
            {"label": "Settings", "url": "/settings/", "icon": "⚙️"},
        ]

    if portal_group in (3, 4, 5):  # School / College / Coaching — role matters
        if role in ("principal", "director", "admin", "vice_principal"):
            return base + [
                {"label": "Students", "url": "/students/", "icon": "👨‍🎓"},
                {"label": "Staff", "url": "/staff/", "icon": "👩‍🏫"},
                {"label": "Attendance", "url": "/attendance/", "icon": "📅"},
                {"label": "Exams", "url": "/exams/", "icon": "📝"},
                {"label": "Fees", "url": "/fees/", "icon": "💰"},
                {"label": "Reports", "url": "/reports/", "icon": "📊"},
                {"label": "Settings", "url": "/settings/", "icon": "⚙️"},
            ]
        if role in ("teacher", "faculty", "hod"):
            return base + [
                {"label": "My Classes", "url": "/classes/", "icon": "🏫"},
                {"label": "Attendance", "url": "/attendance/", "icon": "📅"},
                {"label": "Marks", "url": "/marks/", "icon": "📝"},
                {"label": "Students", "url": "/students/", "icon": "👨‍🎓"},
            ]
        if role == "parent":
            # Parents access via institution portal — no standalone portal
            return base + [
                {"label": "My Ward", "url": "/ward/", "icon": "👧"},
                {"label": "Attendance", "url": "/attendance/ward/", "icon": "📅"},
                {"label": "Results", "url": "/results/ward/", "icon": "📊"},
                {"label": "Fees", "url": "/fees/pay/", "icon": "💰"},
                {"label": "Messages", "url": "/messages/", "icon": "💬"},
            ]
        # student role within institution portal
        return base + [
            {"label": "My Schedule", "url": "/schedule/", "icon": "📅"},
            {"label": "Results", "url": "/results/", "icon": "📊"},
            {"label": "Attendance", "url": "/attendance/", "icon": "📅"},
            {"label": "Fee", "url": "/fees/", "icon": "💰"},
        ]

    if portal_group == 6:  # Exam Domain
        return base + [
            {"label": "Test Series", "url": "/tests/", "icon": "📝"},
            {"label": "My Performance", "url": "/performance/", "icon": "📊"},
            {"label": "Rankings", "url": "/rankings/", "icon": "🏆"},
            {"label": "Study Material", "url": "/material/", "icon": "📚"},
            {"label": "AI Study Plan", "url": "/ai-plan/", "icon": "🤖"},
            {"label": "Subscription", "url": "/subscription/", "icon": "💳"},
        ]

    if portal_group == 7:  # TSP
        return base + [
            {"label": "Clients", "url": "/clients/", "icon": "🏛️"},
            {"label": "Branding", "url": "/white-label/configure/", "icon": "🎨"},
            {"label": "API Keys", "url": "/api/keys/", "icon": "🔑"},
            {"label": "Billing", "url": "/billing/tsp/", "icon": "💳"},
            {"label": "Analytics", "url": "/analytics/", "icon": "📊"},
        ]

    if portal_group == 9:  # B2B Partner
        return base + [
            {"label": "Content", "url": "/content/", "icon": "📚"},
            {"label": "Analytics", "url": "/analytics/", "icon": "📊"},
            {"label": "Payouts", "url": "/payouts/", "icon": "💰"},
            {"label": "Settings", "url": "/settings/", "icon": "⚙️"},
        ]

    if portal_group == 10:  # Student Unified
        return base + [
            {"label": "My Institutions", "url": "/institutions/", "icon": "🏛️"},
            {"label": "Schedule", "url": "/schedule/", "icon": "📅"},
            {"label": "Results", "url": "/results/", "icon": "📊"},
            {"label": "Deadlines", "url": "/deadlines/", "icon": "⏰"},
        ]

    # Default fallback
    return base + [
        {"label": "Reports", "url": "/reports/", "icon": "📊"},
        {"label": "Settings", "url": "/settings/", "icon": "⚙️"},
    ]
