"""Inject tenant branding into every template context."""

from django.conf import settings


def tenant_context(request):
    tenant = getattr(request, "tenant", {})
    branding = tenant.get("branding", {})
    return {
        "tenant": tenant,
        "tenant_name": tenant.get("name", "EduForge"),
        "tenant_slug": tenant.get("slug", "default"),
        "portal_group": tenant.get("portal_group", 1),
        "primary_color": branding.get("primary", "#1A237E"),
        "logo_url": branding.get("logo", "/static/img/eduforge-logo.svg"),
        "logo_dark_url": branding.get(
            "logo_dark", "/static/img/eduforge-logo-dark.svg"
        ),
        "favicon_url": branding.get("favicon", "/static/img/favicon.ico"),
        "cdn_base": settings.CDN_BASE_URL,
        "user": getattr(request, "user_data", None),
    }
