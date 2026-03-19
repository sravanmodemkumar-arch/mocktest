from django.urls import path
from . import views

urlpatterns = [
    path("login/",               views.login_view,         name="login"),
    path("otp/send/",            views.otp_send,           name="otp_send"),
    path("otp/verify/",          views.otp_verify_view,    name="otp_verify"),
    path("otp/verify/submit/",   views.otp_verify_submit,  name="otp_verify_submit"),
    path("select-role/",         views.select_role_view,   name="select_role"),
    path("select-role/confirm/", views.select_role_confirm,name="select_role_confirm"),
    path("setup-profile/",       views.setup_profile_view, name="setup_profile"),
    path("profile/save/",        views.profile_save,       name="profile_save"),
    path("2fa/",                 views.twofa_view,         name="twofa"),
    path("2fa/verify/",          views.twofa_verify,       name="twofa_verify"),
    path("account-blocked/",     views.account_blocked_view,name="account_blocked"),
    path("register/",            views.register_view,      name="register"),
    path("register/submit/",     views.register_submit,    name="register_submit"),
    path("logout/",              views.logout_view,        name="logout"),
    path("session/reauth/",      views.session_reauth,     name="session_reauth"),
    path("partials/session-expired/", views.session_reauth,name="session_expired_partial"),
]
