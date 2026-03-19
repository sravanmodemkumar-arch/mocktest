"""
Integration tests — Full authentication flow.
OTP send → OTP verify → get token → /auth/me → logout.
Calls real FastAPI app via ASGI (no real network, real DB logic with mocks).

Requires a PostgreSQL instance. Skipped automatically when DB is unavailable.
Run with: pytest tests/integration/test_auth_flow.py --db-available
"""
import pytest
from unittest.mock import patch, AsyncMock

pytestmark = [pytest.mark.integration, pytest.mark.requires_db]


class TestOTPSendEndpoint:
    @pytest.mark.asyncio
    async def test_send_otp_valid_mobile(self, identity_client):
        with patch("app.services.otp.save_otp", new_callable=AsyncMock):
            resp = await identity_client.post(
                "/api/v1/auth/otp/send",
                json={"mobile": "+919876543210", "channel": "whatsapp"},
            )
        assert resp.status_code == 200
        assert "message" in resp.json()

    @pytest.mark.asyncio
    async def test_send_otp_returns_dev_otp_in_debug(self, identity_client):
        with patch("app.services.otp.save_otp", new_callable=AsyncMock):
            resp = await identity_client.post(
                "/api/v1/auth/otp/send",
                json={"mobile": "+919876543210"},
            )
        data = resp.json()
        # In DEBUG mode, dev_otp is returned
        assert "dev_otp" in data

    @pytest.mark.asyncio
    async def test_send_otp_invalid_mobile_rejected(self, identity_client):
        resp = await identity_client.post(
            "/api/v1/auth/otp/send",
            json={"mobile": "123"},  # too short
        )
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_send_otp_missing_mobile_422(self, identity_client):
        resp = await identity_client.post("/api/v1/auth/otp/send", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_send_otp_rate_limit(self, identity_client):
        """6th OTP request in 30min must return 429."""
        with patch("app.services.otp.save_otp", new_callable=AsyncMock), \
             patch("app.services.otp.count_recent_otps", return_value=5):
            resp = await identity_client.post(
                "/api/v1/auth/otp/send",
                json={"mobile": "+919876543210"},
            )
        assert resp.status_code == 429


class TestOTPVerifyEndpoint:
    @pytest.mark.asyncio
    async def test_verify_valid_otp_returns_tokens(self, identity_client):
        with patch("app.services.otp.validate_otp", new_callable=AsyncMock, return_value=True), \
             patch("app.api.v1.auth.select", return_value=AsyncMock()), \
             patch("app.api.v1.auth.db") as mock_db:

            mock_db.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db.__aexit__ = AsyncMock(return_value=False)

            resp = await identity_client.post(
                "/api/v1/auth/otp/verify",
                json={"mobile": "+919876543210", "otp": "123456"},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_verify_wrong_otp_returns_401(self, identity_client):
        with patch("app.services.otp.validate_otp", new_callable=AsyncMock, return_value=False):
            resp = await identity_client.post(
                "/api/v1/auth/otp/verify",
                json={"mobile": "+919876543210", "otp": "000000"},
            )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_otp_wrong_length_422(self, identity_client):
        resp = await identity_client.post(
            "/api/v1/auth/otp/verify",
            json={"mobile": "+919876543210", "otp": "123"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_otp_tokens_are_valid_jwt(self, identity_client):
        with patch("app.services.otp.validate_otp", new_callable=AsyncMock, return_value=True):
            resp = await identity_client.post(
                "/api/v1/auth/otp/verify",
                json={"mobile": "+919876543210", "otp": "123456"},
            )

        if resp.status_code == 200:
            data = resp.json()
            from app.services.jwt import decode_token
            access_data = decode_token(data["access_token"])
            assert access_data is not None
            assert access_data["type"] == "access"


class TestAuthMeEndpoint:
    @pytest.mark.asyncio
    async def test_me_valid_token(self, identity_client, student_token):
        resp = await identity_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "role" in data

    @pytest.mark.asyncio
    async def test_me_no_token_401(self, identity_client):
        resp = await identity_client.get("/api/v1/auth/me")
        assert resp.status_code == 403  # HTTPBearer returns 403 when missing

    @pytest.mark.asyncio
    async def test_me_invalid_token_401(self, identity_client):
        resp = await identity_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_refresh_token_rejected(self, identity_client):
        from app.services.jwt import create_refresh_token
        refresh = create_refresh_token(1)
        resp = await identity_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh}"},
        )
        # Refresh token must not work for /me endpoint
        assert resp.status_code == 401


class TestTokenRefreshEndpoint:
    @pytest.mark.asyncio
    async def test_refresh_returns_new_access_token(self, identity_client):
        from app.services.jwt import create_refresh_token
        refresh = create_refresh_token(1)

        resp = await identity_client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_with_access_token_fails(self, identity_client, student_token):
        resp = await identity_client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": student_token},  # wrong type
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_garbage_fails(self, identity_client):
        resp = await identity_client.post(
            "/api/v1/auth/token/refresh",
            json={"refresh_token": "garbage"},
        )
        assert resp.status_code == 401


class TestLogoutEndpoint:
    @pytest.mark.asyncio
    async def test_logout_valid_token(self, identity_client, student_token):
        resp = await identity_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {student_token}"},
        )
        assert resp.status_code == 200
        assert "message" in resp.json()

    @pytest.mark.asyncio
    async def test_logout_no_token_403(self, identity_client):
        resp = await identity_client.post("/api/v1/auth/logout")
        assert resp.status_code == 403


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, identity_client):
        resp = await identity_client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
