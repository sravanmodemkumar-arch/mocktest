"""
Unit tests — Executive Dashboard views (apps.exec).

Coverage:
  - Access control: non-exec roles redirected, exec roles allowed
  - Shell view renders correct template
  - All HTMX partial views return 200 + correct template
  - Query param routing (tab, range, search, filter, pagination)
  - Mock data helpers return expected shapes
  - Role-filtered nav sections
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory, override_settings

pytestmark = pytest.mark.unit


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_request(path="/exec/dashboard/", role="ceo", method="GET", **kwargs):
    """Build a Django request with user_data attached (simulates AuthMiddleware)."""
    factory = RequestFactory()
    request = getattr(factory, method.lower())(path, **kwargs)
    request.user_data = {"id": 1, "role": role, "name": "Test User"}
    request.session = {}
    request.tenant = {"slug": "eduforge", "portal_group": 1}
    return request


def _import_views():
    from apps.exec import views
    return views


# ─────────────────────────────────────────────────────────────────────────────
# Access control
# ─────────────────────────────────────────────────────────────────────────────

class TestAccessControl:

    def test_non_exec_role_redirected_from_shell(self):
        views = _import_views()
        for role in ("student", "teacher", "principal", "parent"):
            req = _make_request(role=role)
            resp = views.dashboard_shell(req)
            assert resp.status_code == 302, f"Role {role!r} should be redirected"
            assert resp["Location"] == "/home/"

    def test_exec_roles_allowed_on_shell(self):
        views = _import_views()
        for role in ("ceo", "cto", "coo", "cfo", "platform_owner"):
            req = _make_request(role=role)
            resp = views.dashboard_shell(req)
            assert resp.status_code == 200, f"Role {role!r} should be allowed"

    def test_non_exec_role_gets_403_on_kpi(self):
        views = _import_views()
        req = _make_request(role="student")
        resp = views.kpi_bar(req)
        assert resp.status_code == 403

    def test_non_exec_role_gets_403_on_platform_health(self):
        views = _import_views()
        req = _make_request(role="teacher")
        resp = views.platform_health(req)
        assert resp.status_code == 403

    def test_no_user_data_redirected(self):
        """Request with no user_data (unauthenticated) treated as non-exec."""
        views = _import_views()
        factory = RequestFactory()
        req = factory.get("/exec/dashboard/")
        req.user_data = None
        req.session = {}
        req.tenant = {}
        resp = views.dashboard_shell(req)
        assert resp.status_code == 302


# ─────────────────────────────────────────────────────────────────────────────
# Shell view
# ─────────────────────────────────────────────────────────────────────────────

class TestDashboardShell:

    def test_renders_dashboard_template(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.dashboard_shell(req)
        assert resp.status_code == 200
        assert "exec/dashboard.html" in [t.name for t in resp.templates]

    def test_context_has_role(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.dashboard_shell(req)
        assert resp.context["role"] == "cfo"

    def test_context_has_page_title(self):
        views = _import_views()
        req = _make_request()
        resp = views.dashboard_shell(req)
        assert resp.context["page_title"] == "Executive Dashboard"


# ─────────────────────────────────────────────────────────────────────────────
# KPI bar
# ─────────────────────────────────────────────────────────────────────────────

class TestKpiBar:

    def test_returns_200_for_ceo(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.kpi_bar(req)
        assert resp.status_code == 200

    def test_renders_kpi_template(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.kpi_bar(req)
        assert "exec/partials/kpi_bar.html" in [t.name for t in resp.templates]

    def test_context_has_platform_health(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.kpi_bar(req)
        ctx = resp.context
        assert "platform_health" in ctx
        assert "value" in ctx["platform_health"]
        assert "status" in ctx["platform_health"]

    def test_context_has_active_exams(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.kpi_bar(req)
        assert "active_exams" in resp.context
        assert "concurrent" in resp.context["active_exams"]

    def test_context_has_revenue_for_ceo(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.kpi_bar(req)
        assert "revenue" in resp.context

    def test_context_role_passed_correctly(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.kpi_bar(req)
        assert resp.context["role"] == "cfo"


# ─────────────────────────────────────────────────────────────────────────────
# Platform health
# ─────────────────────────────────────────────────────────────────────────────

class TestPlatformHealth:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        assert resp.status_code == 200

    def test_renders_platform_health_template(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        assert "exec/partials/platform_health.html" in [t.name for t in resp.templates]

    def test_default_range_is_24h(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        assert resp.context["range"] == "24h"

    @pytest.mark.parametrize("range_", ["1h", "6h", "24h", "7d"])
    def test_accepts_all_time_ranges(self, range_):
        views = _import_views()
        req = _make_request(role="cto", path=f"/exec/dashboard/platform-health/?range={range_}")
        req = RequestFactory().get("/exec/dashboard/platform-health/", {"range": range_})
        req.user_data = {"id": 1, "role": "cto"}
        req.session = {}
        resp = views.platform_health(req)
        assert resp.status_code == 200
        assert resp.context["range"] == range_

    def test_context_has_services_list(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        services = resp.context["services"]
        assert isinstance(services, list)
        assert len(services) > 0
        assert "name" in services[0]
        assert "status" in services[0]

    def test_context_has_json_series(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        ctx = resp.context
        # All JSON fields must be valid JSON strings
        for field in ("labels_json", "uptime_json", "latency_json", "error_rate_json"):
            assert field in ctx
            parsed = json.loads(ctx[field])
            assert isinstance(parsed, list)
            assert len(parsed) > 0

    def test_label_count_matches_data_count(self):
        views = _import_views()
        req = _make_request(role="cto")
        resp = views.platform_health(req)
        ctx = resp.context
        n_labels = len(json.loads(ctx["labels_json"]))
        assert len(json.loads(ctx["uptime_json"])) == n_labels
        assert len(json.loads(ctx["latency_json"])) == n_labels
        assert len(json.loads(ctx["error_rate_json"])) == n_labels


# ─────────────────────────────────────────────────────────────────────────────
# Business overview
# ─────────────────────────────────────────────────────────────────────────────

class TestBusinessOverview:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.business_overview(req)
        assert resp.status_code == 200

    def test_renders_business_template(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.business_overview(req)
        assert "exec/partials/business_overview.html" in [t.name for t in resp.templates]

    def test_default_tab_is_growth(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.business_overview(req)
        assert resp.context["active_tab"] == "growth"

    @pytest.mark.parametrize("tab", ["growth", "geo", "type"])
    def test_tab_switching(self, tab):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/business/", {"tab": tab})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.business_overview(req)
        assert resp.status_code == 200
        assert resp.context["active_tab"] == tab

    def test_context_has_institution_counts(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.business_overview(req)
        ctx = resp.context
        assert "total_institutions" in ctx
        assert int(ctx["total_institutions"]) > 0

    def test_context_has_chart_json(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.business_overview(req)
        ctx = resp.context
        for field in ("months_json", "inst_new_json", "student_growth_json"):
            assert field in ctx
            parsed = json.loads(ctx[field])
            assert isinstance(parsed, list)


# ─────────────────────────────────────────────────────────────────────────────
# Exam operations
# ─────────────────────────────────────────────────────────────────────────────

class TestExamOps:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="coo")
        resp = views.exam_ops(req)
        assert resp.status_code == 200

    def test_renders_exam_ops_template(self):
        views = _import_views()
        req = _make_request(role="coo")
        resp = views.exam_ops(req)
        assert "exec/partials/exam_ops.html" in [t.name for t in resp.templates]

    def test_search_filters_exams(self):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/exam-ops/", {"q": "JEE"})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.exam_ops(req)
        exams = resp.context["exams"]
        assert all("JEE" in e["name"] or "JEE" in e["institution"] for e in exams)

    def test_search_empty_returns_no_results(self):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/exam-ops/", {"q": "ZZZNOMATCH9999"})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.exam_ops(req)
        assert resp.context["exams"] == []

    def test_no_search_returns_all_exams(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exam_ops(req)
        assert len(resp.context["exams"]) > 0

    def test_context_has_summary(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exam_ops(req)
        ctx = resp.context
        assert "summary" in ctx
        assert "active_exams" in ctx["summary"]
        assert "concurrent" in ctx["summary"]


# ─────────────────────────────────────────────────────────────────────────────
# Revenue & billing
# ─────────────────────────────────────────────────────────────────────────────

class TestRevenueBilling:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.revenue_billing(req)
        assert resp.status_code == 200

    def test_renders_revenue_template(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.revenue_billing(req)
        assert "exec/partials/revenue_billing.html" in [t.name for t in resp.templates]

    def test_default_tab_is_mtd(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.revenue_billing(req)
        assert resp.context["tab"] == "mtd"

    @pytest.mark.parametrize("tab", ["mtd", "ytd"])
    def test_tab_switching(self, tab):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/revenue/", {"tab": tab})
        req.user_data = {"id": 1, "role": "cfo"}
        req.session = {}
        resp = views.revenue_billing(req)
        assert resp.status_code == 200
        assert resp.context["tab"] == tab

    def test_context_has_donut_data(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.revenue_billing(req)
        ctx = resp.context
        assert "donut" in ctx
        donut = ctx["donut"]
        assert isinstance(donut, list)
        assert len(donut) > 0
        total_pct = sum(d["value"] for d in donut)
        assert total_pct == 100, "Donut segments must sum to 100%"

    def test_context_has_json_fields(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.revenue_billing(req)
        ctx = resp.context
        for field in ("donut_labels_json", "donut_values_json", "donut_colors_json"):
            assert field in ctx
            parsed = json.loads(ctx[field])
            assert isinstance(parsed, list)

    def test_403_for_non_exec(self):
        views = _import_views()
        req = _make_request(role="student")
        resp = views.revenue_billing(req)
        assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Activity feed
# ─────────────────────────────────────────────────────────────────────────────

class TestActivityFeed:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.activity_feed(req)
        assert resp.status_code == 200

    def test_renders_activity_template(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.activity_feed(req)
        assert "exec/partials/activity_feed.html" in [t.name for t in resp.templates]

    def test_category_filter_all(self):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/activity/", {"cat": "all"})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.activity_feed(req)
        assert resp.status_code == 200
        assert len(resp.context["events"]) > 0

    @pytest.mark.parametrize("cat", ["config", "infra", "incident", "billing", "exam", "compliance"])
    def test_category_filter_specific(self, cat):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/activity/", {"cat": cat})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.activity_feed(req)
        assert resp.status_code == 200
        events = resp.context["events"]
        assert all(e["category"] == cat for e in events), \
            f"All events should have category={cat!r}"

    def test_search_filters_events(self):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/activity/", {"q": "JEE"})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.activity_feed(req)
        events = resp.context["events"]
        assert all(
            "jee" in e["summary"].lower() or "jee" in e["actor"].lower()
            for e in events
        )

    def test_search_no_match_returns_empty(self):
        views = _import_views()
        req = RequestFactory().get("/exec/dashboard/activity/", {"q": "ZZZNONESUCH9999"})
        req.user_data = {"id": 1, "role": "ceo"}
        req.session = {}
        resp = views.activity_feed(req)
        assert resp.context["events"] == []

    def test_context_has_category_field(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.activity_feed(req)
        assert "category" in resp.context


# ─────────────────────────────────────────────────────────────────────────────
# Exec nav
# ─────────────────────────────────────────────────────────────────────────────

class TestExecNav:

    def test_returns_200(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exec_nav(req)
        assert resp.status_code == 200

    def test_renders_nav_template(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exec_nav(req)
        assert "exec/partials/exec_nav.html" in [t.name for t in resp.templates]

    def test_nav_has_sections(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exec_nav(req)
        sections = resp.context["nav_sections"]
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_each_section_has_items(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exec_nav(req)
        for section in resp.context["nav_sections"]:
            assert "label" in section
            assert "items" in section
            assert len(section["items"]) > 0

    def test_cfo_sees_finance_section(self):
        views = _import_views()
        req = _make_request(role="cfo")
        resp = views.exec_nav(req)
        section_labels = [s["label"] for s in resp.context["nav_sections"]]
        assert "FINANCE" in section_labels

    def test_all_nav_items_have_url(self):
        views = _import_views()
        req = _make_request(role="ceo")
        resp = views.exec_nav(req)
        for section in resp.context["nav_sections"]:
            for item in section["items"]:
                assert "url" in item
                assert item["url"].startswith("/")


# ─────────────────────────────────────────────────────────────────────────────
# Mock data helpers — unit tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMockHelpers:

    def test_mock_kpi_platform_health_has_required_keys(self):
        from apps.exec.views import _mock_kpi
        data = _mock_kpi("ceo")
        ph = data["platform_health"]
        assert "value" in ph
        assert "status" in ph
        assert ph["status"] in ("healthy", "warning", "critical")

    def test_mock_kpi_active_exams_concurrent_is_int(self):
        from apps.exec.views import _mock_kpi
        data = _mock_kpi("ceo")
        assert isinstance(data["active_exams"]["concurrent"], int)

    def test_mock_platform_health_series_lengths_match(self):
        from apps.exec.views import _mock_platform_health
        for rng in ("1h", "6h", "24h", "7d"):
            data = _mock_platform_health(rng)
            labels = json.loads(data["labels_json"])
            uptime = json.loads(data["uptime_json"])
            assert len(labels) == len(uptime), f"Mismatch for range={rng}"

    def test_mock_business_overview_geo_data_is_dict(self):
        from apps.exec.views import _mock_business_overview
        data = _mock_business_overview()
        geo = json.loads(data["geo_data_json"])
        assert isinstance(geo, dict)
        assert len(geo) > 0

    def test_mock_revenue_donut_sums_to_100(self):
        from apps.exec.views import _mock_revenue
        data = _mock_revenue("mtd")
        total = sum(d["value"] for d in data["donut"])
        assert total == 100

    def test_mock_activity_all_events_have_required_keys(self):
        from apps.exec.views import _mock_activity
        data = _mock_activity("all", "", 0)
        for event in data["events"]:
            assert "id" in event
            assert "category" in event
            assert "summary" in event
            assert "actor" in event

    def test_mock_exam_ops_search_case_insensitive(self):
        from apps.exec.views import _mock_exam_ops
        data = _mock_exam_ops(search="jee")
        assert all(
            "jee" in e["name"].lower() or "jee" in e["institution"].lower()
            for e in data["exams"]
        )
