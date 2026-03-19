"""
E2E tests — Login journey.
Playwright browser tests against a running Django portal (localhost:8000).
Run: pytest tests/e2e/ --headed (or headless by default)
"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.e2e


class TestLoginPage:
    def test_login_page_loads(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        expect(page).to_have_title(re.compile(r"Sign In", re.IGNORECASE))
        expect(page.locator("#login_id")).to_be_visible()
        expect(page.locator("#password")).to_be_visible()
        expect(page.locator("#login-btn")).to_be_visible()

    def test_login_page_has_forgot_password_link(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        link = page.locator("a[href='/forgot-password/']")
        expect(link).to_be_visible()

    def test_password_toggle_shows_hides_text(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        pwd = page.locator("#password")
        toggle = page.locator("button[onclick='togglePwd()']")
        expect(pwd).to_have_attribute("type", "password")
        toggle.click()
        expect(pwd).to_have_attribute("type", "text")
        toggle.click()
        expect(pwd).to_have_attribute("type", "password")

    def test_empty_form_does_not_submit(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        page.click("#login-btn")
        # Should stay on login page (HTML5 validation)
        expect(page).to_have_url(f"{base_url}/login/")

    def test_wrong_credentials_shows_error(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        page.fill("#login_id", "0000000000")
        page.fill("#password", "wrongpassword")
        page.click("#login-btn")
        error = page.locator("#form-response")
        expect(error).to_contain_text("Incorrect", timeout=5000)

    def test_successful_login_redirects_to_home(self, page: Page, base_url: str):
        page.goto(f"{base_url}/login/")
        page.fill("#login_id", "9876543210")
        page.fill("#password", "Test@1234")
        page.click("#login-btn")
        page.wait_for_url(f"{base_url}/home/**", timeout=8000)
        expect(page).to_have_url(f"{base_url}/home/")

    def test_already_logged_in_redirects_to_home(self, page: Page, base_url: str):
        """If ef_token cookie exists, /login/ should redirect to /home/."""
        page.goto(f"{base_url}/login/")
        page.fill("#login_id", "9876543210")
        page.fill("#password", "Test@1234")
        page.click("#login-btn")
        page.wait_for_url(f"{base_url}/home/**", timeout=8000)
        # Now revisit login
        page.goto(f"{base_url}/login/")
        expect(page).to_have_url(f"{base_url}/home/")

    def test_brand_panel_visible_on_desktop(self, page: Page, base_url: str):
        page.set_viewport_size({"width": 1280, "height": 800})
        page.goto(f"{base_url}/login/")
        # Brand panel is shown on lg+ screens
        panel = page.locator(".lg\\:flex").first
        expect(panel).to_be_visible()

    def test_brand_panel_hidden_on_mobile(self, page: Page, base_url: str):
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(f"{base_url}/login/")
        # Mobile logo shown instead
        mobile_logo = page.locator(".lg\\:hidden").first
        expect(mobile_logo).to_be_visible()


import re


class TestForgotPasswordJourney:
    def test_forgot_password_page_loads(self, page: Page, base_url: str):
        page.goto(f"{base_url}/forgot-password/")
        expect(page.locator("input[name='email']")).to_be_visible()

    def test_invalid_email_shows_error(self, page: Page, base_url: str):
        page.goto(f"{base_url}/forgot-password/")
        page.fill("input[name='email']", "notanemail")
        page.click("button[type='submit']")
        # HTML5 email validation prevents submission
        expect(page).to_have_url(f"{base_url}/forgot-password/")

    def test_valid_email_shows_otp_form(self, page: Page, base_url: str):
        page.goto(f"{base_url}/forgot-password/")
        page.fill("input[name='email']", "aspirant@example.com")
        page.click("button[type='submit']")
        # OTP boxes should appear (HTMX swap)
        otp_boxes = page.locator(".otp-box")
        expect(otp_boxes.first).to_be_visible(timeout=5000)

    def test_back_to_login_link_works(self, page: Page, base_url: str):
        page.goto(f"{base_url}/forgot-password/")
        page.click("a[href='/login/']")
        expect(page).to_have_url(f"{base_url}/login/")
