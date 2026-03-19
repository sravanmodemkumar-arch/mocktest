"""
Performance tests — Locust load scenarios.
Run: locust -f tests/performance/locustfile.py --host=http://localhost:8000

Scenarios:
  - AnonymousUser: browses login page (CDN-cacheable)
  - AuthenticatedStudent: logs in, loads home, navigates
  - AuthenticatedTeacher: marks attendance, loads timetable
  - PlatformAdminUser: loads admin dashboard with high KPI count
"""
from locust import HttpUser, task, between, tag
import random
import json


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def get_csrf(client, path="/login/"):
    """Fetch CSRF token from a GET request."""
    resp = client.get(path)
    for cookie in client.cookiejar:
        if cookie.name == "csrftoken":
            return cookie.value
    return ""


# ---------------------------------------------------------------------------
# Anonymous user — simulates CDN cache misses on auth pages
# ---------------------------------------------------------------------------

class AnonymousUser(HttpUser):
    """
    Represents unauthenticated traffic hitting auth pages.
    These should be served fast — ideally from CDN edge.
    Target: p95 < 200ms, error rate < 0.1%
    """
    wait_time = between(1, 3)
    weight = 60  # 60% of traffic is anonymous

    @task(5)
    @tag("auth", "anonymous")
    def view_login_page(self):
        with self.client.get(
            "/login/",
            headers={"Host": "ssc.eduforge.in"},
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login page returned {resp.status_code}")
            elif b"Sign in" not in resp.content and b"login" not in resp.content.lower():
                resp.failure("Login page missing expected content")

    @task(2)
    @tag("auth", "anonymous")
    def view_forgot_password(self):
        self.client.get("/forgot-password/")

    @task(1)
    @tag("auth", "anonymous")
    def view_register_page(self):
        with self.client.get(
            "/register/",
            headers={"Host": "ssc.eduforge.in"},
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Register page returned {resp.status_code}")


# ---------------------------------------------------------------------------
# Authenticated student — most common active user type
# ---------------------------------------------------------------------------

class AuthenticatedStudent(HttpUser):
    """
    Simulates a logged-in student on an exam domain portal.
    Target: home data p95 < 500ms, error rate < 0.5%
    """
    wait_time = between(2, 8)
    weight = 30  # 30% of traffic

    def on_start(self):
        """Simulate login by setting auth cookie directly."""
        # In real perf test, obtain token via login endpoint
        self.client.cookies.set("ef_token", "perf.test.student.token")

    @task(10)
    @tag("home", "student")
    def load_home_shell(self):
        with self.client.get("/home/", catch_response=True) as resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Home shell: {resp.status_code}")

    @task(8)
    @tag("home", "student")
    def load_home_data(self):
        with self.client.get(
            "/home/data/",
            headers={"HX-Request": "true"},
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Home data: {resp.status_code}")

    @task(5)
    @tag("nav", "student")
    def load_nav_links(self):
        self.client.get(
            "/home/nav/",
            headers={"HX-Request": "true"},
        )

    @task(2)
    @tag("auth", "student")
    def logout_and_login(self):
        self.client.get("/logout/")
        self.client.cookies.set("ef_token", "perf.test.student.token")


# ---------------------------------------------------------------------------
# Authenticated teacher — medium frequency, attendance-heavy
# ---------------------------------------------------------------------------

class AuthenticatedTeacher(HttpUser):
    """
    Simulates a teacher managing attendance and marks.
    Target: home p95 < 600ms
    """
    wait_time = between(3, 10)
    weight = 8

    def on_start(self):
        self.client.cookies.set("ef_token", "perf.test.teacher.token")

    @task(5)
    @tag("home", "teacher")
    def load_home(self):
        self.client.get("/home/data/", headers={"HX-Request": "true"})

    @task(3)
    @tag("nav", "teacher")
    def load_nav(self):
        self.client.get("/home/nav/", headers={"HX-Request": "true"})


# ---------------------------------------------------------------------------
# Platform admin — low volume, high data complexity
# ---------------------------------------------------------------------------

class PlatformAdminUser(HttpUser):
    """
    Simulates platform admin monitoring institution health.
    Low traffic, complex data — target p95 < 1000ms.
    """
    wait_time = between(5, 20)
    weight = 2

    def on_start(self):
        self.client.cookies.set("ef_token", "perf.test.admin.token")

    @task(3)
    @tag("home", "admin")
    def load_admin_home(self):
        with self.client.get(
            "/home/data/",
            headers={"HX-Request": "true", "Host": "admin.eduforge.in"},
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 302):
                resp.failure(f"Admin home: {resp.status_code}")

    @task(1)
    @tag("health")
    def check_health(self):
        self.client.get("/health/")
