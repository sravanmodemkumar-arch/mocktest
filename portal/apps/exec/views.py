"""Executive Dashboard views — HTMX-driven panels with mock data.

Each view corresponds to one dashboard panel partial. The shell view
renders the page frame; HTMX fetches each panel independently so they
load and refresh in parallel without blocking each other.

Mock data is structured identically to the real API response shape so
swapping in live API calls later requires only replacing _mock_* helpers.
"""

import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse


# ─────────────────────────────────────────────────────────────────────────────
# Access guard
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_ROLES = {"ceo", "cto", "coo", "cfo", "platform_owner"}


def _require_exec(request):
    """Return redirect if user is not an executive role, else None."""
    user = getattr(request, "user_data", {}) or {}
    role = user.get("role", "").lower()
    if role not in ALLOWED_ROLES:
        return redirect("/home/")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Mock data helpers
# ─────────────────────────────────────────────────────────────────────────────

def _mock_kpi(role: str) -> dict:
    return {
        "platform_health": {
            "value": 98.7,
            "trend": -0.3,
            "trend_dir": "down",
            "status": "warning",     # healthy | warning | critical
            "target": 99.5,
            "sub": "Target: 99.5% · 0.8% below SLA",
        },
        "active_exams": {
            "value": 3,
            "concurrent": 74000,
            "concurrent_status": "critical",   # ok | warning | critical
            "trend": 0,
            "trend_dir": "flat",
            "sub": "74,000 concurrent users",
        },
        "enrollments": {
            "value": 2413847,
            "value_fmt": "2,413,847",
            "trend": 12.4,
            "trend_dir": "up",
            "sub": "+1,42,301 from last month",
        },
        "revenue": {
            "value_fmt": "₹4.82 Cr",
            "trend": 8.2,
            "trend_dir": "up",
            "target_fmt": "₹5.2 Cr",
            "pct_achieved": 92.7,
            "sub": "Target: ₹5.2 Cr · 92.7% achieved",
            "status": "ok",
        },
        "role": role,
        "now_ist": datetime.now().strftime("%A, %d %B %Y"),
    }


def _mock_platform_health(range_: str = "24h") -> dict:
    """Generate time-series data for the platform health chart."""
    now = datetime.now()
    points = {"1h": 12, "6h": 36, "24h": 24, "7d": 28}.get(range_, 24)
    step_mins = {"1h": 5, "6h": 10, "24h": 60, "7d": 360}.get(range_, 60)

    labels, uptime, latency, error_rate = [], [], [], []
    for i in range(points):
        t = now - timedelta(minutes=step_mins * (points - i))
        labels.append(t.strftime("%H:%M") if range_ in ("1h", "6h", "24h") else t.strftime("%d %b"))
        # Slight dip at i=18 to simulate a past degradation
        dip = (i == 18)
        uptime.append(round(96.8 if dip else 98.7 + (i % 3) * 0.1, 2))
        latency.append(210 if dip else 42 + (i % 5) * 3)
        error_rate.append(0.08 if dip else 0.01 + (i % 4) * 0.002)

    services = [
        {"name": "API Gateway",      "uptime": 99.9,  "metric": "99.9% uptime",  "status": "healthy"},
        {"name": "Database Cluster", "uptime": 99.94, "metric": "0ms lag",        "status": "healthy"},
        {"name": "Exam Engine",      "uptime": 99.7,  "metric": "142ms p99",     "status": "healthy"},
        {"name": "CDN / Media",      "uptime": 99.8,  "metric": "91% cache hit", "status": "healthy"},
        {"name": "Notif Queue",      "uptime": 100.0, "metric": "depth: 42",     "status": "healthy"},
        {"name": "AI / ML Service",  "uptime": 99.2,  "metric": "680ms infer",   "status": "warning"},
    ]
    return {
        "range": range_,
        "labels_json": json.dumps(labels),
        "uptime_json": json.dumps(uptime),
        "latency_json": json.dumps(latency),
        "error_rate_json": json.dumps(error_rate),
        "services": services,
    }


def _mock_business_overview() -> dict:
    months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    inst_new = [38, 42, 35, 51, 44, 48]
    student_growth = [98000, 115000, 89000, 142000, 128000, 142301]
    return {
        "months_json": json.dumps(months),
        "inst_new_json": json.dumps(inst_new),
        "student_growth_json": json.dumps(student_growth),
        "total_institutions": 1900,
        "total_students_fmt": "2,413,847",
        "inst_change": "+48 this month",
        "inst_pct": "+2.6%",
        "student_change": "+1,42,301 this month",
        "student_pct": "+12.4%",
        "geo_data_json": json.dumps({
            "Andhra Pradesh": 280, "Telangana": 310, "Maharashtra": 195,
            "Karnataka": 210, "Tamil Nadu": 175, "UP": 140, "Delhi": 98,
            "Rajasthan": 87, "Gujarat": 76, "West Bengal": 65,
        }),
    }


def _mock_exam_ops(search: str = "", status_filter: str = "", type_filter: str = "") -> dict:
    all_exams = [
        {
            "id": "e1", "name": "JEE Main Mock 8",
            "institution": "Delhi Public Schools Group",
            "students": 42318, "live_users": 38204,
            "live_pct": 90, "status": "RUNNING", "type": "MCQ",
            "status_color": "text-emerald-400", "dot_color": "bg-emerald-400",
        },
        {
            "id": "e2", "name": "NEET Mock 4",
            "institution": "Sri Chaitanya Organisation",
            "students": 18500, "live_users": 17912,
            "live_pct": 97, "status": "RUNNING", "type": "MCQ",
            "status_color": "text-emerald-400", "dot_color": "bg-red-400",
        },
        {
            "id": "e3", "name": "Class 10 Finals",
            "institution": "Ryan International Schools",
            "students": 13200, "live_users": 13100,
            "live_pct": 99, "status": "RUNNING", "type": "Mixed",
            "status_color": "text-emerald-400", "dot_color": "bg-red-400",
        },
    ]

    exams = all_exams
    if search:
        q = search.lower()
        exams = [e for e in exams if q in e["name"].lower() or q in e["institution"].lower()]
    if status_filter and status_filter != "all":
        exams = [e for e in exams if e["status"].lower().replace(" ", "_") == status_filter]
    if type_filter and type_filter != "all":
        exams = [e for e in exams if e["type"].lower() == type_filter.lower()]

    summary = {
        "active_exams": len(all_exams),
        "concurrent": 74000,
        "concurrent_status": "critical",
        "submissions_min": 12400,
        "avg_latency_ms": 142,
        "pending_results": 2,
    }
    return {"exams": exams, "summary": summary, "search": search,
            "status_filter": status_filter, "type_filter": type_filter}


def _mock_revenue(tab: str = "mtd") -> dict:
    days = list(range(1, 21))
    mtd_this = [round(0.24 * d + (d % 3) * 0.05, 2) for d in days]
    mtd_last = [round(0.22 * d + (d % 3) * 0.04, 2) for d in days]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ytd_this = [3.8, 4.1, 4.82, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ytd_last = [3.4, 3.7, 4.45, 4.5, 4.6, 4.7, 4.8, 4.9, 5.1, 5.2, 5.0, 5.3]

    donut = [
        {"label": "Annual plans",   "value": 71, "amount": "₹3.42 Cr", "color": "#6366F1"},
        {"label": "Monthly plans",  "value": 19, "amount": "₹0.94 Cr", "color": "#10B981"},
        {"label": "Trial accounts", "value": 6,  "amount": "₹0.31 Cr", "color": "#F59E0B"},
        {"label": "Overdue",        "value": 4,  "amount": "₹0.15 Cr", "color": "#EF4444"},
    ]
    return {
        "tab": tab,
        "days_json": json.dumps(days),
        "mtd_this_json": json.dumps(mtd_this),
        "mtd_last_json": json.dumps(mtd_last),
        "months_json": json.dumps(months),
        "ytd_this_json": json.dumps(ytd_this),
        "ytd_last_json": json.dumps(ytd_last),
        "donut_json": json.dumps(donut),
        "donut_labels_json": json.dumps([d["label"] for d in donut]),
        "donut_values_json": json.dumps([d["value"] for d in donut]),
        "donut_colors_json": json.dumps([d["color"] for d in donut]),
        "mtd_total": "₹4.82 Cr",
        "mtd_target": "₹5.2 Cr",
        "mtd_pct": 92.7,
        "projected_eom": "₹5.31 Cr",
        "days_left": 11,
        "donut": donut,
    }


def _mock_activity(category: str = "all", search: str = "", before_id: int = 0) -> dict:
    events = [
        {
            "id": 10, "ts": "14:32:05", "category": "config",
            "badge": "CONFIG", "badge_color": "text-indigo-400 bg-indigo-400/10",
            "actor": "Arjun Mehta", "actor_role": "CEO",
            "summary": "Updated exam slot capacity — JEE Main 2026",
            "detail": [("Previous", "70,000 seats"), ("New", "74,000 seats"), ("Reason", '"Peak season demand"')],
            "link": "/exec/exams/jee-main-2026/", "link_text": "View Exam →",
        },
        {
            "id": 9, "ts": "14:28:41", "category": "infra",
            "badge": "INFRA", "badge_color": "text-amber-400 bg-amber-400/10",
            "actor": "System", "actor_role": "Auto-Scaler",
            "summary": "Scaled exam cluster: 8 → 12 nodes",
            "detail": [("Trigger", "CPU > 80% for 3 consecutive minutes"), ("Region", "ap-south-1")],
            "link": None, "link_text": None,
        },
        {
            "id": 8, "ts": "14:15:00", "category": "incident",
            "badge": "INCIDENT", "badge_color": "text-red-400 bg-red-400/10",
            "actor": "Priya Sharma", "actor_role": "Platform Ops",
            "summary": "Opened P1 Incident: Elevated API latency — South region",
            "detail": [("Incident ID", "INC-2026-0312"), ("Duration", "17 min and counting")],
            "link": "/exec/incidents/INC-2026-0312/", "link_text": "View Incident →",
        },
        {
            "id": 7, "ts": "13:50:22", "category": "billing",
            "badge": "BILLING", "badge_color": "text-emerald-400 bg-emerald-400/10",
            "actor": "Billing System", "actor_role": "Auto",
            "summary": "₹12.4L invoice paid — Delhi Public Schools Group",
            "detail": [("Invoice", "INV-2026-0847"), ("Plan", "Annual · 14 schools")],
            "link": "/exec/billing/INV-2026-0847/", "link_text": "View Invoice →",
        },
        {
            "id": 6, "ts": "13:42:18", "category": "exam",
            "badge": "EXAM", "badge_color": "text-cyan-400 bg-cyan-400/10",
            "actor": "Exam Engine", "actor_role": "System",
            "summary": "NEET Mock 4 completed — Sri Chaitanya Organisation",
            "detail": [("Students", "18,412 submitted"), ("Avg Score", "312 / 720")],
            "link": "/exec/exams/neet-mock-4/results/", "link_text": "View Results →",
        },
        {
            "id": 5, "ts": "12:58:00", "category": "compliance",
            "badge": "COMPLIANCE", "badge_color": "text-yellow-400 bg-yellow-400/10",
            "actor": "Rohan Verma", "actor_role": "Legal",
            "summary": "DPDP audit log exported",
            "detail": [("Records", "4,218 rows"), ("Period", "Jan–Mar 2026")],
            "link": "/exec/compliance/audit-exports/", "link_text": "View Export →",
        },
    ]

    if category and category != "all":
        events = [e for e in events if e["category"] == category]
    if search:
        q = search.lower()
        events = [e for e in events if q in e["summary"].lower() or q in e["actor"].lower()]
    if before_id:
        events = [e for e in events if e["id"] < before_id]

    return {
        "events": events,
        "category": category,
        "search": search,
        "has_more": len(events) >= 6,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helper: detect HTMX request
# ─────────────────────────────────────────────────────────────────────────────

def _is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def _paginate(items, page, per_page=10):
    """Slice a list and return pagination context."""
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    half = 2
    p_start = max(1, page - half)
    p_end   = min(total_pages, page + half)
    return {
        "items": items[start: start + per_page],
        "page": page,
        "total_pages": total_pages,
        "total_count": total,
        "page_start": start + 1 if items else 0,
        "page_end": min(start + per_page, total),
        "page_range": list(range(p_start, p_end + 1)),
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Views  — ONE URL per page
#
# Pattern:
#   GET /exec/<page>/              → full shell HTML
#   GET /exec/<page>/?part=<name>  → HTMX partial HTML  (HX-Request header)
#
# Each view function handles both cases.
# ─────────────────────────────────────────────────────────────────────────────

def dashboard(request):
    """div-a-01: Executive Dashboard.
    ?part=kpi          → KPI bar
    ?part=health       → Platform health mini-panel
    ?part=business     → Business overview chart
    ?part=exams        → Exam ops mini-table
    ?part=revenue      → Revenue & billing chart
    ?part=activity     → Activity feed
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    role = user.get("role", "ceo").lower()

    if _is_htmx(request):
        part = request.GET.get("part", "")
        if part == "kpi":
            return render(request, "exec/partials/kpi_bar.html", _mock_kpi(role))
        if part == "health":
            range_ = request.GET.get("range", "24h")
            data = _mock_platform_health(range_)
            data["tabs"] = [("growth", "Growth"), ("geo", "Geo"), ("type", "Type")]
            return render(request, "exec/partials/platform_health.html", data)
        if part == "business":
            tab = request.GET.get("tab", "growth")
            data = _mock_business_overview()
            data["active_tab"] = tab
            data["tabs"] = [("growth", "Growth"), ("geo", "Geo"), ("type", "Type")]
            return render(request, "exec/partials/business_overview.html", data)
        if part == "exams":
            search   = request.GET.get("q", "")
            status_f = request.GET.get("status", "")
            type_f   = request.GET.get("type", "")
            data = _mock_exam_ops(search, status_f, type_f)
            data.update({
                "total_active": 3, "total_students": 74018, "peak_concurrent": 91,
                "status_options": [("", "All"), ("running", "Running"), ("paused", "Paused"),
                                   ("scheduled", "Scheduled")],
                "active_filter": status_f,
            })
            return render(request, "exec/partials/exam_ops.html", data)
        if part == "revenue":
            tab = request.GET.get("tab", "mtd")
            data = _mock_revenue(tab)
            data.update({
                "active_tab": tab,
                "rev_tabs": [("mtd", "MTD"), ("ytd", "YTD"), ("forecast", "Forecast")],
                "rev_labels_json": data.get("days_json", "[]"),
                "rev_data_json":   data.get("mtd_this_json", "[]"),
                "revenue_mtd_fmt": data["mtd_total"], "revenue_ytd_fmt": "₹12.54 Cr",
                "arr_fmt": "₹58.40 Cr", "mrr_fmt": "₹4.87 Cr",
                "rev_change": "8.2", "arr_change": "14.3",
                "donut_segments": data["donut"],
            })
            return render(request, "exec/partials/revenue_billing.html", data)
        if part == "activity":
            category = request.GET.get("cat", "all")
            search   = request.GET.get("q", "")
            page     = int(request.GET.get("page", 1))
            paged    = _paginate(_mock_activity(category, search, 0)["events"], page, 6)
            cat_tabs = [
                ("all", "All", "#64748B"), ("config", "Config", "#6366F1"),
                ("incident", "Incident", "#EF4444"), ("infra", "Infra", "#F59E0B"),
                ("billing", "Billing", "#10B981"), ("exam", "Exam", "#06B6D4"),
                ("compliance", "Compliance", "#F59E0B"),
            ]
            return render(request, "exec/partials/activity_feed.html", {
                "events": paged["items"], "category": category, "search": search,
                "page": paged["page"], "has_next": paged["has_next"],
                "has_prev": paged["has_prev"], "total_count": paged["total_count"],
                "category_tabs": cat_tabs,
            })
        return HttpResponse(status=400)

    return render(request, "exec/dashboard.html", {
        "user": user, "role": role, "page_title": "Executive Dashboard",
    })


def platform_health(request):
    """div-a-02: Platform Health.
    ?part=chart        → chart panel (range, metric params)
    ?part=incidents    → recent incidents table
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}

    if _is_htmx(request):
        part   = request.GET.get("part", "chart")
        range_ = request.GET.get("range", "24h")
        if part == "chart":
            data = _mock_platform_health(range_)
            data["active_metric"] = request.GET.get("metric", "all")
            return render(request, "exec/partials/ph_chart.html", data)
        if part == "incidents":
            incidents = [
                {"id": "INC-2026-0312", "title": "Elevated API latency — South region",
                 "severity": "P1", "status": "open",     "duration": "17m", "ts": "14:15"},
                {"id": "INC-2026-0308", "title": "CDN cache miss spike",
                 "severity": "P2", "status": "resolved", "duration": "42m", "ts": "09:03"},
                {"id": "INC-2026-0301", "title": "DB replica lag > 30s",
                 "severity": "P1", "status": "resolved", "duration": "8m",  "ts": "Mar 18"},
                {"id": "INC-2026-0298", "title": "Notification queue backlog",
                 "severity": "P2", "status": "resolved", "duration": "23m", "ts": "Mar 17"},
                {"id": "INC-2026-0291", "title": "Exam Engine cold start delay",
                 "severity": "P3", "status": "resolved", "duration": "5m",  "ts": "Mar 15"},
            ]
            return render(request, "exec/partials/ph_incidents.html", {"incidents": incidents})
        return HttpResponse(status=400)

    return render(request, "exec/platform_health_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Platform Health", "active_nav": "/exec/platform-health/",
    })


def exam_ops(request):
    """div-a-03: Exam Operations.
    ?part=stats        → live stats strip
    ?part=table        → exam table (q, status, type, page params)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}

    if _is_htmx(request):
        part = request.GET.get("part", "table")
        if part == "stats":
            return render(request, "exec/partials/eo_stats.html", {
                "total_active": 3, "total_students": 74018,
                "peak_concurrent": 91, "submissions_min": 12400,
                "avg_latency_ms": 142, "pending_results": 2,
            })
        if part == "table":
            search   = request.GET.get("q", "")
            status_f = request.GET.get("status", "")
            type_f   = request.GET.get("type", "")
            page     = int(request.GET.get("page", 1))
            data     = _mock_exam_ops(search, status_f, type_f)
            paged    = _paginate(data["exams"], page, 10)
            data.update({
                "exams": paged["items"], "page": paged["page"],
                "total_pages": paged["total_pages"], "total_count": paged["total_count"],
                "has_prev": paged["has_prev"], "has_next": paged["has_next"],
                "page_start": paged["page_start"], "page_end": paged["page_end"],
                "active_filter": status_f,
            })
            return render(request, "exec/partials/eo_table.html", data)
        return HttpResponse(status=400)

    return render(request, "exec/exam_ops_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Exam Operations", "active_nav": "/exec/exam-ops/",
    })


def financial_overview(request):
    """div-a-08: Financial Overview.
    ?part=chart        → revenue chart (tab param)
    ?part=invoices     → invoice table (q, status, page params)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}

    if _is_htmx(request):
        part = request.GET.get("part", "chart")
        if part == "chart":
            tab  = request.GET.get("tab", "mtd")
            data = _mock_revenue(tab)
            data.update({
                "tab": tab,
                "rev_labels_json": data.get("days_json", "[]"),
                "rev_data_json":   data.get("mtd_this_json", "[]"),
            })
            return render(request, "exec/partials/fin_chart.html", data)
        if part == "invoices":
            search   = request.GET.get("q", "")
            status_f = request.GET.get("status", "")
            page     = int(request.GET.get("page", 1))
            all_invoices = [
                {"id": "INV-2026-0847", "institution": "Delhi Public Schools Group",
                 "amount": "₹12,40,000", "plan": "Annual · 14 schools",
                 "status": "paid",    "due": "Mar 01"},
                {"id": "INV-2026-0841", "institution": "Sri Chaitanya Organisation",
                 "amount": "₹8,20,000", "plan": "Annual · 9 schools",
                 "status": "paid",    "due": "Mar 01"},
                {"id": "INV-2026-0835", "institution": "Ryan International Schools",
                 "amount": "₹6,50,000", "plan": "Annual · 7 schools",
                 "status": "overdue", "due": "Feb 15"},
                {"id": "INV-2026-0829", "institution": "Narayana Group",
                 "amount": "₹9,80,000", "plan": "Annual · 11 schools",
                 "status": "paid",    "due": "Feb 01"},
                {"id": "INV-2026-0822", "institution": "Aakash Institute",
                 "amount": "₹4,10,000", "plan": "Monthly · 5 branches",
                 "status": "pending", "due": "Mar 25"},
                {"id": "INV-2026-0810", "institution": "FIITJEE Ltd",
                 "amount": "₹5,60,000", "plan": "Annual · 6 centres",
                 "status": "paid",    "due": "Jan 15"},
            ]
            filtered = all_invoices
            if search:
                q = search.lower()
                filtered = [i for i in filtered
                            if q in i["institution"].lower() or q in i["id"].lower()]
            if status_f:
                filtered = [i for i in filtered if i["status"] == status_f]
            paged = _paginate(filtered, page, 5)
            return render(request, "exec/partials/fin_invoices.html", {
                "invoices": paged["items"], "search": search, "status_f": status_f,
                "page": paged["page"], "total_pages": paged["total_pages"],
                "total_count": paged["total_count"],
                "has_prev": paged["has_prev"], "has_next": paged["has_next"],
            })
        return HttpResponse(status=400)

    return render(request, "exec/financial_overview.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Financial Overview", "active_nav": "/exec/financial-overview/",
    })


def incidents(request):
    """div-a-12: Incident Manager.
    ?part=table        → incidents table (q, severity, status, page params)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}

    if _is_htmx(request):
        part = request.GET.get("part", "table")
        if part == "table":
            search   = request.GET.get("q", "")
            sev_f    = request.GET.get("severity", "")
            status_f = request.GET.get("status", "")
            page     = int(request.GET.get("page", 1))
            all_incidents = [
                {"id": "INC-2026-0312", "title": "Elevated API latency — South region",
                 "severity": "P1", "status": "open",     "service": "API Gateway",
                 "opened_by": "Priya Sharma", "duration": "17m", "ts": "14:15 Today",
                 "affected": "74,000 students"},
                {"id": "INC-2026-0308", "title": "CDN cache miss spike",
                 "severity": "P2", "status": "resolved", "service": "CDN / Media",
                 "opened_by": "Auto-Monitor", "duration": "42m", "ts": "09:03 Today",
                 "affected": "12,000 students"},
                {"id": "INC-2026-0301", "title": "DB replica lag > 30s",
                 "severity": "P1", "status": "resolved", "service": "Database Cluster",
                 "opened_by": "Rohan Verma",  "duration": "8m",  "ts": "Mar 18 11:22",
                 "affected": "All users"},
                {"id": "INC-2026-0298", "title": "Notification queue backlog",
                 "severity": "P2", "status": "resolved", "service": "Notif Queue",
                 "opened_by": "Auto-Monitor", "duration": "23m", "ts": "Mar 17 08:45",
                 "affected": "~8,000 users"},
                {"id": "INC-2026-0291", "title": "Exam Engine cold start delay",
                 "severity": "P3", "status": "resolved", "service": "Exam Engine",
                 "opened_by": "Rahul Dev",    "duration": "5m",  "ts": "Mar 15 14:00",
                 "affected": "1,200 students"},
                {"id": "INC-2026-0284", "title": "AI proctoring false-positive spike",
                 "severity": "P2", "status": "resolved", "service": "AI / ML Service",
                 "opened_by": "Auto-Monitor", "duration": "31m", "ts": "Mar 14 16:30",
                 "affected": "900 sessions"},
            ]
            filtered = all_incidents
            if search:
                q = search.lower()
                filtered = [i for i in filtered
                            if q in i["title"].lower() or q in i["service"].lower()]
            if sev_f:
                filtered = [i for i in filtered if i["severity"] == sev_f]
            if status_f:
                filtered = [i for i in filtered if i["status"] == status_f]
            paged = _paginate(filtered, page, 8)
            return render(request, "exec/partials/incidents_table.html", {
                "incidents": paged["items"], "search": search,
                "sev_f": sev_f, "status_f": status_f,
                "page": paged["page"], "total_pages": paged["total_pages"],
                "total_count": paged["total_count"],
                "has_prev": paged["has_prev"], "has_next": paged["has_next"],
                "open_count": sum(1 for i in all_incidents if i["status"] == "open"),
            })
        return HttpResponse(status=400)

    return render(request, "exec/incidents_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Incident Manager", "active_nav": "/exec/incidents/",
    })


def incident_detail(request, incident_id):
    """div-a-13: Incident Detail page."""
    guard = _require_exec(request)
    if guard:
        return guard
    return render(request, "exec/incident_detail.html", {
        "incident_id": incident_id, "page_title": f"Incident {incident_id}",
    })


def institutions(request):
    """div-a-06: Institution List.
    ?part=table        → institutions table (q, status, tier, page params)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}

    if _is_htmx(request):
        part     = request.GET.get("part", "table")
        search   = request.GET.get("q", "")
        status_f = request.GET.get("status", "")
        tier_f   = request.GET.get("tier", "")
        page     = int(request.GET.get("page", 1))
        all_insts = [
            {"id": "i1", "name": "Delhi Public Schools Group", "type": "School Chain",
             "tier": "Enterprise", "region": "North", "students": 42318,
             "status": "active", "health": 99.1, "arr": "₹12.4L", "joined": "Jan 2024"},
            {"id": "i2", "name": "Sri Chaitanya Organisation", "type": "Coaching Chain",
             "tier": "Enterprise", "region": "South", "students": 18500,
             "status": "active", "health": 99.7, "arr": "₹8.2L",  "joined": "Mar 2024"},
            {"id": "i3", "name": "Ryan International Schools", "type": "School Chain",
             "tier": "Growth",     "region": "West", "students": 13200,
             "status": "active", "health": 98.4, "arr": "₹6.5L",  "joined": "Jun 2024"},
            {"id": "i4", "name": "Narayana Group",             "type": "Coaching Chain",
             "tier": "Enterprise", "region": "South", "students": 28000,
             "status": "active", "health": 99.9, "arr": "₹9.8L",  "joined": "Feb 2024"},
            {"id": "i5", "name": "Aakash Institute",           "type": "Coaching",
             "tier": "Growth",     "region": "North", "students": 9400,
             "status": "active", "health": 97.2, "arr": "₹4.1L",  "joined": "Aug 2024"},
            {"id": "i6", "name": "FIITJEE Ltd",                "type": "Coaching",
             "tier": "Growth",     "region": "North", "students": 7800,
             "status": "active", "health": 99.3, "arr": "₹5.6L",  "joined": "Sep 2024"},
            {"id": "i7", "name": "Brilliant Tutorials",        "type": "Coaching",
             "tier": "Starter",    "region": "South", "students": 3200,
             "status": "trial",  "health": 98.0, "arr": "₹0",     "joined": "Mar 2025"},
        ]
        filtered = all_insts
        if search:
            q = search.lower()
            filtered = [i for i in filtered
                        if q in i["name"].lower() or q in i["type"].lower()]
        if status_f:
            filtered = [i for i in filtered if i["status"] == status_f]
        if tier_f:
            filtered = [i for i in filtered if i["tier"].lower() == tier_f.lower()]
        paged = _paginate(filtered, page, 10)
        return render(request, "exec/partials/inst_table.html", {
            "institutions": paged["items"], "search": search,
            "status_f": status_f, "tier_f": tier_f,
            "page": paged["page"], "total_pages": paged["total_pages"],
            "total_count": paged["total_count"],
            "has_prev": paged["has_prev"], "has_next": paged["has_next"],
        })

    return render(request, "exec/institutions_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Institutions", "active_nav": "/exec/institutions/",
    })


def institution_detail(request, inst_id):
    """div-a-05: Institution Detail page."""
    guard = _require_exec(request)
    if guard:
        return guard
    return render(request, "exec/institution_detail.html", {
        "inst_id": inst_id, "page_title": "Institution Detail",
    })


def compliance(request):
    """div-a-16: Compliance Dashboard.
    ?part=controls     → controls pass/fail table
    ?part=audits       → upcoming audits list
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    if _is_htmx(request):
        part = request.GET.get("part", "controls")
        return render(request, f"exec/partials/compliance_{part}.html", {})
    return render(request, "exec/compliance_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Compliance", "active_nav": "/exec/compliance/",
    })


def audit_log(request):
    """div-a-17: Audit Log.
    ?part=table        → audit events table (q, category, page)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    if _is_htmx(request):
        search   = request.GET.get("q", "")
        category = request.GET.get("cat", "all")
        page     = int(request.GET.get("page", 1))
        events   = _mock_activity(category if category != "all" else "", search, 0)["events"]
        paged    = _paginate(events, page, 20)
        return render(request, "exec/partials/audit_table.html", {
            "events": paged["items"], "search": search, "category": category,
            "page": paged["page"], "total_pages": paged["total_pages"],
            "total_count": paged["total_count"],
            "has_prev": paged["has_prev"], "has_next": paged["has_next"],
        })
    return render(request, "exec/audit_log_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Audit Log", "active_nav": "/exec/audit-log/",
    })


def reports(request):
    """div-a-24: Executive Reports.
    ?part=list         → reports list table
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    if _is_htmx(request):
        return render(request, "exec/partials/reports_list.html", {})
    return render(request, "exec/reports_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "Executive Reports", "active_nav": "/exec/reports/",
    })


def user_management(request):
    """div-a-29: User Management.
    ?part=table        → users table (q, role, page)
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    if _is_htmx(request):
        search = request.GET.get("q", "")
        role_f = request.GET.get("role", "")
        page   = int(request.GET.get("page", 1))
        all_users = [
            {"id": 1, "name": "Arjun Mehta",   "email": "arjun@eduforge.in",
             "role": "CEO",    "last_login": "Today 14:30", "mfa": True,  "status": "active"},
            {"id": 2, "name": "Priya Sharma",  "email": "priya@eduforge.in",
             "role": "CTO",    "last_login": "Today 13:12", "mfa": True,  "status": "active"},
            {"id": 3, "name": "Rohit Nair",    "email": "rohit@eduforge.in",
             "role": "COO",    "last_login": "Today 11:00", "mfa": True,  "status": "active"},
            {"id": 4, "name": "Supriya Das",   "email": "supriya@eduforge.in",
             "role": "CFO",    "last_login": "Yesterday",   "mfa": False, "status": "active"},
            {"id": 5, "name": "Rahul Dev",     "email": "rahul@eduforge.in",
             "role": "Platform Owner", "last_login": "Today 14:25", "mfa": True, "status": "active"},
        ]
        filtered = all_users
        if search:
            q = search.lower()
            filtered = [u for u in filtered
                        if q in u["name"].lower() or q in u["email"].lower()]
        if role_f:
            filtered = [u for u in filtered if u["role"].lower() == role_f.lower()]
        paged = _paginate(filtered, page, 25)
        return render(request, "exec/partials/users_table.html", {
            "users": paged["items"], "search": search, "role_f": role_f,
            "page": paged["page"], "total_pages": paged["total_pages"],
            "total_count": paged["total_count"],
            "has_prev": paged["has_prev"], "has_next": paged["has_next"],
        })
    return render(request, "exec/user_management_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "User Management", "active_nav": "/exec/settings/users/",
    })


def sla_dashboard(request):
    """div-a-26: SLA Dashboard.
    ?part=table        → SLA compliance table
    ?part=chart        → SLA trend chart
    """
    guard = _require_exec(request)
    if guard:
        return guard if not _is_htmx(request) else HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    if _is_htmx(request):
        part = request.GET.get("part", "table")
        data = _mock_platform_health("30d")
        return render(request, f"exec/partials/sla_{part}.html", data)
    return render(request, "exec/sla_page.html", {
        "user": user, "role": user.get("role", "ceo").lower(),
        "page_title": "SLA Dashboard", "active_nav": "/exec/sla/",
    })


def exec_nav(request):
    """HTMX: dark-themed sidebar nav for executive roles."""
    user = getattr(request, "user_data", {}) or {}
    role = user.get("role", "ceo").lower()

    nav_sections = [
        {
            "label": "COMMAND",
            "items": [
                {"label": "Dashboard",      "url": "/exec/dashboard/",       "icon": "grid"},
                {"label": "WAR ROOM",       "url": "/exec/war-room/",        "icon": "zap",    "badge": None},
                {"label": "Incidents",      "url": "/exec/incidents/",       "icon": "alert-triangle", "badge": 2},
                {"label": "Live Monitoring","url": "/exec/monitoring/",      "icon": "activity"},
            ],
        },
        {
            "label": "OPERATIONS",
            "items": [
                {"label": "Exam Operations","url": "/exec/exam-ops/",        "icon": "clipboard"},
                {"label": "Pre-Exam Ready", "url": "/exec/pre-exam/",        "icon": "check-circle"},
                {"label": "Institutions",   "url": "/exec/institutions/",    "icon": "building"},
                {"label": "Staff Directory","url": "/exec/staff/",           "icon": "users"},
            ],
        },
        {
            "label": "FINANCE",
            "items": [
                {"label": "Financial Overview","url": "/exec/finance/",      "icon": "trending-up"},
                {"label": "Revenue Analytics", "url": "/exec/revenue/",      "icon": "bar-chart-2"},
                {"label": "Billing & Invoices","url": "/exec/billing/",      "icon": "credit-card"},
            ],
        },
        {
            "label": "PLATFORM",
            "items": [
                {"label": "Platform Health","url": "/exec/platform-health/", "icon": "heart"},
                {"label": "Compliance",     "url": "/exec/compliance/",      "icon": "shield"},
                {"label": "Settings",       "url": "/exec/settings/",        "icon": "settings"},
            ],
        },
    ]

    # Role-filter: CFO sees only Finance sections
    if role == "cfo":
        nav_sections = [s for s in nav_sections if s["label"] in ("COMMAND", "FINANCE")]
    # COO hides Finance details
    if role == "coo":
        nav_sections = [s for s in nav_sections if s["label"] != "FINANCE" or s["label"] == "COMMAND"]

    return render(request, "exec/partials/exec_nav.html", {
        "nav_sections": nav_sections,
        "current_url": request.path,
    })


def kpi_bar(request):
    """HTMX: KPI summary cards — polled every 5s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    user = getattr(request, "user_data", {}) or {}
    role = user.get("role", "ceo").lower()
    data = _mock_kpi(role)
    return render(request, "exec/partials/kpi_bar.html", data)


def platform_health(request):
    """HTMX: Platform health chart + service strip — polled every 30s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    range_ = request.GET.get("range", "24h")
    return render(request, "exec/partials/platform_health.html", _mock_platform_health(range_))


def business_overview(request):
    """HTMX: Business growth charts — polled every 5 min."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    tab = request.GET.get("tab", "growth")
    data = _mock_business_overview()
    data["active_tab"] = tab
    return render(request, "exec/partials/business_overview.html", data)


def exam_ops(request):
    """HTMX: Active exams table — polled every 5s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    search = request.GET.get("q", "")
    status_f = request.GET.get("status", "")
    type_f = request.GET.get("type", "")
    return render(request, "exec/partials/exam_ops.html",
                  _mock_exam_ops(search, status_f, type_f))


def revenue_billing(request):
    """HTMX: Revenue charts + subscription donut — polled every 2 min."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    tab = request.GET.get("tab", "mtd")
    return render(request, "exec/partials/revenue_billing.html", _mock_revenue(tab))


def activity_feed(request):
    """HTMX: Activity timeline — polled every 10s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    category = request.GET.get("cat", "all")
    search = request.GET.get("q", "")
    before_id = int(request.GET.get("before", 0))
    return render(request, "exec/partials/activity_feed.html",
                  _mock_activity(category, search, before_id))


# ─────────────────────────────────────────────────────────────────────────────
# Full detail page views  (div-a-02, div-a-03, div-a-08, div-a-12 …)
# ─────────────────────────────────────────────────────────────────────────────

def platform_health_page(request):
    """div-a-02: Platform Health full page shell."""
    guard = _require_exec(request)
    if guard:
        return guard
    user = getattr(request, "user_data", {}) or {}
    return render(request, "exec/platform_health_page.html", {
        "user": user,
        "role": user.get("role", "ceo").lower(),
        "page_title": "Platform Health",
        "active_nav": "/exec/platform-health/",
    })


def ph_chart_partial(request):
    """HTMX: Platform Health full-page chart — polled every 30s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    range_ = request.GET.get("range", "24h")
    metric = request.GET.get("metric", "uptime")
    data = _mock_platform_health(range_)
    data["active_metric"] = metric
    return render(request, "exec/partials/ph_chart.html", data)


def ph_incidents_partial(request):
    """HTMX: Platform Health — recent incidents table."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    incidents = [
        {"id": "INC-2026-0312", "title": "Elevated API latency — South region",
         "severity": "P1", "status": "open",   "duration": "17m", "ts": "14:15"},
        {"id": "INC-2026-0308", "title": "CDN cache miss spike",
         "severity": "P2", "status": "resolved", "duration": "42m", "ts": "09:03"},
        {"id": "INC-2026-0301", "title": "DB replica lag > 30s",
         "severity": "P1", "status": "resolved", "duration": "8m",  "ts": "Mar 18"},
        {"id": "INC-2026-0298", "title": "Notification queue backlog",
         "severity": "P2", "status": "resolved", "duration": "23m", "ts": "Mar 17"},
        {"id": "INC-2026-0291", "title": "Exam Engine cold start delay",
         "severity": "P3", "status": "resolved", "duration": "5m",  "ts": "Mar 15"},
    ]
    return render(request, "exec/partials/ph_incidents.html", {"incidents": incidents})


def exam_ops_page(request):
    """div-a-03: Exam Operations full page shell."""
    guard = _require_exec(request)
    if guard:
        return guard
    user = getattr(request, "user_data", {}) or {}
    return render(request, "exec/exam_ops_page.html", {
        "user": user,
        "role": user.get("role", "ceo").lower(),
        "page_title": "Exam Operations",
        "active_nav": "/exec/exam-ops/",
    })


def eo_table_partial(request):
    """HTMX: Exam Ops full-page table — searched/filtered/paginated."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    search    = request.GET.get("q", "")
    status_f  = request.GET.get("status", "")
    type_f    = request.GET.get("type", "")
    page      = int(request.GET.get("page", 1))
    per_page  = 10
    data      = _mock_exam_ops(search, status_f, type_f)
    exams     = data["exams"]
    total     = len(exams)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page      = max(1, min(page, total_pages))
    start     = (page - 1) * per_page
    data.update({
        "exams": exams[start: start + per_page],
        "page": page, "total_pages": total_pages, "total_count": total,
        "has_prev": page > 1, "has_next": page < total_pages,
        "page_start": start + 1, "page_end": min(start + per_page, total),
        "status_options": [("", "All"), ("running", "Running"), ("paused", "Paused"),
                           ("scheduled", "Scheduled"), ("completed", "Completed")],
        "type_options":   [("", "All Types"), ("mcq", "MCQ"),
                           ("descriptive", "Descriptive"), ("mixed", "Mixed")],
        "active_filter": status_f,
    })
    return render(request, "exec/partials/eo_table.html", data)


def eo_stats_partial(request):
    """HTMX: Exam Ops live stats bar — polled every 5s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    return render(request, "exec/partials/eo_stats.html", {
        "total_active": 3, "total_students": 74018,
        "peak_concurrent": 91, "submissions_min": 12400,
        "avg_latency_ms": 142, "pending_results": 2,
    })


def financial_overview(request):
    """div-a-08: Financial Overview full page shell."""
    guard = _require_exec(request)
    if guard:
        return guard
    user = getattr(request, "user_data", {}) or {}
    return render(request, "exec/financial_overview.html", {
        "user": user,
        "role": user.get("role", "ceo").lower(),
        "page_title": "Financial Overview",
        "active_nav": "/exec/financial-overview/",
    })


def fin_chart_partial(request):
    """HTMX: Financial chart panel — polled every 2 min."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    tab = request.GET.get("tab", "mtd")
    return render(request, "exec/partials/fin_chart.html", _mock_revenue(tab))


def fin_invoices_partial(request):
    """HTMX: Invoice table — searchable/filterable."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    search   = request.GET.get("q", "")
    status_f = request.GET.get("status", "")
    page     = int(request.GET.get("page", 1))
    invoices = [
        {"id": "INV-2026-0847", "institution": "Delhi Public Schools Group",
         "amount": "₹12,40,000", "plan": "Annual · 14 schools",
         "status": "paid",    "due": "Mar 01", "paid_on": "Feb 28"},
        {"id": "INV-2026-0841", "institution": "Sri Chaitanya Organisation",
         "amount": "₹8,20,000", "plan": "Annual · 9 schools",
         "status": "paid",    "due": "Mar 01", "paid_on": "Mar 01"},
        {"id": "INV-2026-0835", "institution": "Ryan International Schools",
         "amount": "₹6,50,000", "plan": "Annual · 7 schools",
         "status": "overdue", "due": "Feb 15", "paid_on": None},
        {"id": "INV-2026-0829", "institution": "Narayana Group",
         "amount": "₹9,80,000", "plan": "Annual · 11 schools",
         "status": "paid",    "due": "Feb 01", "paid_on": "Feb 01"},
        {"id": "INV-2026-0822", "institution": "Aakash Institute",
         "amount": "₹4,10,000", "plan": "Monthly · 5 branches",
         "status": "pending", "due": "Mar 25", "paid_on": None},
        {"id": "INV-2026-0810", "institution": "FIITJEE Ltd",
         "amount": "₹5,60,000", "plan": "Annual · 6 centres",
         "status": "paid",    "due": "Jan 15", "paid_on": "Jan 14"},
    ]
    if search:
        q = search.lower()
        invoices = [i for i in invoices
                    if q in i["institution"].lower() or q in i["id"].lower()]
    if status_f:
        invoices = [i for i in invoices if i["status"] == status_f]
    per_page    = 5
    total       = len(invoices)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    start       = (page - 1) * per_page
    return render(request, "exec/partials/fin_invoices.html", {
        "invoices": invoices[start: start + per_page],
        "search": search, "status_f": status_f,
        "page": page, "total_pages": total_pages, "total_count": total,
        "has_prev": page > 1, "has_next": page < total_pages,
    })


def incidents_page(request):
    """div-a-12: Incident Manager full page shell."""
    guard = _require_exec(request)
    if guard:
        return guard
    user = getattr(request, "user_data", {}) or {}
    return render(request, "exec/incidents_page.html", {
        "user": user,
        "role": user.get("role", "ceo").lower(),
        "page_title": "Incident Manager",
        "active_nav": "/exec/incidents/",
    })


def incidents_table_partial(request):
    """HTMX: Incidents table — polled every 30s."""
    guard = _require_exec(request)
    if guard:
        return HttpResponse(status=403)
    search   = request.GET.get("q", "")
    sev_f    = request.GET.get("severity", "")
    status_f = request.GET.get("status", "")
    page     = int(request.GET.get("page", 1))
    all_incidents = [
        {"id": "INC-2026-0312", "title": "Elevated API latency — South region",
         "severity": "P1", "status": "open",     "service": "API Gateway",
         "opened_by": "Priya Sharma", "duration": "17m", "ts": "14:15 Today",
         "affected": "74,000 students"},
        {"id": "INC-2026-0308", "title": "CDN cache miss spike",
         "severity": "P2", "status": "resolved", "service": "CDN / Media",
         "opened_by": "Auto-Monitor", "duration": "42m", "ts": "09:03 Today",
         "affected": "12,000 students"},
        {"id": "INC-2026-0301", "title": "DB replica lag > 30s",
         "severity": "P1", "status": "resolved", "service": "Database Cluster",
         "opened_by": "Rohan Verma",  "duration": "8m",  "ts": "Mar 18 11:22",
         "affected": "All users"},
        {"id": "INC-2026-0298", "title": "Notification queue backlog",
         "severity": "P2", "status": "resolved", "service": "Notif Queue",
         "opened_by": "Auto-Monitor", "duration": "23m", "ts": "Mar 17 08:45",
         "affected": "~8,000 users"},
        {"id": "INC-2026-0291", "title": "Exam Engine cold start delay",
         "severity": "P3", "status": "resolved", "service": "Exam Engine",
         "opened_by": "Rahul Dev",    "duration": "5m",  "ts": "Mar 15 14:00",
         "affected": "1,200 students"},
        {"id": "INC-2026-0284", "title": "AI proctoring false-positive spike",
         "severity": "P2", "status": "resolved", "service": "AI / ML Service",
         "opened_by": "Auto-Monitor", "duration": "31m", "ts": "Mar 14 16:30",
         "affected": "900 sessions"},
    ]
    incidents = all_incidents
    if search:
        q = search.lower()
        incidents = [i for i in incidents if q in i["title"].lower() or q in i["service"].lower()]
    if sev_f:
        incidents = [i for i in incidents if i["severity"] == sev_f]
    if status_f:
        incidents = [i for i in incidents if i["status"] == status_f]
    per_page    = 8
    total       = len(incidents)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    start       = (page - 1) * per_page
    open_count  = sum(1 for i in all_incidents if i["status"] == "open")
    return render(request, "exec/partials/incidents_table.html", {
        "incidents": incidents[start: start + per_page],
        "search": search, "sev_f": sev_f, "status_f": status_f,
        "page": page, "total_pages": total_pages, "total_count": total,
        "has_prev": page > 1, "has_next": page < total_pages,
        "open_count": open_count,
    })


def incident_detail(request, incident_id):
    """Incident detail page or HTMX drawer."""
    guard = _require_exec(request)
    if guard:
        return guard
    return render(request, "exec/incident_detail.html", {
        "incident_id": incident_id,
        "page_title": f"Incident {incident_id}",
    })
