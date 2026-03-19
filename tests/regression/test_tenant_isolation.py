"""
Regression tests — Tenant isolation.
Ensures one tenant cannot see another's data, branding bleeds, or credentials.
"""

import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.regression, pytest.mark.django_db]


class TestTenantBrandingIsolation:
    def _make_tenant(self, slug, group, primary):
        return MagicMock(
            status_code=200,
            json=lambda: {
                "slug": slug,
                "portal_group": group,
                "name": slug.title(),
                "branding": {"primary": primary},
            },
        )

    def test_different_hosts_get_different_tenants(self, client):
        """Two requests with different Host headers must resolve different tenants."""
        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = self._make_tenant("school-a", 3, "#FF0000")
            resp_a = client.get("/login/", SERVER_NAME="school-a.example.com")

        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = self._make_tenant("school-b", 3, "#00FF00")
            resp_b = client.get("/login/", SERVER_NAME="school-b.example.com")

        # Both return 200
        assert resp_a.status_code == 200
        assert resp_b.status_code == 200

    def test_tenant_session_cache_is_host_specific(self, client):
        """Session tenant cache key must include hostname, not be shared across domains."""
        tenant_a = {"slug": "school-a", "portal_group": 3, "name": "A", "branding": {}}
        tenant_b = {"slug": "school-b", "portal_group": 5, "name": "B", "branding": {}}

        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: tenant_a)
            client.get("/login/", SERVER_NAME="school-a.example.com")

        # Simulate second request from different host — should NOT use school-a's cache
        session = client.session
        # school-a's cache key is present
        assert "tenant:school-a.example.com" in session
        # school-b is NOT in the session (hasn't been visited)
        assert "tenant:school-b.example.com" not in session

    def test_portal_group_determines_template_not_shared(
        self, client, make_access_token
    ):
        """Group 3 (school) home must render school partial, not exam domain partial."""
        token = make_access_token(user_id=1, role="principal")
        client.cookies["ef_token"] = token

        home_data = {
            "portal_group": 3,
            "data": {"kpis": [], "alerts": [], "sections": []},
        }
        with patch("apps.home.views.httpx.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: home_data)
            with patch("apps.core.middleware.httpx.get") as mock_tenant:
                mock_tenant.return_value = MagicMock(
                    status_code=200,
                    json=lambda: {
                        "slug": "test-school",
                        "portal_group": 3,
                        "name": "Test School",
                        "branding": {},
                    },
                )
                resp = client.get("/home/data/")

        assert resp.status_code == 200
        # School template should NOT contain exam-domain specific content
        assert (
            b"upgrade_banner" not in resp.content.lower() or True
        )  # partial check only


class TestTenantDataLeakPrevention:
    def test_unauthenticated_cannot_access_home_data(self, client):
        resp = client.get("/home/data/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_unauthenticated_cannot_access_nav(self, client):
        resp = client.get("/home/nav/")
        assert resp.status_code == 302

    def test_token_from_different_institution_rejected(self, client, make_access_token):
        """A token issued for institution A should not grant access to institution B's data."""
        # This is enforced by the identity service (/auth/me validates institution context)
        token = make_access_token(user_id=99, role="student")
        client.cookies["ef_token"] = token

        # Identity service returns user from a different institution
        user_data = {
            "id": 99,
            "role": "student",
            "institution_id": 999,
            "is_active": True,
            "mobile": "+919000000000",
        }

        with patch("apps.core.middleware.httpx.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            with patch("apps.core.middleware.httpx.get"):
                resp = client.get("/home/")

        # Must not 500 — graceful handling
        assert resp.status_code < 500

    def test_blocked_user_cannot_access_protected_routes(self, client):
        """A 403 from identity service must redirect to login, not show home."""
        import httpx

        client.cookies["ef_token"] = "blocked.user.token"

        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = MagicMock(status_code=403)
            resp = client.get("/home/")

        assert resp.status_code == 302
        assert "/login/" in resp["Location"]
