"""
Unit tests — JWT token creation and decoding.
No DB, no network.
"""
import pytest
import time

pytestmark = pytest.mark.unit


class TestAccessToken:
    def test_create_access_token_structure(self):
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(user_id=1, role="student", institution_id=None)
        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # header.payload.signature

    def test_access_token_claims(self):
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(user_id=42, role="principal", institution_id=7)
        data = decode_token(token)
        assert data["sub"] == "42"
        assert data["role"] == "principal"
        assert data["institution_id"] == 7
        assert data["type"] == "access"

    def test_access_token_expires(self):
        from app.services.jwt import create_access_token, decode_token
        from app.config import settings
        token = create_access_token(user_id=1, role="student", institution_id=None)
        data = decode_token(token)
        assert "exp" in data
        # exp should be in the future (within 31 min from now)
        assert data["exp"] > time.time()
        assert data["exp"] < time.time() + (settings.JWT_ACCESS_EXPIRE_MINUTES + 1) * 60

    def test_decode_invalid_token_returns_none(self):
        from app.services.jwt import decode_token
        assert decode_token("not.a.token") is None
        assert decode_token("") is None
        assert decode_token(None) is None

    def test_decode_tampered_token_returns_none(self):
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(user_id=1, role="student", institution_id=None)
        # Tamper with payload part
        parts = token.split(".")
        tampered = f"{parts[0]}.TAMPERED{parts[1]}.{parts[2]}"
        assert decode_token(tampered) is None

    def test_access_token_wrong_secret_returns_none(self):
        """Token signed with wrong key should not decode."""
        from jose import jwt as jose_jwt
        import datetime
        payload = {
            "sub": "1",
            "role": "admin",
            "type": "access",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        }
        bad_token = jose_jwt.encode(payload, "wrong-secret", algorithm="HS256")
        from app.services.jwt import decode_token
        assert decode_token(bad_token) is None


class TestRefreshToken:
    def test_refresh_token_type(self):
        from app.services.jwt import create_refresh_token, decode_token
        token = create_refresh_token(user_id=1)
        data = decode_token(token)
        assert data["type"] == "refresh"
        assert data["sub"] == "1"

    def test_refresh_token_longer_expiry(self):
        from app.services.jwt import create_access_token, create_refresh_token, decode_token
        access = decode_token(create_access_token(1, "student", None))
        refresh = decode_token(create_refresh_token(1))
        # Refresh must expire later than access
        assert refresh["exp"] > access["exp"]

    def test_access_token_is_not_refresh(self):
        """Access token must not be accepted as refresh token."""
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(1, "student", None)
        data = decode_token(token)
        assert data["type"] != "refresh"


class TestTokenEdgeCases:
    def test_institution_id_none_is_preserved(self):
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(1, "student", None)
        data = decode_token(token)
        assert data.get("institution_id") is None

    def test_large_user_id(self):
        from app.services.jwt import create_access_token, decode_token
        token = create_access_token(999_999_999, "admin", None)
        data = decode_token(token)
        assert data["sub"] == "999999999"

    def test_special_roles(self):
        from app.services.jwt import create_access_token, decode_token
        for role in ["platform_admin", "principal", "teacher", "student", "parent", "tsp_owner"]:
            token = create_access_token(1, role, None)
            assert decode_token(token)["role"] == role
