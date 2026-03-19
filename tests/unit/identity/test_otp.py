"""
Unit tests — OTP generation, hashing, validation.
No DB, no network. Pure function tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, timezone


pytestmark = pytest.mark.unit


class TestOTPGeneration:
    def test_otp_is_6_digits(self):
        from app.services.otp import generate_otp
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_otp_is_random(self):
        from app.services.otp import generate_otp
        otps = {generate_otp() for _ in range(50)}
        # In 50 draws, highly unlikely to get all same
        assert len(otps) > 1

    def test_otp_range(self):
        from app.services.otp import generate_otp
        for _ in range(100):
            otp = generate_otp()
            assert 0 <= int(otp) <= 999999


class TestOTPHashing:
    def test_otp_hash_not_plain_text(self):
        from app.services.otp import hash_otp
        otp = "123456"
        hashed = hash_otp(otp)
        assert hashed != otp
        assert len(hashed) > 20  # bcrypt hash is 60 chars

    def test_otp_hash_verify_correct(self):
        from app.services.otp import hash_otp, verify_otp_hash
        otp = "456789"
        hashed = hash_otp(otp)
        assert verify_otp_hash(otp, hashed) is True

    def test_otp_hash_verify_wrong(self):
        from app.services.otp import hash_otp, verify_otp_hash
        hashed = hash_otp("111111")
        assert verify_otp_hash("222222", hashed) is False

    def test_different_otps_different_hashes(self):
        from app.services.otp import hash_otp
        h1 = hash_otp("123456")
        h2 = hash_otp("123456")
        # bcrypt uses random salt — same input, different hash
        assert h1 != h2

    def test_empty_otp_raises(self):
        from app.services.otp import hash_otp
        with pytest.raises(Exception):
            hash_otp("")


class TestOTPExpiry:
    @pytest.mark.asyncio
    async def test_validate_otp_expired(self):
        """Expired OTP (past expires_at) must return False."""
        from app.services.otp import validate_otp

        mock_db = AsyncMock()
        mock_otp_record = MagicMock()
        mock_otp_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        mock_otp_record.used = False
        mock_otp_record.otp_hash = "somehash"

        with patch("app.services.otp.get_latest_otp", return_value=mock_otp_record):
            result = await validate_otp(mock_db, "+919876543210", "123456")

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_otp_already_used(self):
        """Already-used OTP must return False."""
        from app.services.otp import validate_otp

        mock_db = AsyncMock()
        mock_otp_record = MagicMock()
        mock_otp_record.expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)
        mock_otp_record.used = True

        with patch("app.services.otp.get_latest_otp", return_value=mock_otp_record):
            result = await validate_otp(mock_db, "+919876543210", "123456")

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_otp_not_found(self):
        """No OTP record in DB must return False."""
        from app.services.otp import validate_otp

        mock_db = AsyncMock()
        with patch("app.services.otp.get_latest_otp", return_value=None):
            result = await validate_otp(mock_db, "+919876543210", "123456")

        assert result is False

    @pytest.mark.asyncio
    async def test_validate_otp_valid(self):
        """Valid, non-expired, non-used OTP returns True."""
        from app.services.otp import validate_otp, hash_otp

        plain_otp = "654321"
        mock_db = AsyncMock()
        mock_otp_record = MagicMock()
        mock_otp_record.expires_at = datetime.now(timezone.utc) + timedelta(minutes=3)
        mock_otp_record.used = False
        mock_otp_record.otp_hash = hash_otp(plain_otp)

        with patch("app.services.otp.get_latest_otp", return_value=mock_otp_record):
            result = await validate_otp(mock_db, "+919876543210", plain_otp)

        assert result is True


class TestOTPRateLimiting:
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """More than 5 OTPs in 30 min should raise HTTPException 429."""
        from app.services.otp import check_rate_limit
        from fastapi import HTTPException

        mock_db = AsyncMock()
        with patch("app.services.otp.count_recent_otps", return_value=5):
            with pytest.raises(HTTPException) as exc_info:
                await check_rate_limit(mock_db, "+919876543210")
            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_rate_limit_not_exceeded(self):
        """Under the limit should not raise."""
        from app.services.otp import check_rate_limit

        mock_db = AsyncMock()
        with patch("app.services.otp.count_recent_otps", return_value=2):
            # Should not raise
            await check_rate_limit(mock_db, "+919876543210")
