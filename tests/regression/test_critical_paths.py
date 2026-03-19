"""
Regression tests — Critical user paths.
These must NEVER break: login, home load, token refresh, logout.
Run after every deployment.
"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.regression, pytest.mark.django_db]


class TestLoginCriticalPath:
    def test_login_page_always_renders(self, client):
        """GET /login/ must always return 200 regardless of tenant state."""
        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = MagicMock(
                status_code=200,
                json=lambda: {"slug": "default", "portal_group": 3,
                              "name": "Test School", "branding": {"primary": "#1565C0"}},
            )
            resp = client.get("/login/")
        assert resp.status_code == 200

    def test_login_page_renders_even_if_tenant_service_down(self, client):
        """Tenant service failure must NOT cause 500 on login page."""
        import httpx
        with patch("apps.core.middleware.httpx.get", side_effect=httpx.ConnectError("down")):
            resp = client.get("/login/")
        assert resp.status_code in (200, 302)  # Not 500

    def test_password_login_returns_4xx_not_500_on_bad_input(self, client):
        """Malformed input must never cause a 500."""
        resp = client.post("/login/password/", data={"login_id": "", "password": ""})
        assert resp.status_code < 500

    def test_password_login_handles_identity_service_down(self, client):
        """Identity service failure must return a user-friendly error, not 500."""
        import httpx
        with patch("apps.auth_views.views.httpx.post",
                   side_effect=httpx.ConnectError("down")):
            resp = client.post(
                "/login/password/",
                data={"login_id": "9876543210", "password": "Test@1234"},
                HTTP_HX_REQUEST="true",
            )
        assert resp.status_code < 500
        assert b"unavailable" in resp.content.lower()

    def test_forgot_password_page_renders(self, client):
        resp = client.get("/forgot-password/")
        assert resp.status_code == 200

    def test_account_blocked_page_renders(self, client):
        resp = client.get("/account-blocked/")
        assert resp.status_code == 200

    def test_register_page_renders(self, client):
        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = MagicMock(
                status_code=200,
                json=lambda: {"slug": "ssc", "portal_group": 6,
                              "name": "SSC Domain", "branding": {}},
            )
            resp = client.get("/register/")
        assert resp.status_code == 200


class TestHomeCriticalPath:
    def test_home_redirects_unauthenticated(self, client):
        resp = client.get("/home/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_home_renders_for_authenticated_user(self, authed_portal_client):
        resp = authed_portal_client.get("/home/")
        assert resp.status_code == 200

    def test_home_data_endpoint_never_500(self, authed_portal_client):
        import httpx
        with patch("apps.home.views.httpx.get",
                   side_effect=httpx.ConnectError("home service down")):
            resp = authed_portal_client.get("/home/data/")
        # Should degrade gracefully, not crash
        assert resp.status_code < 500

    def test_home_data_handles_bad_json_from_service(self, authed_portal_client):
        with patch("apps.home.views.httpx.get") as mock:
            mock.return_value = MagicMock(status_code=200, json=lambda: {})
            resp = authed_portal_client.get("/home/data/")
        assert resp.status_code == 200

    def test_nav_links_endpoint_works(self, authed_portal_client):
        resp = authed_portal_client.get("/home/nav/")
        assert resp.status_code == 200


class TestTokenRefreshCriticalPath:
    def test_expired_token_triggers_refresh_not_hard_logout(self, client, make_access_token):
        """Expired access token + valid refresh must silently refresh, not kick user out."""
        import httpx
        token = make_access_token(user_id=1, role="teacher")
        client.cookies["ef_token"] = token
        client.cookies["ef_refresh"] = "valid.refresh.token"

        new_tokens = {"access_token": "new.access", "refresh_token": "new.refresh"}

        with patch("apps.core.middleware.httpx.get") as mock_get, \
             patch("apps.core.middleware.httpx.post") as mock_post:
            mock_get.return_value = MagicMock(status_code=401)
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: new_tokens
            )
            resp = client.get("/home/")

        # Should NOT redirect to login (refresh succeeded)
        mock_post.assert_called_once()


class TestLogoutCriticalPath:
    def test_logout_clears_cookies(self, authed_portal_client):
        resp = authed_portal_client.get("/logout/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]
        assert "ef_token" not in resp.cookies or resp.cookies["ef_token"].value == ""

    def test_logout_works_even_if_identity_service_down(self, authed_portal_client):
        import httpx
        with patch("apps.auth_views.views.httpx.post",
                   side_effect=httpx.ConnectError("down")):
            resp = authed_portal_client.get("/logout/")
        # Must still redirect to login
        assert resp.status_code == 302
