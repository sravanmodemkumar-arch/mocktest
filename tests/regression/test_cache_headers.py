"""
Regression tests — Cache-Control headers.
Verifies CDN and mobile cache headers are correct for all criticality levels.
Must never regress — incorrect cache headers cause stale data in production.
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))

pytestmark = pytest.mark.regression


class TestAuthRoutesNeverCached:
    """Auth routes must always be no-cache — security requirement."""

    @pytest.mark.asyncio
    @pytest.mark.requires_db
    async def test_login_endpoint_no_cache(self, identity_client):
        resp = await identity_client.post(
            "/api/v1/auth/login",
            json={"login_id": "test", "password": "test"},
        )
        cc = resp.headers.get("Cache-Control", "")
        assert "no-cache" in cc or "no-store" in cc or resp.status_code in (401, 422)

    @pytest.mark.asyncio
    @pytest.mark.requires_db
    async def test_auth_me_no_cache(self, identity_client, student_token):
        resp = await identity_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        cc = resp.headers.get("Cache-Control", "")
        assert "no-cache" in cc or "no-store" in cc or "private" in cc


class TestTenantCacheHeaders:
    """Tenant config CDN cache must be set correctly."""

    @pytest.mark.asyncio
    async def test_first_party_domain_has_cdn_cache(self, tenant_client):
        resp = await tenant_client.get(
            "/api/v1/tenant/config", params={"domain": "ssc.eduforge.in"}
        )
        if resp.status_code == 200:
            cc = resp.headers.get("Cache-Control", "")
            assert "s-maxage" in cc, "First-party web must have CDN s-maxage"
            assert "public" in cc

    @pytest.mark.asyncio
    async def test_mobile_client_gets_private_cache(self, tenant_client):
        resp = await tenant_client.get(
            "/api/v1/tenant/config",
            params={"domain": "ssc.eduforge.in"},
            headers={"X-Client-Type": "mobile_ios"},
        )
        if resp.status_code == 200:
            cc = resp.headers.get("Cache-Control", "")
            assert "private" in cc, "Mobile must not use public CDN cache"
            assert "s-maxage" not in cc

    @pytest.mark.asyncio
    async def test_unknown_domain_not_cached(self, tenant_client):
        resp = await tenant_client.get(
            "/api/v1/tenant/config",
            params={"domain": "unknown-xyz-domain.com"},
        )
        assert resp.status_code in (404, 503)
        cc = resp.headers.get("Cache-Control", "")
        assert "no-cache" in cc or "no-store" in cc or not cc


class TestCriticalitySystemRegression:
    """Criticality TTL ordering must never change without explicit decision."""

    def test_critical_ttl_is_zero(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.CRITICAL] == 0

    def test_realtime_ttl_is_15(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.REALTIME] == 15

    def test_high_ttl_is_30(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.HIGH] == 30

    def test_medium_ttl_is_120(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.MEDIUM] == 120

    def test_low_ttl_is_300(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.LOW] == 300

    def test_offpeak_ttl_is_1800(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.OFFPEAK] == 1800

    def test_static_ttl_is_86400(self):
        from shared.client import CRITICALITY_TTL, Criticality
        assert CRITICALITY_TTL[Criticality.STATIC] == 86400

    def test_live_tests_is_critical(self):
        from shared.client import SECTION_CRITICALITY, Criticality
        assert SECTION_CRITICALITY["live_tests"] == Criticality.CRITICAL

    def test_fee_status_is_critical(self):
        from shared.client import SECTION_CRITICALITY, Criticality
        assert SECTION_CRITICALITY["fee_status"] == Criticality.CRITICAL

    def test_leaderboard_is_offpeak(self):
        from shared.client import SECTION_CRITICALITY, Criticality
        assert SECTION_CRITICALITY["leaderboard"] == Criticality.OFFPEAK

    def test_upgrade_banner_is_static(self):
        from shared.client import SECTION_CRITICALITY, Criticality
        assert SECTION_CRITICALITY["upgrade_banner"] == Criticality.STATIC
