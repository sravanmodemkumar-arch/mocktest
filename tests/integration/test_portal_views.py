"""
Integration tests — Django portal views.
Uses pytest-django's client fixture. Mocks httpx calls to backend services.
"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestLoginView:
    def test_login_page_renders(self, client):
        with patch("apps.core.middleware.httpx.get") as mock_tenant:
            mock_tenant.return_value = MagicMock(
                status_code=200,
                json=lambda: {"slug": "test", "portal_group": 3, "name": "Test", "branding": {"primary": "#1565C0"}},
            )
            resp = client.get("/login/", SERVER_NAME="school.test.com")
        assert resp.status_code == 200
        assert b"Welcome back" in resp.content

    def test_login_page_has_mobile_input(self, client):
        with patch("apps.core.middleware.httpx.get") as mock_tenant:
            mock_tenant.return_value = MagicMock(status_code=200, json=lambda: {
                "slug": "test", "portal_group": 3, "name": "Test", "branding": {}
            })
            resp = client.get("/login/")
        assert b'name="mobile"' in resp.content
        assert b'type="tel"' in resp.content

    def test_login_redirects_to_home_if_authed(self, client, student_token):
        client.cookies["ef_token"] = student_token
        resp = client.get("/login/")
        assert resp.status_code == 302
        assert "/home/" in resp["Location"]

    def test_login_page_shows_brand_logo(self, client):
        with patch("apps.core.middleware.httpx.get") as mock_tenant:
            mock_tenant.return_value = MagicMock(status_code=200, json=lambda: {
                "slug": "xyz-school",
                "portal_group": 3,
                "name": "XYZ School",
                "branding": {"primary": "#1565C0", "logo": "https://cdn.eduforge.in/logos/xyz.svg"},
            })
            resp = client.get("/login/", SERVER_NAME="www.xyzschool.com")
        assert b"XYZ School" in resp.content


class TestOTPSendView:
    def test_valid_mobile_sends_otp(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: {"message": "OTP sent"})
            resp = client.post(
                "/otp/send/",
                data={"mobile": "9876543210"},
                HTTP_HX_REQUEST="true",
            )
        # HTMX endpoint returns 204 + HX-Redirect
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/otp/verify/"

    def test_short_mobile_returns_error(self, client):
        resp = client.post(
            "/otp/send/",
            data={"mobile": "12345"},
            HTTP_HX_REQUEST="true",
        )
        assert resp.status_code == 200
        assert b"valid 10-digit" in resp.content

    def test_non_numeric_mobile_returns_error(self, client):
        resp = client.post(
            "/otp/send/",
            data={"mobile": "abcdefghij"},
            HTTP_HX_REQUEST="true",
        )
        assert b"valid" in resp.content

    def test_identity_service_down_returns_error(self, client):
        import httpx
        with patch("apps.auth_views.views.httpx.post", side_effect=httpx.ConnectError("down")):
            resp = client.post(
                "/otp/send/",
                data={"mobile": "9876543210"},
                HTTP_HX_REQUEST="true",
            )
        assert b"unavailable" in resp.content.lower()

    def test_rate_limited_shows_429_message(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=429)
            resp = client.post("/otp/send/", data={"mobile": "9876543210"})
        assert b"Too many" in resp.content


class TestOTPVerifyView:
    def test_otp_page_renders_with_session(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session["otp_channel"] = "whatsapp"
        session.save()

        resp = client.get("/otp/verify/")
        assert resp.status_code == 200
        assert b"Enter OTP" in resp.content
        assert b"9876543210" in resp.content

    def test_otp_page_redirects_without_session(self, client):
        resp = client.get("/otp/verify/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_correct_otp_sets_cookie(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        tokens = {"access_token": "test.access.token", "refresh_token": "test.refresh.token"}
        user_data = {"id": 1, "mobile": "+919876543210", "role": "student",
                     "requires_2fa": False, "profile_complete": True, "has_multiple_roles": False}

        with patch("apps.auth_views.views.httpx.post") as mock_post, \
             patch("apps.auth_views.views.httpx.get") as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)

            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp.status_code == 204
        assert "ef_token" in resp.cookies

    def test_wrong_otp_returns_401_html(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "000000"},
            )

        assert resp.status_code == 401
        assert b"Incorrect" in resp.content

    def test_2fa_required_redirects_to_2fa(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        tokens = {"access_token": "tok", "refresh_token": "ref"}
        user_data = {"id": 2, "role": "principal", "requires_2fa": True,
                     "profile_complete": True, "has_multiple_roles": False}

        with patch("apps.auth_views.views.httpx.post") as mock_post, \
             patch("apps.auth_views.views.httpx.get") as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)

            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp["HX-Redirect"] == "/2fa/"


class TestHomeView:
    def test_home_redirects_unauthenticated(self, client):
        resp = client.get("/home/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_home_renders_for_authenticated_user(self, authed_portal_client):
        resp = authed_portal_client.get("/home/")
        assert resp.status_code == 200
        assert b"home-content" in resp.content  # HTMX container

    def test_home_data_loads_correct_group_template(self, authed_portal_client):
        home_data = {
            "portal_group": 6,
            "data": {
                "greeting": {"title": "Welcome back"},
                "kpis": [],
                "sections": [{"id": "test_series", "criticality": "medium"}],
            }
        }
        with patch("apps.home.views.httpx.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, json=lambda: home_data)
            resp = authed_portal_client.get("/home/data/")

        assert resp.status_code == 200

    def test_home_data_shows_upgrade_banner_for_free(self, client, make_access_token):
        free_token = make_access_token(user_id=3, role="student")
        client.cookies["ef_token"] = free_token

        home_data = {
            "portal_group": 6,
            "data": {
                "sections": [{"id": "upgrade_banner", "criticality": "static"}],
                "upgrade_banner": {
                    "heading": "Upgrade to Premium",
                    "price_monthly": 299,
                    "features": [],
                },
                "kpis": [],
                "alerts": [],
            }
        }

        with patch("apps.home.views.httpx.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200, json=lambda: home_data)
            resp = client.get("/home/data/")

        assert resp.status_code == 200
