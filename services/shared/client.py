"""Shared utilities for client type detection, cache control, and criticality flags.

Criticality Flag System
──────────────────────
7 levels control when data refreshes:

  critical  →  0s    No cache. Always live. (live exam, fee due TODAY, active OTP)
  realtime  → 15s    Near-real-time. Background poll / WebSocket. (attendance entry in progress)
  high      → 30s    Refresh immediately in background. (today's schedule, API health)
  medium    → 120s   Normal background refresh. (marks, upcoming tests, KPI bar)
  low       → 300s   Refresh during normal hours. Background sync when idle.
  offpeak   → 1800s  Refresh ONLY during low-traffic window (default: 00:00–06:00 IST).
                     Mobile uses iOS Background Fetch / Android WorkManager.
  static    → 86400s Almost never changes. Bust only on app update or manual flush.
                     (branding, feature flags, syllabus structure)

Low-Traffic Window Logic (offpeak)
───────────────────────────────────
- Backend returns `refresh_window: {"start": "00:00", "end": "06:00", "tz": "Asia/Kolkata"}`
- Mobile SDK schedules background sync in that window
- If device is on WiFi + charging → sync immediately even outside window
- Web: stale-while-revalidate handles it silently
- Server: offpeak sections are pre-computed at midnight and cached until next run
"""

from fastapi import Request
from enum import Enum
from datetime import datetime, time
import pytz


# ── Client Detection ─────────────────────────────────────────────────────────


class ClientType(str, Enum):
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    API = "api"


def detect_client(request: Request) -> ClientType:
    """Detect client type from X-Client-Type header or User-Agent fallback."""
    client_type = request.headers.get("X-Client-Type", "").lower()
    if client_type in ("mobile_ios", "ios"):
        return ClientType.MOBILE_IOS
    if client_type in ("mobile_android", "android"):
        return ClientType.MOBILE_ANDROID
    if client_type == "api":
        return ClientType.API
    ua = request.headers.get("User-Agent", "")
    if "EduForgeIOS" in ua:
        return ClientType.MOBILE_IOS
    if "EduForgeAndroid" in ua:
        return ClientType.MOBILE_ANDROID
    return ClientType.WEB


def is_mobile(client: ClientType) -> bool:
    return client in (ClientType.MOBILE_IOS, ClientType.MOBILE_ANDROID)


# ── Criticality Levels ────────────────────────────────────────────────────────


class Criticality(str, Enum):
    CRITICAL = "critical"  # 0s   — no cache, always live
    REALTIME = "realtime"  # 15s  — near-real-time poll / WebSocket
    HIGH = "high"  # 30s  — immediate background refresh
    MEDIUM = "medium"  # 120s — normal background refresh
    LOW = "low"  # 300s — idle background refresh
    OFFPEAK = "offpeak"  # 1800s — refresh during low-traffic window only
    STATIC = "static"  # 86400s — bust on app update only


CRITICALITY_TTL: dict[str, int] = {
    Criticality.CRITICAL: 0,
    Criticality.REALTIME: 15,
    Criticality.HIGH: 30,
    Criticality.MEDIUM: 120,
    Criticality.LOW: 300,
    Criticality.OFFPEAK: 1800,
    Criticality.STATIC: 86400,
}

# Ordered from most → least urgent (for min-TTL computation)
CRITICALITY_ORDER = [
    Criticality.CRITICAL,
    Criticality.REALTIME,
    Criticality.HIGH,
    Criticality.MEDIUM,
    Criticality.LOW,
    Criticality.OFFPEAK,
    Criticality.STATIC,
]


# ── Section → Criticality Map ─────────────────────────────────────────────────

SECTION_CRITICALITY: dict[str, str] = {
    # ── CRITICAL: no cache, always live ──────────────────────────────────────
    "live_tests_monitor": Criticality.CRITICAL,  # Operator watching live exam
    "live_tests": Criticality.CRITICAL,  # Student attempting live exam
    "alerts": Criticality.CRITICAL,  # Fee due TODAY, exam TODAY
    "fee_status": Criticality.CRITICAL,  # Fee due TODAY — must reflect payment
    "fee_centre": Criticality.CRITICAL,  # Parent about to pay — live balance
    "system_health": Criticality.CRITICAL,  # Platform admin — server down?
    # ── REALTIME: 15s — near real-time ───────────────────────────────────────
    "attendance_entry": Criticality.REALTIME,  # Teacher actively marking attendance
    "marks_entry": Criticality.REALTIME,  # Teacher entering marks
    "api_health": Criticality.REALTIME,  # B2B partner monitoring API errors
    # ── HIGH: 30s — refresh immediately in background ────────────────────────
    "attendance": Criticality.HIGH,  # Student/parent sees today's status
    "today_schedule": Criticality.HIGH,  # Next class is in 10 min
    "timetable": Criticality.HIGH,  # Teacher's schedule for today
    "air_rank": Criticality.HIGH,  # Live exam rank updates
    # ── MEDIUM: 120s — normal background refresh ─────────────────────────────
    "kpi_bar": Criticality.MEDIUM,
    "marks": Criticality.MEDIUM,
    "upcoming_tests": Criticality.MEDIUM,
    "upcoming_events": Criticality.MEDIUM,
    "upcoming_calendar": Criticality.MEDIUM,
    "children_cards": Criticality.MEDIUM,
    "institution_cards": Criticality.MEDIUM,
    "exam_domain_cards": Criticality.MEDIUM,
    "billing": Criticality.MEDIUM,
    "integration_status": Criticality.MEDIUM,
    "usage_analytics": Criticality.MEDIUM,
    "batch_info": Criticality.MEDIUM,
    "messages": Criticality.MEDIUM,
    "student_list": Criticality.MEDIUM,
    "student_ranks": Criticality.MEDIUM,
    "batch_grid": Criticality.MEDIUM,
    "stream_cards": Criticality.MEDIUM,
    "board_countdown": Criticality.MEDIUM,
    "faculty_grid": Criticality.MEDIUM,
    "staff_grid": Criticality.MEDIUM,
    # ── LOW: 300s — refresh when idle ────────────────────────────────────────
    "performance": Criticality.LOW,
    "performance_deep": Criticality.LOW,
    "score_trend_basic": Criticality.LOW,
    "student_performance": Criticality.LOW,
    "faculty_performance": Criticality.LOW,
    "fee_summary": Criticality.LOW,
    "exam_schedule": Criticality.LOW,
    "revenue": Criticality.LOW,
    "tenant_list": Criticality.LOW,
    "content_pipeline": Criticality.LOW,
    "student_acquisition": Criticality.LOW,
    "activity_feed": Criticality.LOW,
    # ── OFFPEAK: 1800s — sync only during low-traffic window ─────────────────
    # These are expensive aggregations — pre-computed at midnight, served stale all day
    "leaderboard": Criticality.OFFPEAK,  # National rank — recomputed nightly
    "ai_study_plan": Criticality.OFFPEAK,  # AI plan — recomputed nightly
    "weak_topics": Criticality.OFFPEAK,  # ML analysis — updated nightly
    "revenue_chart": Criticality.OFFPEAK,  # Historical trend — no intraday change
    "branch_map": Criticality.OFFPEAK,  # Geo data — rarely changes
    "branch_cards": Criticality.OFFPEAK,  # Branch summary — daily refresh enough
    "air_leaderboard": Criticality.OFFPEAK,  # AIR board — post-test compute
    "performance_trend": Criticality.OFFPEAK,  # 30-day trend — daily enough
    # ── STATIC: 86400s — bust on app update only ─────────────────────────────
    "upgrade_banner": Criticality.STATIC,  # Pricing never changes mid-day
    "greeting": Criticality.STATIC,  # "Good morning" template
    "study_plan": Criticality.STATIC,  # Weekly plan — static until Monday
}


# ── Low-Traffic Window ────────────────────────────────────────────────────────

LOW_TRAFFIC_WINDOW = {
    "start": "00:00",  # 12:00 AM IST
    "end": "06:00",  # 06:00 AM IST
    "tz": "Asia/Kolkata",
}


def is_low_traffic_now() -> bool:
    """Returns True if current time is within the low-traffic window (IST)."""
    tz = pytz.timezone(LOW_TRAFFIC_WINDOW["tz"])
    now = datetime.now(tz).time()
    start = time(0, 0)  # 00:00
    end = time(6, 0)  # 06:00
    return start <= now <= end


def seconds_until_low_traffic() -> int:
    """Returns seconds until next low-traffic window starts (for mobile scheduling)."""
    tz = pytz.timezone(LOW_TRAFFIC_WINDOW["tz"])
    now = datetime.now(tz)
    # Next midnight
    from datetime import timedelta

    next_midnight = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if now.time() <= time(6, 0):
        # Already in window — start now
        return 0
    delta = (next_midnight - now).total_seconds()
    return int(delta)


# ── TTL Computation ───────────────────────────────────────────────────────────


def compute_page_cache_ttl(sections: list[str]) -> tuple[int, str]:
    """
    Returns (ttl_seconds, worst_criticality_level).
    Page TTL = TTL of the most-urgent (lowest TTL) section.

    Examples:
      ["greeting", "leaderboard", "alerts"]  → (0, "critical")   alerts dominates
      ["greeting", "leaderboard", "kpi_bar"] → (120, "medium")   kpi_bar dominates
      ["greeting", "leaderboard"]            → (1800, "offpeak")  leaderboard dominates
    """
    worst = Criticality.STATIC
    worst_idx = len(CRITICALITY_ORDER) - 1

    for section in sections:
        level = SECTION_CRITICALITY.get(section, Criticality.MEDIUM)
        idx = (
            CRITICALITY_ORDER.index(level) if level in CRITICALITY_ORDER else worst_idx
        )
        if idx < worst_idx:
            worst_idx = idx
            worst = CRITICALITY_ORDER[idx]

    ttl = CRITICALITY_TTL[worst]
    return ttl, worst


# ── Cache Header Builder ──────────────────────────────────────────────────────


def make_cache_headers(
    ttl: int,
    criticality: str,
    client: ClientType,
    app_version: str = "1.0",
) -> dict:
    """
    Build Cache-Control + refresh-hint headers for both web (CDN) and mobile.

    Web/CDN:
      critical/realtime → no-cache (CDN bypassed, goes to Lambda every time)
      high/medium/low   → s-maxage = TTL (CDN caches at edge)
      offpeak/static    → s-maxage = TTL + stale-while-revalidate = 1hr

    Mobile:
      critical/realtime → no-cache (always hit API)
      high/medium/low   → private max-age = TTL + X-Refresh-Strategy hints
      offpeak           → private max-age = TTL + X-Refresh-Window tells SDK when to sync
      static            → private max-age = TTL (bust only on app version change)
    """
    is_mob = is_mobile(client)

    # ── Critical / Realtime — no cache anywhere ───────────────────────────────
    if criticality in (Criticality.CRITICAL, Criticality.REALTIME):
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "X-Cache-Status": "bypass",
            "X-Criticality": criticality,
        }
        if criticality == Criticality.REALTIME:
            headers["X-Poll-Interval"] = "15"  # Mobile should poll every 15s
        return headers

    # ── Offpeak — refresh during low-traffic window ───────────────────────────
    if criticality == Criticality.OFFPEAK:
        secs_until = seconds_until_low_traffic()
        if is_mob:
            return {
                "Cache-Control": f"private, max-age={ttl}, stale-while-revalidate=3600",
                "Vary": "X-Client-Type, X-App-Version",
                "X-Criticality": Criticality.OFFPEAK,
                "X-Cache-Status": "offpeak",
                "X-Cache-TTL": str(ttl),
                "X-Refresh-Window": f"{LOW_TRAFFIC_WINDOW['start']}-{LOW_TRAFFIC_WINDOW['end']} {LOW_TRAFFIC_WINDOW['tz']}",
                "X-Seconds-Until-Sync": str(secs_until),
                # Mobile hint: sync now if on WiFi+charging, else wait for window
                "X-Sync-Condition": "wifi_and_charging_or_window",
            }
        # Web CDN: cache until next midnight (stale all day is fine for these)
        stale_secs = max(secs_until, 3600)
        return {
            "Cache-Control": f"public, s-maxage={ttl}, stale-while-revalidate={stale_secs}",
            "Vary": "X-Tenant-Slug, X-User-Role",
            "X-Criticality": Criticality.OFFPEAK,
            "X-Cache-Status": "offpeak",
        }

    # ── Static — bust on app version change ──────────────────────────────────
    if criticality == Criticality.STATIC:
        if is_mob:
            return {
                "Cache-Control": f"private, max-age={ttl}, immutable",
                "Vary": "X-App-Version",
                "X-Criticality": Criticality.STATIC,
                "X-Cache-Status": "static",
                "X-Cache-TTL": str(ttl),
                "X-App-Version-Required": app_version,
            }
        return {
            "Cache-Control": f"public, s-maxage={ttl}, stale-while-revalidate=3600",
            "Vary": "Accept-Encoding",
            "X-Criticality": Criticality.STATIC,
            "X-Cache-Status": "static",
        }

    # ── High / Medium / Low — standard TTL cache ─────────────────────────────
    swr = min(ttl, 30)  # stale-while-revalidate = shorter of TTL or 30s
    if is_mob:
        return {
            "Cache-Control": f"private, max-age={ttl}, stale-while-revalidate={swr}",
            "Vary": "X-Client-Type, X-App-Version",
            "X-Cache-TTL": str(ttl),
            "X-Criticality": criticality,
            "X-Cache-Status": "cacheable",
            # Hint to mobile: refresh in background before TTL expires
            "X-Prefetch-At": str(max(ttl - 10, 5)),  # Start prefetch 10s before expiry
        }
    return {
        "Cache-Control": f"public, s-maxage={ttl}, stale-while-revalidate={swr}",
        "Vary": "X-Tenant-Slug, X-User-Role",
        "X-Cache-TTL": str(ttl),
        "X-Criticality": criticality,
        "X-Cache-Status": "cacheable",
    }
