"""
Shared fixtures for the entire test suite.
Loaded automatically by pytest from this file.

Fixture scopes used:
  session  → created once per pytest run   (DB engine, browser)
  module   → created once per test file    (test app clients)
  function → created per test (default)    (clean state per test)
"""
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient, ASGITransport

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "identity"))
sys.path.insert(0, os.path.join(ROOT, "portal"))
sys.path.insert(0, os.path.join(ROOT, "services"))

# ── Test environment ──────────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portal.settings")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/eduforge_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("DEBUG", "True")

fake = Faker("en_IN")


# ── Event loop ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the entire session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Identity service (FastAPI) ────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="module")
async def identity_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for the identity FastAPI service."""
    from app.main import app  # identity/app/main.py
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def home_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for the home FastAPI service."""
    from home.main import app as home_app  # services/home/main.py
    async with AsyncClient(
        transport=ASGITransport(app=home_app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def tenant_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for the tenant FastAPI service."""
    from tenant.main import app as tenant_app  # services/tenant/main.py
    async with AsyncClient(
        transport=ASGITransport(app=tenant_app),
        base_url="http://test",
    ) as client:
        yield client


# ── Database ──────────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Create test DB tables once per session, drop after."""
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.database import Base

    engine = create_async_engine(
        os.environ["DATABASE_URL"], echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Fresh DB session per test, rolled back after."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    Session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with Session() as session:
        async with session.begin():
            yield session
            await session.rollback()


# ── Test data factories ───────────────────────────────────────────────────────
@pytest.fixture
def indian_mobile() -> str:
    """Valid Indian mobile number (10 digits, starts 6-9)."""
    prefix = fake.random_element(["6", "7", "8", "9"])
    rest = "".join([str(fake.random_digit()) for _ in range(9)])
    return f"{prefix}{rest}"


@pytest.fixture
def valid_otp() -> str:
    return "123456"


@pytest.fixture
def expired_otp() -> str:
    return "000000"


@pytest.fixture
def test_institution():
    return {
        "name": "XYZ Test School",
        "domain": "xyz-test.school.com",
        "institution_type": "school",
        "portal_group": 3,
    }


@pytest.fixture
def test_tenant():
    return {
        "slug": "xyz-test-school",
        "portal_group": 3,
        "name": "XYZ Test School",
        "branding": {
            "primary": "#1565C0",
            "logo": "https://cdn.eduforge.in/static/tenants/xyz-test-school/logo.svg",
        },
        "features": {},
        "auth_methods": ["whatsapp_otp", "sms_otp"],
        "domain_type": "custom",
    }


# ── JWT helpers ───────────────────────────────────────────────────────────────
@pytest.fixture
def make_access_token():
    """Factory: create a real JWT access token for a given user_id + role."""
    def _make(user_id: int = 1, role: str = "student", institution_id: int = None):
        from app.services.jwt import create_access_token
        return create_access_token(user_id, role, institution_id)
    return _make


@pytest.fixture
def student_token(make_access_token) -> str:
    return make_access_token(user_id=1, role="student")


@pytest.fixture
def principal_token(make_access_token) -> str:
    return make_access_token(user_id=2, role="principal", institution_id=10)


@pytest.fixture
def admin_token(make_access_token) -> str:
    return make_access_token(user_id=99, role="platform_admin")


# ── Django test client ────────────────────────────────────────────────────────
@pytest.fixture
def portal_client(client):
    """Django test client (pytest-django provides `client` fixture)."""
    return client


@pytest.fixture
def authed_portal_client(client, student_token):
    """Django test client pre-authenticated with student JWT cookie."""
    client.cookies["ef_token"] = student_token
    return client


# ── Playwright fixtures ───────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def browser_context_args():
    """Base browser context — viewport + locale."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-IN",
        "timezone_id": "Asia/Kolkata",
    }


@pytest.fixture
def portal_base_url() -> str:
    return os.environ.get("PORTAL_BASE_URL", "http://localhost:8080")


@pytest.fixture
def identity_base_url() -> str:
    return os.environ.get("IDENTITY_BASE_URL", "http://localhost:8001")


# ── Mock HTMX headers (for Django view tests) ─────────────────────────────────
@pytest.fixture
def htmx_headers() -> dict:
    """Headers that HTMX sends with every request."""
    return {
        "HX-Request": "true",
        "HX-Current-URL": "http://localhost:8080/home/",
    }


# ── Respx mock for httpx calls ────────────────────────────────────────────────
@pytest.fixture
def mock_identity_service(respx_mock):
    """Pre-configured respx mock for identity service calls."""
    respx_mock.get("http://localhost:8001/api/v1/auth/me").mock(
        return_value=respx_mock.build_response(200, json={
            "id": 1,
            "mobile": "+919876543210",
            "role": "student",
            "institution_id": None,
            "is_active": True,
        })
    )
    return respx_mock


@pytest.fixture
def mock_tenant_service(respx_mock):
    """Pre-configured respx mock for tenant service calls."""
    respx_mock.get("http://localhost:8003/api/v1/tenant/config").mock(
        return_value=respx_mock.build_response(200, json={
            "slug": "test-school",
            "portal_group": 3,
            "name": "Test School",
            "branding": {"primary": "#1565C0"},
            "features": {},
            "auth_methods": ["whatsapp_otp"],
            "domain_type": "custom",
        })
    )
    return respx_mock
