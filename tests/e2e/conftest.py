"""E2E test configuration — Playwright browser fixtures."""

import pytest
from playwright.sync_api import Page, BrowserContext


@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"


@pytest.fixture
def auth_page(page: Page, base_url: str) -> Page:
    """Page pre-navigated to login."""
    page.goto(f"{base_url}/login/")
    return page


def login(
    page: Page, base_url: str, login_id: str = "9876543210", password: str = "Test@1234"
):
    """Helper: fill login form and submit."""
    page.goto(f"{base_url}/login/")
    page.fill("#login_id", login_id)
    page.fill("#password", password)
    page.click("#login-btn")
    page.wait_for_url(f"{base_url}/home/**", timeout=8000)
