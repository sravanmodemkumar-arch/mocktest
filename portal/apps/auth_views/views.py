"""Auth views — login, OTP verify, role select, profile setup, 2FA."""

import httpx
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect


def login_view(request):
    """GET: render login page. Auth is password-based; OTP is institution-configurable."""
    if request.COOKIES.get(settings.AUTH_COOKIE_NAME):
        return redirect("/home/")
    return render(request, "auth/login.html")


@require_http_methods(["POST"])
@csrf_protect
def password_login(request):
    """Primary login: mobile/email/username + password.
    On success: staff/admin roles are redirected to /2fa/, others go to /home/.
    OTP is a separate configurable flow, not part of primary login.
    """
    login_id = request.POST.get("login_id", "").strip()
    password = request.POST.get("password", "")

    if not login_id or not password:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Please enter your mobile/email and password.</p>'
        )

    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/login",
            json={"login_id": login_id, "password": password},
            timeout=5.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            access = data["access_token"]
            refresh = data["refresh_token"]

            me_resp = httpx.get(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access}"},
                timeout=3.0,
            )
            user = me_resp.json() if me_resp.status_code == 200 else {}

            # Staff/admin roles require 2FA; students/parents go directly home
            staff_roles = {
                "principal",
                "vice_principal",
                "director",
                "admin",
                "teacher",
                "faculty",
                "hod",
                "chain_admin",
                "platform_admin",
            }
            role = user.get("role", "")

            if role in staff_roles and user.get("requires_2fa", False):
                next_url = "/2fa/"
            elif user.get("profile_complete") is False:
                next_url = "/setup-profile/"
            elif user.get("has_multiple_roles"):
                next_url = "/select-role/"
            else:
                next_url = request.session.get("login_next", "/home/")

            response = HttpResponse(status=204)
            response["HX-Redirect"] = next_url
            response.set_cookie(
                settings.AUTH_COOKIE_NAME,
                access,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                max_age=60 * 30,
            )
            response.set_cookie(
                settings.AUTH_COOKIE_REFRESH,
                refresh,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                max_age=60 * 60 * 24 * 7,
            )
            return response

        elif resp.status_code == 401:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Incorrect mobile number or password.</p>'
            )
        elif resp.status_code == 423:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/account-blocked/"
            return response
        else:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Login failed. Please try again.</p>'
            )
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable. Please try again shortly.</p>'
        )


# ---------------------------------------------------------------------------
# OTP send/verify — institution-configurable, OFF by default.
# Enabled per-institution from admin panel (tenant.otp_login_enabled flag).
# Used for critical actions (password reset confirmation, suspicious login, etc.)
# when the institution enables it. Not part of standard daily login flow.
# ---------------------------------------------------------------------------


@require_http_methods(["POST"])
@csrf_protect
def otp_send(request):
    """HTMX: send OTP — only active when institution has otp_login_enabled."""
    mobile = request.POST.get("mobile", "").strip()
    channel = request.POST.get("channel", "whatsapp")

    if len(mobile) != 10 or not mobile.isdigit():
        return HttpResponse(
            '<p class="text-red-600 text-sm">Please enter a valid 10-digit mobile number.</p>'
        )

    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/otp/send",
            json={"mobile": f"+91{mobile}", "channel": channel},
            timeout=5.0,
        )
        if resp.status_code == 200:
            # Store mobile in session, redirect to OTP page via HX-Redirect
            request.session["otp_mobile"] = mobile
            request.session["otp_channel"] = channel
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/otp/verify/"
            return response
        elif resp.status_code == 429:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Too many OTP requests. Please wait 30 minutes.</p>'
            )
        else:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Failed to send OTP. Please try again.</p>'
            )
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable. Please try again shortly.</p>'
        )


def otp_verify_view(request):
    """GET: render OTP verification page."""
    mobile = request.session.get("otp_mobile", "")
    channel = request.session.get("otp_channel", "whatsapp")
    if not mobile:
        return redirect("/login/")
    return render(
        request,
        "auth/verify_otp.html",
        {
            "mobile": mobile,
            "channel": channel,
        },
    )


@require_http_methods(["POST"])
@csrf_protect
def otp_verify_submit(request):
    """HTMX endpoint: verify OTP against identity service."""
    mobile = request.session.get("otp_mobile", "")
    otp = request.POST.get("otp", "").strip()

    if not mobile or len(otp) != 6:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Invalid OTP. Please enter all 6 digits.</p>',
            status=400,
        )

    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/otp/verify",
            json={"mobile": f"+91{mobile}", "otp": otp},
            timeout=5.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            access = data["access_token"]
            refresh = data["refresh_token"]

            # Get user profile to check next step
            me_resp = httpx.get(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access}"},
                timeout=3.0,
            )
            user = me_resp.json() if me_resp.status_code == 200 else {}

            # Determine next step
            if user.get("requires_2fa"):
                next_url = "/2fa/"
            elif user.get("profile_complete") is False:
                next_url = "/setup-profile/"
            elif user.get("has_multiple_roles"):
                next_url = "/select-role/"
            else:
                next_url = request.session.get("login_next", "/home/")

            response = HttpResponse(status=204)
            response["HX-Redirect"] = next_url
            # Set httpOnly cookies
            response.set_cookie(
                settings.AUTH_COOKIE_NAME,
                access,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                max_age=60 * 30,
            )
            response.set_cookie(
                settings.AUTH_COOKIE_REFRESH,
                refresh,
                httponly=True,
                samesite="Lax",
                secure=not settings.DEBUG,
                max_age=60 * 60 * 24 * 7,
            )
            return response

        elif resp.status_code == 401:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Incorrect OTP. Please try again.</p>',
                status=401,
            )
        elif resp.status_code == 423:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/account-blocked/"
            return response
        else:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Verification failed. Please try again.</p>',
                status=400,
            )
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable. Please try again shortly.</p>',
            status=503,
        )


def select_role_view(request):
    """GET: render role selector page with user's available roles."""
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
    try:
        resp = httpx.get(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/roles",
            headers={"Authorization": f"Bearer {token}"},
            timeout=3.0,
        )
        roles = resp.json().get("roles", []) if resp.status_code == 200 else []
    except Exception:
        roles = []
    return render(request, "auth/select_role.html", {"roles": roles})


@require_http_methods(["GET"])
def select_role_confirm(request):
    """Confirm role selection — set role in session, redirect to home."""
    role_id = request.GET.get("role_id")
    institution_id = request.GET.get("institution_id")
    request.session["active_role_id"] = role_id
    request.session["active_institution_id"] = institution_id
    return redirect("/home/")


def setup_profile_view(request):
    return render(request, "auth/setup_profile.html")


@require_http_methods(["POST"])
@csrf_protect
def profile_save(request):
    """Save profile via HTMX — forward to identity service."""
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
    try:
        httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/profile",
            json={
                "full_name": request.POST.get("full_name"),
                "language": request.POST.get("language", "en"),
                "email": request.POST.get("email"),
                "notif_sms": request.POST.get("notif_sms") == "on",
                "notif_email": request.POST.get("notif_email") == "on",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=5.0,
        )
    except Exception:
        pass
    response = HttpResponse(status=204)
    response["HX-Redirect"] = "/home/"
    return response


def twofa_view(request):
    return render(request, "auth/2fa.html")


@require_http_methods(["POST"])
@csrf_protect
def twofa_verify(request):
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
    totp = request.POST.get("totp", "")
    backup = request.POST.get("backup_code", "")
    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/2fa/verify",
            json={"totp": totp, "backup_code": backup},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5.0,
        )
        if resp.status_code == 200:
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/home/"
            return response
        return HttpResponse(
            '<p class="text-red-600 text-sm">Invalid code. Please try again.</p>',
            status=401,
        )
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable.</p>', status=503
        )


def account_blocked_view(request):
    context = {
        "reason": request.GET.get("reason"),
        "reference_id": request.GET.get("ref"),
        "resolution_steps": [],
        "support_email": "support@eduforge.in",
    }
    return render(request, "auth/account_blocked.html", context)


def register_view(request):
    return render(request, "auth/register.html")


@require_http_methods(["POST"])
@csrf_protect
def register_submit(request):
    mobile = request.POST.get("mobile", "").strip()
    if len(mobile) != 10 or not mobile.isdigit():
        return HttpResponse(
            '<p class="text-red-600 text-sm">Enter a valid 10-digit mobile number.</p>'
        )
    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/register",
            json={
                "full_name": request.POST.get("full_name"),
                "mobile": f"+91{mobile}",
                "dob": request.POST.get("dob"),
                "state": request.POST.get("state"),
                "target_exam": request.POST.get("target_exam"),
            },
            timeout=5.0,
        )
        if resp.status_code in (200, 201):
            request.session["otp_mobile"] = mobile
            request.session["otp_channel"] = "whatsapp"
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/otp/verify/"
            return response
        detail = resp.json().get("detail", "Registration failed.")
        return HttpResponse(f'<p class="text-red-600 text-sm">{detail}</p>', status=400)
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable.</p>', status=503
        )


def logout_view(request):
    """Clear auth cookies and redirect to login."""
    token = request.COOKIES.get(settings.AUTH_COOKIE_NAME, "")
    if token:
        try:
            httpx.post(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
                timeout=3.0,
            )
        except Exception:
            pass
    response = redirect("/login/")
    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH)
    request.session.flush()
    return response


def session_reauth(request):
    """HTMX: re-authenticate without full page reload."""
    if request.method == "POST":
        return password_login(request)
    return render(request, "partials/session_expired.html")


def forgot_password_view(request):
    """Render forgot password page (step 1: enter email)."""
    return render(request, "auth/forgot_password.html")


@require_http_methods(["POST"])
@csrf_protect
def forgot_password_request(request):
    """HTMX: send email OTP for password reset.
    Email OTP is always available regardless of institution's otp_login_enabled setting.
    """
    email = request.POST.get("email", "").strip().lower()
    if not email or "@" not in email:
        return HttpResponse(
            '<div id="step-email" hx-swap-oob="true">'
            '<p class="text-red-600 text-sm">Please enter a valid email address.</p>'
            "</div>"
        )
    try:
        httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/password/reset-otp",
            json={"email": email},
            timeout=5.0,
        )
    except Exception:
        pass

    # Always show OTP entry screen to prevent email enumeration
    request.session["reset_email"] = email
    return render(request, "auth/reset_otp_verify.html", {"email": email})


@require_http_methods(["POST"])
@csrf_protect
def forgot_password_verify_otp(request):
    """HTMX: verify email OTP for password reset, then show new password form."""
    email = request.session.get("reset_email", "")
    otp = request.POST.get("otp", "").strip()

    if not email or len(otp) != 6:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Invalid code. Please enter all 6 digits.</p>',
            status=400,
        )
    try:
        resp = httpx.post(
            f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/password/reset-otp-verify",
            json={"email": email, "otp": otp},
            timeout=5.0,
        )
        if resp.status_code == 200:
            reset_token = resp.json().get("reset_token", "")
            request.session["reset_token"] = reset_token
            response = HttpResponse(status=204)
            response["HX-Redirect"] = "/reset-password/"
            return response
        return HttpResponse(
            '<p class="text-red-600 text-sm">Incorrect OTP. Please try again.</p>',
            status=401,
        )
    except Exception:
        return HttpResponse(
            '<p class="text-red-600 text-sm">Service unavailable. Please try again.</p>',
            status=503,
        )


def reset_password_view(request):
    """GET: show new password form. POST: submit new password."""
    reset_token = request.session.get("reset_token", "")
    if not reset_token:
        return redirect("/forgot-password/")

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")
        if password != confirm or len(password) < 8:
            return HttpResponse(
                '<p class="text-red-600 text-sm">'
                "Passwords must match and be at least 8 characters."
                "</p>"
            )
        try:
            resp = httpx.post(
                f"{settings.IDENTITY_SERVICE_URL}/api/v1/auth/password/reset",
                json={"reset_token": reset_token, "new_password": password},
                timeout=5.0,
            )
            if resp.status_code == 200:
                request.session.pop("reset_token", None)
                request.session.pop("reset_email", None)
                response = HttpResponse(status=204)
                response["HX-Redirect"] = "/login/?reset=success"
                return response
            return HttpResponse(
                '<p class="text-red-600 text-sm">Reset failed. Please start again.</p>'
            )
        except Exception:
            return HttpResponse(
                '<p class="text-red-600 text-sm">Service unavailable.</p>', status=503
            )

    return render(request, "auth/reset_password.html")
