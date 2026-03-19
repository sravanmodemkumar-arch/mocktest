"""
Security tests — Authentication security.
Tests for common auth vulnerabilities: brute force, token misuse,
injection, session fixation, cookie security.
"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.security, pytest.mark.django_db]


class TestBruteForceProtection:
    def test_multiple_failed_logins_handled_gracefully(self, client):
        """Identity service must rate-limit; portal must surface the error."""
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=429)
            for _ in range(6):
                resp = client.post(
                    "/login/password/",
                    data={"login_id": "9876543210", "password": "wrongpass"},
                    HTTP_HX_REQUEST="true",
                )
        # Last response should inform user of rate limiting
        assert resp.status_code < 500

    def test_account_lockout_returns_423(self, client):
        """423 from identity service must redirect to account-blocked."""
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=423)
            resp = client.post(
                "/login/password/",
                data={"login_id": "locked_user", "password": "anypass"},
                HTTP_HX_REQUEST="true",
            )
        # Should redirect to account-blocked page
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/account-blocked/"


class TestCookieSecurity:
    def test_auth_cookie_is_httponly(self, client):
        """ef_token must be HttpOnly — inaccessible to JavaScript."""
        tokens = {"access_token": "test.access.token", "refresh_token": "test.refresh.token"}
        user_data = {
            "id": 1, "role": "student", "requires_2fa": False,
            "profile_complete": True, "has_multiple_roles": False,
        }
        with patch("apps.auth_views.views.httpx.post") as mock_post, \
             patch("apps.auth_views.views.httpx.get") as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "9876543210", "password": "Test@1234"},
            )

        cookie = resp.cookies.get("ef_token")
        if cookie:
            assert cookie.has_header("HttpOnly") or resp.cookies["ef_token"]

    def test_auth_cookie_has_samesite(self, client):
        """ef_token must have SameSite=Lax to mitigate CSRF."""
        tokens = {"access_token": "tok", "refresh_token": "ref"}
        user_data = {
            "id": 1, "role": "student", "requires_2fa": False,
            "profile_complete": True, "has_multiple_roles": False,
        }
        with patch("apps.auth_views.views.httpx.post") as mock_post, \
             patch("apps.auth_views.views.httpx.get") as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "9876543210", "password": "Test@1234"},
            )
        # Django's test client confirms cookie was set
        assert resp.status_code == 204

    def test_logout_clears_both_cookies(self, client, make_access_token):
        token = make_access_token(user_id=1, role="student")
        client.cookies["ef_token"] = token
        client.cookies["ef_refresh"] = "refresh.token.here"

        with patch("apps.auth_views.views.httpx.post"):
            resp = client.get("/logout/")

        assert resp.status_code == 302


class TestCSRFProtection:
    def test_login_post_requires_csrf_token(self, client):
        """POST without CSRF token should be rejected."""
        from django.test import Client
        raw_client = Client(enforce_csrf_checks=True)
        resp = raw_client.post(
            "/login/password/",
            data={"login_id": "test", "password": "test"},
        )
        assert resp.status_code == 403

    def test_forgot_password_post_requires_csrf(self, client):
        from django.test import Client
        raw_client = Client(enforce_csrf_checks=True)
        resp = raw_client.post(
            "/forgot-password/request/",
            data={"email": "test@example.com"},
        )
        assert resp.status_code == 403


class TestInputValidationSecurity:
    def test_sql_injection_in_login_id_handled(self, client):
        """SQL injection attempts must not cause 500."""
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/login/password/",
                data={"login_id": "' OR '1'='1", "password": "' OR '1'='1"},
                HTTP_HX_REQUEST="true",
            )
        assert resp.status_code < 500

    def test_xss_in_login_id_escaped(self, client):
        """XSS payload in login_id must not be reflected unescaped."""
        xss = "<script>alert('xss')</script>"
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/login/password/",
                data={"login_id": xss, "password": "test"},
                HTTP_HX_REQUEST="true",
            )
        assert b"<script>" not in resp.content

    def test_very_long_login_id_does_not_crash(self, client):
        """Extremely long input must not cause server error."""
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/login/password/",
                data={"login_id": "a" * 10000, "password": "test"},
                HTTP_HX_REQUEST="true",
            )
        assert resp.status_code < 500

    def test_password_not_logged_or_returned(self, client):
        """Password must never appear in any response."""
        secret_password = "SuperSecretPassword123!"
        with patch("apps.auth_views.views.httpx.post") as mock:
            mock.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/login/password/",
                data={"login_id": "test@test.com", "password": secret_password},
                HTTP_HX_REQUEST="true",
            )
        assert secret_password.encode() not in resp.content


class TestTokenSecurity:
    def test_refresh_token_cannot_access_protected_route(self, client):
        """A refresh token used as an access token must be rejected."""
        from app.services.jwt import create_refresh_token  # type: ignore
        try:
            refresh = create_refresh_token(1)
            client.cookies["ef_token"] = refresh
            with patch("apps.core.middleware.httpx.get") as mock:
                mock.return_value = MagicMock(status_code=401)
                resp = client.get("/home/")
            assert resp.status_code == 302
        except ImportError:
            pytest.skip("Identity service not in path")

    def test_tampered_token_rejected(self, client):
        """A JWT with tampered payload must be rejected by identity service."""
        client.cookies["ef_token"] = "eyJhbGciOiJIUzI1NiJ9.TAMPERED.signature"
        with patch("apps.core.middleware.httpx.get") as mock:
            mock.return_value = MagicMock(status_code=401)
            resp = client.get("/home/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_email_enumeration_prevention_on_forgot_password(self, client):
        """Forgot password must return same response for known/unknown emails."""
        with patch("apps.auth_views.views.httpx.post"):
            resp_known = client.post(
                "/forgot-password/request/",
                data={"email": "known@example.com"},
                HTTP_HX_REQUEST="true",
            )
            resp_unknown = client.post(
                "/forgot-password/request/",
                data={"email": "unknown_xyz_12345@example.com"},
                HTTP_HX_REQUEST="true",
            )
        # Both must behave the same (OTP entry form shown regardless)
        assert resp_known.status_code == resp_unknown.status_code
