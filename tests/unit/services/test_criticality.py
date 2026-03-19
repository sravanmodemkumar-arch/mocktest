"""
Unit tests — 7-level criticality flag system.
Tests cache TTL computation and header generation for all levels.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "services"))

from shared.client import (
    Criticality,
    CRITICALITY_TTL,
    SECTION_CRITICALITY,
    compute_page_cache_ttl,
    make_cache_headers,
    ClientType,
    detect_client,
    is_mobile,
    is_low_traffic_now,
    seconds_until_low_traffic,
)

pytestmark = pytest.mark.unit


class TestCriticalityLevels:
    def test_all_levels_defined(self):
        """All 7 criticality levels must exist."""
        for level in ["critical", "realtime", "high", "medium", "low", "offpeak", "static"]:
            assert level in CRITICALITY_TTL

    def test_ttl_ordering(self):
        """TTLs must be ascending from critical → static."""
        levels = ["critical", "realtime", "high", "medium", "low", "offpeak", "static"]
        ttls = [CRITICALITY_TTL[l] for l in levels]
        assert ttls == sorted(ttls), "TTLs must be in ascending order"

    def test_critical_ttl_is_zero(self):
        assert CRITICALITY_TTL[Criticality.CRITICAL] == 0

    def test_static_ttl_is_one_day(self):
        assert CRITICALITY_TTL[Criticality.STATIC] == 86400

    def test_all_sections_have_criticality(self):
        """Every section in SECTION_CRITICALITY must map to a valid level."""
        for section, level in SECTION_CRITICALITY.items():
            assert level in CRITICALITY_TTL, f"Section '{section}' has unknown level '{level}'"


class TestSectionCriticality:
    @pytest.mark.parametrize("section,expected_level", [
        ("live_tests",         Criticality.CRITICAL),
        ("alerts",             Criticality.CRITICAL),
        ("fee_status",         Criticality.CRITICAL),
        ("fee_centre",         Criticality.CRITICAL),
        ("attendance_entry",   Criticality.REALTIME),
        ("api_health",         Criticality.REALTIME),
        ("attendance",         Criticality.HIGH),
        ("today_schedule",     Criticality.HIGH),
        ("kpi_bar",            Criticality.MEDIUM),
        ("marks",              Criticality.MEDIUM),
        ("upcoming_tests",     Criticality.MEDIUM),
        ("leaderboard",        Criticality.OFFPEAK),
        ("ai_study_plan",      Criticality.OFFPEAK),
        ("weak_topics",        Criticality.OFFPEAK),
        ("upgrade_banner",     Criticality.STATIC),
        ("greeting",           Criticality.STATIC),
    ])
    def test_section_criticality_level(self, section, expected_level):
        assert SECTION_CRITICALITY[section] == expected_level


class TestPageTTLComputation:
    def test_critical_section_dominates(self):
        """If any section is critical, page TTL is 0."""
        ttl, level = compute_page_cache_ttl(["greeting", "leaderboard", "alerts"])
        assert ttl == 0
        assert level == Criticality.CRITICAL

    def test_realtime_dominates_over_medium(self):
        ttl, level = compute_page_cache_ttl(["kpi_bar", "attendance_entry", "marks"])
        assert ttl == CRITICALITY_TTL[Criticality.REALTIME]
        assert level == Criticality.REALTIME

    def test_all_static_sections(self):
        ttl, level = compute_page_cache_ttl(["greeting", "upgrade_banner"])
        assert ttl == CRITICALITY_TTL[Criticality.STATIC]
        assert level == Criticality.STATIC

    def test_mixed_low_and_medium(self):
        """Low + medium → TTL is medium (more urgent wins)."""
        ttl, level = compute_page_cache_ttl(["leaderboard", "kpi_bar"])
        assert ttl == CRITICALITY_TTL[Criticality.MEDIUM]
        assert level == Criticality.MEDIUM

    def test_empty_sections(self):
        """Empty sections → fallback to static."""
        ttl, level = compute_page_cache_ttl([])
        assert ttl == CRITICALITY_TTL[Criticality.STATIC]

    def test_unknown_section_defaults_to_medium(self):
        """Unknown section names default to medium."""
        ttl, level = compute_page_cache_ttl(["nonexistent_section_xyz"])
        assert ttl == CRITICALITY_TTL[Criticality.MEDIUM]

    def test_single_critical_section(self):
        ttl, level = compute_page_cache_ttl(["live_tests_monitor"])
        assert ttl == 0
        assert level == Criticality.CRITICAL


class TestCacheHeaders:
    def test_critical_web_no_cache(self):
        headers = make_cache_headers(0, Criticality.CRITICAL, ClientType.WEB)
        assert "no-cache" in headers["Cache-Control"]
        assert "no-store" in headers["Cache-Control"]

    def test_critical_mobile_no_cache(self):
        headers = make_cache_headers(0, Criticality.CRITICAL, ClientType.MOBILE_IOS)
        assert "no-cache" in headers["Cache-Control"]

    def test_realtime_has_poll_interval(self):
        headers = make_cache_headers(15, Criticality.REALTIME, ClientType.MOBILE_ANDROID)
        assert headers.get("X-Poll-Interval") == "15"

    def test_medium_web_uses_s_maxage(self):
        headers = make_cache_headers(120, Criticality.MEDIUM, ClientType.WEB)
        assert "s-maxage=120" in headers["Cache-Control"]
        assert "public" in headers["Cache-Control"]

    def test_medium_mobile_uses_private(self):
        headers = make_cache_headers(120, Criticality.MEDIUM, ClientType.MOBILE_IOS)
        assert "private" in headers["Cache-Control"]
        assert "max-age=120" in headers["Cache-Control"]
        assert "s-maxage" not in headers["Cache-Control"]

    def test_offpeak_mobile_has_refresh_window(self):
        headers = make_cache_headers(1800, Criticality.OFFPEAK, ClientType.MOBILE_ANDROID)
        assert "X-Refresh-Window" in headers
        assert "00:00" in headers["X-Refresh-Window"]
        assert "06:00" in headers["X-Refresh-Window"]
        assert "X-Sync-Condition" in headers

    def test_offpeak_mobile_has_seconds_until_sync(self):
        headers = make_cache_headers(1800, Criticality.OFFPEAK, ClientType.MOBILE_IOS)
        assert "X-Seconds-Until-Sync" in headers
        secs = int(headers["X-Seconds-Until-Sync"])
        assert 0 <= secs <= 86400

    def test_static_mobile_has_immutable(self):
        headers = make_cache_headers(86400, Criticality.STATIC, ClientType.MOBILE_IOS)
        assert "immutable" in headers["Cache-Control"]

    def test_static_mobile_has_app_version(self):
        headers = make_cache_headers(86400, Criticality.STATIC, ClientType.MOBILE_IOS, app_version="2.1")
        assert headers.get("X-App-Version-Required") == "2.1"

    def test_high_web_stale_while_revalidate(self):
        headers = make_cache_headers(30, Criticality.HIGH, ClientType.WEB)
        assert "stale-while-revalidate" in headers["Cache-Control"]

    def test_vary_header_web_vs_mobile(self):
        web_headers = make_cache_headers(120, Criticality.MEDIUM, ClientType.WEB)
        mob_headers = make_cache_headers(120, Criticality.MEDIUM, ClientType.MOBILE_IOS)
        # Web CDN caches by role+tenant, mobile by client type+version
        assert "X-Tenant-Slug" in web_headers.get("Vary", "")
        assert "X-Client-Type" in mob_headers.get("Vary", "")


class TestClientDetection:
    def test_detect_mobile_ios_header(self):
        from unittest.mock import MagicMock
        req = MagicMock()
        req.headers = {"X-Client-Type": "mobile_ios"}
        assert detect_client(req) == ClientType.MOBILE_IOS

    def test_detect_mobile_android_header(self):
        from unittest.mock import MagicMock
        req = MagicMock()
        req.headers = {"X-Client-Type": "mobile_android"}
        assert detect_client(req) == ClientType.MOBILE_ANDROID

    def test_detect_web_no_header(self):
        from unittest.mock import MagicMock
        req = MagicMock()
        req.headers = {}
        assert detect_client(req) == ClientType.WEB

    def test_detect_flutter_user_agent(self):
        from unittest.mock import MagicMock
        req = MagicMock()
        req.headers = {"User-Agent": "EduForgeAndroid/2.1 (android 14)"}
        assert detect_client(req) == ClientType.MOBILE_ANDROID

    def test_is_mobile_true_for_ios(self):
        assert is_mobile(ClientType.MOBILE_IOS) is True

    def test_is_mobile_true_for_android(self):
        assert is_mobile(ClientType.MOBILE_ANDROID) is True

    def test_is_mobile_false_for_web(self):
        assert is_mobile(ClientType.WEB) is False


class TestLowTrafficWindow:
    def test_seconds_until_low_traffic_non_negative(self):
        secs = seconds_until_low_traffic()
        assert secs >= 0

    def test_seconds_until_low_traffic_max_one_day(self):
        secs = seconds_until_low_traffic()
        assert secs <= 86400

    def test_is_low_traffic_returns_bool(self):
        result = is_low_traffic_now()
        assert isinstance(result, bool)
