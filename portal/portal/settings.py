import environ
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-secret-key-change-in-prod")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.humanize",
    "apps.core",
    "apps.auth_views",
    "apps.home",
    "apps.exec",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.core.middleware.TenantMiddleware",  # resolves domain → tenant config
    "apps.core.middleware.AuthMiddleware",  # validates JWT from cookie
]

ROOT_URLCONF = "portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.tenant_context",
            ],
        },
    },
]

WSGI_APPLICATION = "portal.wsgi.application"
ASGI_APPLICATION = "portal.asgi.application"

import sys as _sys

# During testing allow any host — tests use arbitrary domains (school.test.com etc.)
if "pytest" in _sys.modules:
    ALLOWED_HOSTS = ["*"]

# Signed cookies in production (stateless). DB-backed only during testing so
# Django's test client can set session data via client.session.
SESSION_ENGINE = (
    "django.contrib.sessions.backends.db"
    if "pytest" in _sys.modules
    else "django.contrib.sessions.backends.signed_cookies"
)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
SESSION_COOKIE_SECURE = not DEBUG

# JWT stored in httpOnly cookie named "ef_token"
AUTH_COOKIE_NAME = "ef_token"
AUTH_COOKIE_REFRESH = "ef_refresh"

# Backend service URLs
IDENTITY_SERVICE_URL = env("IDENTITY_SERVICE_URL", default="http://localhost:8001")
TENANT_SERVICE_URL = env("TENANT_SERVICE_URL", default="http://localhost:8003")
HOME_SERVICE_URL = env("HOME_SERVICE_URL", default="http://localhost:8002")

# Cloudflare R2 / CDN
CDN_BASE_URL = env("CDN_BASE_URL", default="https://cdn.eduforge.in")

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Portal is stateless — no database queries in production.
# SQLite in-memory is configured only to satisfy Django's test runner / django_db marker.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
