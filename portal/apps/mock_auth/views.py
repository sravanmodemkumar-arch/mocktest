"""
Mock Identity Service — only active when DEBUG=True.
Simulates /api/v1/auth/login and /api/v1/auth/me so the portal works
locally without the real FastAPI auth service running.

Credentials match scripts/seed_local.py — password: Test@1234
"""

import hashlib
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import signing

# Seed users — matches scripts/seed_local.py
# Key: any of (mobile, email, username) → user dict
_USERS = [
    {
        "id": 1,
        "full_name": "Arjun Mehta",
        "role": "platform_admin",
        "email": "platform@eduforge.in",
        "mobile": "+910000000001",
        "username": "platform_admin",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 1,
    },
    {
        "id": 2,
        "full_name": "Priya Sharma",
        "role": "chain_admin",
        "email": "chain@eduforge.in",
        "mobile": "+910000000002",
        "username": "chain_admin",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 2,
    },
    {
        "id": 3,
        "full_name": "Dr. Rajan Nair",
        "role": "principal",
        "email": "principal@greenwood.com",
        "mobile": "+910000000003",
        "username": "principal",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 3,
    },
    {
        "id": 4,
        "full_name": "Sujata Rao",
        "role": "teacher",
        "email": "teacher@greenwood.com",
        "mobile": "+910000000004",
        "username": "teacher",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 3,
    },
    {
        "id": 5,
        "full_name": "Rahul Verma",
        "role": "student",
        "email": "student@greenwood.com",
        "mobile": "+910000000005",
        "username": "student1",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 3,
    },
    {
        "id": 6,
        "full_name": "Meera Verma",
        "role": "parent",
        "email": "parent@greenwood.com",
        "mobile": "+910000000006",
        "username": "parent1",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 3,
    },
    {
        "id": 7,
        "full_name": "Prof. Anil Kumar",
        "role": "principal",
        "email": "hod@sunrise.com",
        "mobile": "+910000000007",
        "username": "college_principal",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 4,
    },
    {
        "id": 8,
        "full_name": "Dr. Kavitha S",
        "role": "faculty",
        "email": "faculty@sunrise.com",
        "mobile": "+910000000008",
        "username": "faculty1",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 4,
    },
    {
        "id": 9,
        "full_name": "Ananya Pillai",
        "role": "student",
        "email": "coll_std@sunrise.com",
        "mobile": "+910000000009",
        "username": "coll_student",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 4,
    },
    {
        "id": 10,
        "full_name": "Naresh Gupta",
        "role": "director",
        "email": "director@toppers.com",
        "mobile": "+910000000010",
        "username": "director",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 5,
    },
    {
        "id": 11,
        "full_name": "Deepak Yadav",
        "role": "student",
        "email": "aspirant@ssc.com",
        "mobile": "+919876543210",
        "username": "aspirant1",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 6,
    },
    {
        "id": 12,
        "full_name": "Pooja Mishra",
        "role": "student",
        "email": "premium@ssc.com",
        "mobile": "+919876543211",
        "username": "premium1",
        "subscription": "premium",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 6,
    },
    {
        "id": 13,
        "full_name": "Kiran Reddy",
        "role": "tsp_admin",
        "email": "admin@techedu.in",
        "mobile": "+910000000014",
        "username": "tsp_admin",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 7,
    },
    {
        "id": 14,
        "full_name": "Suresh Joshi",
        "role": "partner",
        "email": "partner@contentpro.in",
        "mobile": "+910000000015",
        "username": "b2b_partner",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 9,
    },
    {
        "id": 15,
        "full_name": "Arun Krishnan",
        "role": "student",
        "email": "unified@student.in",
        "mobile": "+910000000016",
        "username": "unified_student",
        "subscription": "free",
        "profile_complete": True,
        "requires_2fa": False,
        "has_multiple_roles": False,
        "portal_group": 10,
    },
]

_PASSWORD_HASH = hashlib.sha256(b"Test@1234").hexdigest()

# Build lookup index
_INDEX = {}
for u in _USERS:
    for field in ("mobile", "email", "username"):
        _INDEX[u[field]] = u


def _find_user(login_id: str):
    # Try as-is
    user = _INDEX.get(login_id)
    if user:
        return user
    # Try with +91 prefix (mobile without country code)
    if login_id.isdigit() and len(login_id) == 10:
        return _INDEX.get(f"+91{login_id}")
    return None


def _make_token(user):
    return signing.dumps({"id": user["id"], "role": user["role"]}, salt="mock-auth")


def _verify_token(token):
    try:
        data = signing.loads(token, salt="mock-auth", max_age=3600)
        uid = data["id"]
        return next((u for u in _USERS if u["id"] == uid), None)
    except Exception:
        return None


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    login_id = body.get("login_id", "").strip()
    password = body.get("password", "")

    user = _find_user(login_id)
    if not user:
        return JsonResponse({"detail": "User not found"}, status=401)

    if hashlib.sha256(password.encode()).hexdigest() != _PASSWORD_HASH:
        return JsonResponse({"detail": "Incorrect password"}, status=401)

    token = _make_token(user)
    return JsonResponse({
        "access_token": token,
        "refresh_token": token,
        "token_type": "bearer",
    })


@csrf_exempt
@require_http_methods(["GET"])
def me(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    token = auth[7:]
    user = _verify_token(token)
    if not user:
        return JsonResponse({"detail": "Invalid token"}, status=401)

    return JsonResponse(user)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    return JsonResponse({"detail": "Logged out"})


@csrf_exempt
@require_http_methods(["POST"])
def token_refresh(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)
    refresh = body.get("refresh_token", "")
    user = _verify_token(refresh)
    if not user:
        return JsonResponse({"detail": "Invalid refresh token"}, status=401)
    token = _make_token(user)
    return JsonResponse({"access_token": token, "refresh_token": token})
