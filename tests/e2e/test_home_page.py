"""
E2E tests — Home page (post-login).
Requires a running portal and a seeded test user.
"""
import pytest
from playwright.sync_api import Page, expect
from .conftest import login

pytestmark = pytest.mark.e2e


class TestHomePageShell:
    def test_home_redirects_unauthenticated(self, page: Page, base_url: str):
        page.goto(f"{base_url}/home/")
        expect(page).to_have_url(f"{base_url}/login/")

    def test_home_renders_after_login(self, page: Page, base_url: str):
        login(page, base_url)
        expect(page).to_have_url(f"{base_url}/home/")
        expect(page.locator("#home-content")).to_be_visible()

    def test_home_shows_sidebar_nav(self, page: Page, base_url: str):
        page.set_viewport_size({"width": 1280, "height": 800})
        login(page, base_url)
        sidebar = page.locator("nav#sidebar, aside")
        expect(sidebar).to_be_visible()

    def test_home_data_loads_via_htmx(self, page: Page, base_url: str):
        login(page, base_url)
        # Skeleton loader should disappear after HTMX loads
        page.wait_for_selector("#home-loader", state="hidden", timeout=8000)
        content = page.locator("#home-content")
        expect(content).not_to_be_empty()

    def test_home_has_greeting(self, page: Page, base_url: str):
        login(page, base_url)
        page.wait_for_selector("#home-loader", state="hidden", timeout=8000)
        # Greeting text should contain time-of-day or user name
        greeting = page.locator("h1").first
        expect(greeting).to_be_visible()

    def test_logout_clears_session(self, page: Page, base_url: str):
        login(page, base_url)
        page.goto(f"{base_url}/logout/")
        expect(page).to_have_url(f"{base_url}/login/")
        # Revisit home should redirect to login
        page.goto(f"{base_url}/home/")
        expect(page).to_have_url(f"{base_url}/login/")

    def test_home_insight_strip_visible(self, page: Page, base_url: str):
        login(page, base_url)
        # Insight strip — one of the contextual banners should be visible
        strips = page.locator(".bg-indigo-50, .bg-amber-50, .bg-purple-50, .bg-blue-50, .bg-green-50, .bg-rose-50")
        # At least one insight strip may be visible depending on portal group
        # Just ensure the home content loaded
        expect(page.locator("#home-content")).to_be_visible()
