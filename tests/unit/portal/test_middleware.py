"""
Unit tests — Django TenantMiddleware and AuthMiddleware.
Uses respx to mock httpx calls — no real network.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


class TestTenantMiddleware:
    def test_tenant_attached_to_request(self, rf, mock_tenant_service):
        """TenantMiddleware must attach tenant dict to request."""
        import django
        django.setup()
        from apps.core.middleware import TenantMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/home/", SERVER_NAME="ssc.eduforge.in")
        request.session = {}

        tenant_data = {
            "slug": "ssc-domain",
            "portal_group": 6,
            "name": "EduForge SSC",
            "branding": {"primary": "#1B5E20"},
        }

        with patch("apps.core.middleware.httpx.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = tenant_data
            mock_get.return_value = mock_resp

            middleware = TenantMiddleware(get_response=lambda r: None)
            middleware.process_request(request)

        assert hasattr(request, "tenant")
        assert request.tenant["slug"] == "ssc-domain"
        assert request.tenant["portal_group"] == 6

    def test_tenant_cached_in_session(self, rf):
        """Second request for same domain uses session cache, not httpx."""
        from apps.core.middleware import TenantMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/home/", SERVER_NAME="ssc.eduforge.in")
        cached = {"slug": "ssc-domain", "portal_group": 6, "name": "SSC", "branding": {}}
        request.session = {"tenant:ssc.eduforge.in": cached}

        with patch("apps.core.middleware.httpx.get") as mock_get:
            middleware = TenantMiddleware(get_response=lambda r: None)
            middleware.process_request(request)
            mock_get.assert_not_called()  # Must use cache

        assert request.tenant["slug"] == "ssc-domain"

    def test_tenant_service_down_uses_default(self, rf):
        """If tenant service times out, fallback to default tenant."""
        from apps.core.middleware import TenantMiddleware
        from django.test import RequestFactory
        import httpx

        factory = RequestFactory()
        request = factory.get("/home/", SERVER_NAME="custom.school.com")
        request.session = {}

        with patch(
            "apps.core.middleware.httpx.get",
            side_effect=httpx.TimeoutException("timeout"),
        ):
            middleware = TenantMiddleware(get_response=lambda r: None)
            middleware.process_request(request)

        assert hasattr(request, "tenant")
        assert request.tenant["portal_group"] == 1  # fallback


class TestAuthMiddleware:
    def test_public_path_skips_auth(self, rf):
        """Login, register, OTP pages must NOT require auth."""
        from apps.core.middleware import AuthMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        for path in ["/login/", "/otp/verify/", "/register/", "/account-blocked/"]:
            request = factory.get(path)
            request.COOKIES = {}

            middleware = AuthMiddleware(get_response=lambda r: None)
            result = middleware.process_request(request)

            assert result is None  # No redirect
            assert request.user_data is None

    def test_no_token_redirects_to_login(self, rf):
        """Request without JWT cookie must redirect to /login/."""
        from apps.core.middleware import AuthMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/home/")
        request.COOKIES = {}

        middleware = AuthMiddleware(get_response=lambda r: None)
        response = middleware.process_request(request)

        assert response is not None
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_valid_token_attaches_user(self, rf, make_access_token):
        """Valid JWT attaches user_data to request."""
        from apps.core.middleware import AuthMiddleware
        from django.test import RequestFactory

        token = make_access_token(user_id=5, role="teacher")
        factory = RequestFactory()
        request = factory.get("/home/")
        request.COOKIES = {"ef_token": token}

        user_data = {"id": 5, "mobile": "+919876543210", "role": "teacher", "is_active": True}

        with patch("apps.core.middleware.httpx.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = user_data
            mock_get.return_value = mock_resp

            middleware = AuthMiddleware(get_response=lambda r: None)
            result = middleware.process_request(request)

        assert result is None  # No redirect
        assert request.user_data["role"] == "teacher"
        assert request.user_data["id"] == 5

    def test_expired_token_triggers_refresh(self, rf):
        """401 from /auth/me must attempt token refresh."""
        from apps.core.middleware import AuthMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/home/")
        request.COOKIES = {"ef_token": "expired.token.here", "ef_refresh": "valid.refresh.token"}

        new_tokens = {"access_token": "new.access.token", "refresh_token": "new.refresh.token"}

        with patch("apps.core.middleware.httpx.get") as mock_get, \
             patch("apps.core.middleware.httpx.post") as mock_post:

            mock_get.return_value = MagicMock(status_code=401)
            mock_post.return_value = MagicMock(status_code=200, json=lambda: new_tokens)

            middleware = AuthMiddleware(get_response=lambda r: None)
            result = middleware.process_request(request)

        # Should attempt refresh, not redirect to login
        mock_post.assert_called_once()
        assert result is None

    def test_blocked_account_redirects(self, rf):
        """If identity returns 403, redirect to account-blocked."""
        from apps.core.middleware import AuthMiddleware
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/home/")
        request.COOKIES = {"ef_token": "blocked.user.token"}

        with patch("apps.core.middleware.httpx.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=403)

            middleware = AuthMiddleware(get_response=lambda r: None)
            response = middleware.process_request(request)

        assert response is not None
        assert response.status_code == 302
        assert "/login/" in response["Location"]
