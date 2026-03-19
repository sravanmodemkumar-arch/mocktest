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
    "apps.core",
    "apps.auth_views",
    "apps.home",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.core.middleware.TenantMiddleware",   # resolves domain → tenant config
    "apps.core.middleware.AuthMiddleware",     # validates JWT from cookie
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

# Sessions — stored in signed cookies (no DB needed)
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7   # 7 days
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

# No database — portal is stateless; all data from API services
DATABASES = {}

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
