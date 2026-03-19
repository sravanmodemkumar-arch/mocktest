"""
Integration tests — auth views coverage.
Covers password_login, role selection, profile, 2FA, register, logout,
forgot-password, and session reauth flows.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

_ME_OK = {"id": 1, "role": "student", "is_active": True}
_ME_MOCK = MagicMock(status_code=200, json=lambda: _ME_OK)


def _authed(client, token):
    """Set up authenticated client: set cookie + patch httpx.get for middleware."""
    client.cookies["ef_token"] = token
    return patch("httpx.get", return_value=_ME_MOCK)


# ── password_login ──────────────────────────────────────────────────────────


class TestPasswordLogin:
    def test_missing_fields_returns_error(self, client):
        resp = client.post("/login/password/", data={})
        assert resp.status_code == 200
        assert b"Please enter your mobile/email and password" in resp.content

    def test_missing_password_returns_error(self, client):
        resp = client.post("/login/password/", data={"login_id": "user"})
        assert resp.status_code == 200
        assert b"Please enter your mobile/email and password" in resp.content

    def test_successful_login_sets_cookies(self, client):
        tokens = {"access_token": "acc.tok.en", "refresh_token": "ref.tok.en"}
        user_data = {
            "id": 1,
            "role": "student",
            "requires_2fa": False,
            "profile_complete": True,
            "has_multiple_roles": False,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "9876543210", "password": "pass123"},
            )

        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/home/"
        assert "ef_token" in resp.cookies

    def test_staff_role_with_2fa_redirects_to_2fa(self, client):
        tokens = {"access_token": "acc", "refresh_token": "ref"}
        user_data = {
            "id": 2,
            "role": "principal",
            "requires_2fa": True,
            "profile_complete": True,
            "has_multiple_roles": False,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "admin@school.com", "password": "pass"},
            )

        assert resp["HX-Redirect"] == "/2fa/"

    def test_incomplete_profile_redirects(self, client):
        tokens = {"access_token": "acc", "refresh_token": "ref"}
        user_data = {
            "id": 3,
            "role": "student",
            "requires_2fa": False,
            "profile_complete": False,
            "has_multiple_roles": False,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "pass"},
            )

        assert resp["HX-Redirect"] == "/setup-profile/"

    def test_multiple_roles_redirects(self, client):
        tokens = {"access_token": "acc", "refresh_token": "ref"}
        user_data = {
            "id": 4,
            "role": "teacher",
            "requires_2fa": False,
            "profile_complete": True,
            "has_multiple_roles": True,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "pass"},
            )

        assert resp["HX-Redirect"] == "/select-role/"

    def test_wrong_password_returns_401_message(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=401)
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "wrong"},
            )

        assert b"Incorrect" in resp.content

    def test_account_locked_redirects(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=423)
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "pass"},
            )

        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/account-blocked/"

    def test_server_error_returns_generic_message(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=500)
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "pass"},
            )

        assert b"Login failed" in resp.content

    def test_service_down_returns_unavailable(self, client):
        import httpx

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(
                "/login/password/",
                data={"login_id": "user", "password": "pass"},
            )

        assert b"unavailable" in resp.content.lower()


# ── OTP edge cases ──────────────────────────────────────────────────────────


class TestOTPEdgeCases:
    def test_otp_verify_submit_missing_mobile_session(self, client):
        resp = client.post("/otp/verify/submit/", data={"otp": "123456"})
        assert resp.status_code == 400

    def test_otp_verify_submit_short_otp(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()
        resp = client.post("/otp/verify/submit/", data={"otp": "123"})
        assert resp.status_code == 400

    def test_otp_verify_submit_account_locked(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=423)
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/account-blocked/"

    def test_otp_verify_submit_generic_error(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=500)
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp.status_code == 400
        assert b"Verification failed" in resp.content

    def test_otp_verify_submit_service_down(self, client):
        import httpx

        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp.status_code == 503

    def test_otp_send_generic_failure(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=500)
            resp = client.post(
                "/otp/send/",
                data={"mobile": "9876543210"},
                HTTP_HX_REQUEST="true",
            )

        assert b"Failed to send OTP" in resp.content

    def test_otp_verify_submit_profile_incomplete(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        tokens = {"access_token": "tok", "refresh_token": "ref"}
        user_data = {
            "id": 5,
            "role": "student",
            "requires_2fa": False,
            "profile_complete": False,
            "has_multiple_roles": False,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp["HX-Redirect"] == "/setup-profile/"

    def test_otp_verify_submit_multiple_roles(self, client):
        session = client.session
        session["otp_mobile"] = "9876543210"
        session.save()

        tokens = {"access_token": "tok", "refresh_token": "ref"}
        user_data = {
            "id": 6,
            "role": "teacher",
            "requires_2fa": False,
            "profile_complete": True,
            "has_multiple_roles": True,
        }

        with patch("apps.auth_views.views.httpx.post") as mock_post, patch(
            "apps.auth_views.views.httpx.get"
        ) as mock_get:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: tokens)
            mock_get.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.post(
                "/otp/verify/submit/",
                data={"mobile": "9876543210", "otp": "123456"},
            )

        assert resp["HX-Redirect"] == "/select-role/"


# ── Role selection ──────────────────────────────────────────────────────────


class TestSelectRole:
    def test_select_role_renders(self, client, student_token):
        client.cookies["ef_token"] = student_token
        with patch("apps.auth_views.views.httpx.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"roles": [{"id": 1, "name": "student"}]},
            )
            resp = client.get("/select-role/")
        assert resp.status_code == 200

    def test_select_role_service_down(self, client, student_token):
        client.cookies["ef_token"] = student_token
        import httpx

        with patch(
            "apps.auth_views.views.httpx.get",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.get("/select-role/")
        assert resp.status_code == 200

    def test_select_role_confirm_redirects(self, client):
        resp = client.get(
            "/select-role/confirm/",
            data={"role_id": "1", "institution_id": "10"},
        )
        assert resp.status_code == 302
        assert "/home/" in resp["Location"]


# ── Profile setup ───────────────────────────────────────────────────────────


class TestProfileSetup:
    def test_setup_profile_renders(self, client, student_token):
        with _authed(client, student_token):
            resp = client.get("/setup-profile/")
        assert resp.status_code == 200

    def test_profile_save(self, client, student_token):
        with _authed(client, student_token):
            with patch("apps.auth_views.views.httpx.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=200)
                resp = client.post(
                    "/profile/save/",
                    data={"full_name": "Test User", "language": "en"},
                )
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/home/"

    def test_profile_save_service_down(self, client, student_token):
        import httpx as _httpx

        def _get_ok(url, **kw):
            return _ME_MOCK

        with patch("httpx.get", side_effect=_get_ok), patch(
            "httpx.post", side_effect=_httpx.ConnectError("down")
        ):
            client.cookies["ef_token"] = student_token
            resp = client.post(
                "/profile/save/",
                data={"full_name": "Test"},
            )
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/home/"


# ── 2FA ─────────────────────────────────────────────────────────────────────


class TestTwoFA:
    def test_2fa_page_renders(self, client, student_token):
        with _authed(client, student_token):
            resp = client.get("/2fa/")
        assert resp.status_code == 200

    def test_2fa_verify_success(self, client, student_token):
        with _authed(client, student_token):
            with patch("apps.auth_views.views.httpx.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=200)
                resp = client.post("/2fa/verify/", data={"totp": "123456"})
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/home/"

    def test_2fa_verify_wrong_code(self, client, student_token):
        with _authed(client, student_token):
            with patch("apps.auth_views.views.httpx.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=401)
                resp = client.post("/2fa/verify/", data={"totp": "000000"})
        assert resp.status_code == 401
        assert b"Invalid code" in resp.content

    def test_2fa_verify_service_down(self, client, student_token):
        import httpx as _httpx

        def _get_ok(url, **kw):
            return _ME_MOCK

        with patch("httpx.get", side_effect=_get_ok), patch(
            "httpx.post", side_effect=_httpx.ConnectError("down")
        ):
            client.cookies["ef_token"] = student_token
            resp = client.post("/2fa/verify/", data={"totp": "123456"})
        assert resp.status_code == 503


# ── Account blocked ─────────────────────────────────────────────────────────


class TestAccountBlocked:
    def test_account_blocked_renders(self, client):
        resp = client.get("/account-blocked/")
        assert resp.status_code == 200

    def test_account_blocked_with_params(self, client):
        resp = client.get("/account-blocked/?reason=suspicious&ref=REF123")
        assert resp.status_code == 200


# ── Register ────────────────────────────────────────────────────────────────


class TestRegister:
    def test_register_page_renders(self, client):
        resp = client.get("/register/")
        assert resp.status_code == 200

    def test_register_invalid_mobile(self, client):
        resp = client.post("/register/submit/", data={"mobile": "123"})
        assert b"valid 10-digit" in resp.content

    def test_register_success(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=201)
            resp = client.post(
                "/register/submit/",
                data={
                    "full_name": "Test",
                    "mobile": "9876543210",
                    "dob": "2000-01-01",
                    "state": "AP",
                    "target_exam": "SSC",
                },
            )
        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/otp/verify/"

    def test_register_duplicate(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=409,
                json=lambda: {"detail": "Mobile already registered."},
            )
            resp = client.post(
                "/register/submit/",
                data={"full_name": "X", "mobile": "9876543210"},
            )
        assert resp.status_code == 400

    def test_register_service_down(self, client):
        import httpx

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(
                "/register/submit/",
                data={"full_name": "X", "mobile": "9876543210"},
            )
        assert resp.status_code == 503


# ── Logout ──────────────────────────────────────────────────────────────────


class TestLogout:
    def test_logout_clears_cookies(self, client, student_token):
        with _authed(client, student_token):
            with patch("apps.auth_views.views.httpx.post") as mock_post:
                mock_post.return_value = MagicMock(status_code=200)
                resp = client.get("/logout/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_logout_without_token(self, client):
        # No token → middleware redirects to login (same end result)
        resp = client.get("/logout/")
        assert resp.status_code == 302
        assert "/login/" in resp["Location"]

    def test_logout_service_down(self, client, student_token):
        import httpx as _httpx

        def _get_ok(url, **kw):
            return _ME_MOCK

        with patch("httpx.get", side_effect=_get_ok), patch(
            "httpx.post", side_effect=_httpx.ConnectError("down")
        ):
            client.cookies["ef_token"] = student_token
            resp = client.get("/logout/")
        assert resp.status_code == 302


# ── Session reauth ──────────────────────────────────────────────────────────


class TestSessionReauth:
    def test_reauth_get_renders(self, client, student_token):
        with _authed(client, student_token):
            resp = client.get("/session/reauth/")
        assert resp.status_code == 200

    def test_reauth_post_delegates_to_password_login(self, client, student_token):
        with _authed(client, student_token):
            resp = client.post(
                "/session/reauth/", data={"login_id": "", "password": ""}
            )
        assert b"Please enter" in resp.content


# ── Forgot password ─────────────────────────────────────────────────────────


class TestForgotPassword:
    def test_forgot_password_page_renders(self, client):
        resp = client.get("/forgot-password/")
        assert resp.status_code == 200

    def test_forgot_password_invalid_email(self, client):
        resp = client.post("/forgot-password/request/", data={"email": "bad"})
        assert b"valid email" in resp.content

    def test_forgot_password_sends_otp(self, client):
        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            resp = client.post(
                "/forgot-password/request/",
                data={"email": "user@test.com"},
            )
        assert resp.status_code == 200

    def test_forgot_password_service_down(self, client):
        import httpx

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(
                "/forgot-password/request/",
                data={"email": "user@test.com"},
            )
        # Still renders OTP page to prevent email enumeration
        assert resp.status_code == 200

    def test_verify_reset_otp_success(self, client):
        url = reverse("forgot_password_verify")
        session = client.session
        session["reset_email"] = "user@test.com"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"reset_token": "rst-tok"},
            )
            resp = client.post(url, data={"otp": "123456"})

        assert resp.status_code == 204
        assert resp["HX-Redirect"] == "/reset-password/"

    def test_verify_reset_otp_wrong(self, client):
        url = reverse("forgot_password_verify")
        session = client.session
        session["reset_email"] = "user@test.com"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=401)
            resp = client.post(url, data={"otp": "000000"})

        assert resp.status_code == 401

    def test_verify_reset_otp_missing_email(self, client):
        url = reverse("forgot_password_verify")
        resp = client.post(url, data={"otp": "123456"})
        assert resp.status_code == 400

    def test_verify_reset_otp_service_down(self, client):
        import httpx

        url = reverse("forgot_password_verify")
        session = client.session
        session["reset_email"] = "user@test.com"
        session.save()

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(url, data={"otp": "123456"})

        assert resp.status_code == 503


# ── Reset password ──────────────────────────────────────────────────────────


class TestResetPassword:
    def test_reset_password_no_token_redirects(self, client):
        resp = client.get("/reset-password/")
        assert resp.status_code == 302
        assert "/forgot-password/" in resp["Location"]

    def test_reset_password_renders_form(self, client):
        session = client.session
        session["reset_token"] = "rst-tok"
        session.save()
        resp = client.get("/reset-password/")
        assert resp.status_code == 200

    def test_reset_password_mismatch(self, client):
        session = client.session
        session["reset_token"] = "rst-tok"
        session.save()
        resp = client.post(
            "/reset-password/",
            data={"password": "newpass123", "confirm_password": "different"},
        )
        assert b"must match" in resp.content.lower()

    def test_reset_password_too_short(self, client):
        session = client.session
        session["reset_token"] = "rst-tok"
        session.save()
        resp = client.post(
            "/reset-password/",
            data={"password": "short", "confirm_password": "short"},
        )
        assert b"8 characters" in resp.content

    def test_reset_password_success(self, client):
        session = client.session
        session["reset_token"] = "rst-tok"
        session["reset_email"] = "user@test.com"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            resp = client.post(
                "/reset-password/",
                data={
                    "password": "newpass123",
                    "confirm_password": "newpass123",
                },
            )

        assert resp.status_code == 204
        assert "reset=success" in resp["HX-Redirect"]

    def test_reset_password_api_failure(self, client):
        session = client.session
        session["reset_token"] = "rst-tok"
        session.save()

        with patch("apps.auth_views.views.httpx.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=400)
            resp = client.post(
                "/reset-password/",
                data={
                    "password": "newpass123",
                    "confirm_password": "newpass123",
                },
            )

        assert b"Reset failed" in resp.content

    def test_reset_password_service_down(self, client):
        import httpx

        session = client.session
        session["reset_token"] = "rst-tok"
        session.save()

        with patch(
            "apps.auth_views.views.httpx.post",
            side_effect=httpx.ConnectError("down"),
        ):
            resp = client.post(
                "/reset-password/",
                data={
                    "password": "newpass123",
                    "confirm_password": "newpass123",
                },
            )

        assert resp.status_code == 503
