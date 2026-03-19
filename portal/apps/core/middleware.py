"""Core middleware — tenant resolution + JWT auth check."""
import httpx
from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

# Routes that don't require authentication
PUBLIC_PATHS = {
    "/login/", "/otp/verify/", "/register/", "/account-blocked/",
    "/static/", "/favicon.ico", "/health/",
}

# Roles that require 2FA after OTP
TWO_FA_ROLES = {
    # Group 1 — Platform
    "platform_admin", "platform_owner", "platform_ops",
    # Group 2 — Chain
    "chain_owner", "chain_ceo", "chain_cto",
    # Group 3 — School
    "principal", "school_admin", "school_owner",
    # Group 4 — College
    "college_principal", "college_admin",
    # Group 5 — Coaching
    "coaching_director", "center_head",
    # Group 7 — TSP
    "tsp_owner", "tsp_admin",
}


class TenantMiddleware(MiddlewareMixin):
    """Resolve Host header → tenant config. Attach to request."""

    def process_request(self, request):
        host = request.get_host().split(":")[0].lower()
        cache_key = f"tenant:{host}"

        # Check session cache first (avoid API call every request)
        tenant = request.session.get(cache_key)
        if not tenant:
            try:
                resp = httpx.get(
                    f"{settings.TENANT_SERVICE_URL}/api/v1/tenant/config",
                    params={"domain": host},
                    timeout=3.0,
                )
                if resp.status_code == 200:
                    tenant = resp.json()
                    request.session[cache_key] = tenant
                else:
                    tenant = {
                        "slug": "default",
                        "portal_group": 1,
                        "name": "EduForge",
                        "branding": {"primary": "#1A237E"},
                    }
            except Exception:
                tenant = {
                    "slug": "default",
                    "portal_group": 1,
                    "name": "EduForge",
                    "branding": {"primary": "#1A237E"},
                }

        request.tenant = tenant


class AuthMiddleware(MiddlewareMixin):
    """Validate JWT from cookie. Attach user to request or redirect to login."""

    def process_request(self, request):
        path = request.path_info

        # Skip auth for public routes
        if any(path.startswith(p) for p in PUBLIC_PATHS):
            request.user_data = None
            return None

        token = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if not token:
            return redirect(f"/login/?next={path}")

        try:
            resp = httpx.get(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=3.0,
            )
            if resp.status_code == 200:
                request.user_data = resp.json()
            elif resp.status_code == 401:
                # Token expired — try refresh
                refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
                if refresh:
                    rr = httpx.post(
                        f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/token/refresh",
                        json={"refresh_token": refresh},
                        timeout=3.0,
                    )
                    if rr.status_code == 200:
                        tokens = rr.json()
                        request.user_data = {"_new_tokens": tokens}
                        return None
                return redirect(f"/login/?next={path}&reason=expired")
            else:
                return redirect(f"/login/?next={path}")
        except Exception:
            request.user_data = None
            return redirect(f"/login/?next={path}&reason=service_unavailable")

        return None
