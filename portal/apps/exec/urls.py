from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard (div-a-01) ─────────────────────────────────────────────────
    path("exec/dashboard/",                   views.dashboard,          name="exec_dashboard"),
    path("exec/nav/",                          views.exec_nav,           name="exec_nav"),

    # ── Full pages — ONE URL each (shell + all partials via ?part=) ──────────
    path("exec/platform-health/",             views.platform_health,    name="exec_platform_health"),
    path("exec/exam-ops/",                     views.exam_ops,           name="exec_exam_ops"),
    path("exec/financial-overview/",           views.financial_overview, name="exec_financial_overview"),
    path("exec/incidents/",                    views.incidents,          name="exec_incidents"),
    path("exec/incidents/<str:incident_id>/",  views.incident_detail,    name="exec_incident_detail"),
    path("exec/institutions/",                 views.institutions,       name="exec_institutions"),
    path("exec/institutions/<str:inst_id>/",   views.institution_detail, name="exec_institution_detail"),
    path("exec/compliance/",                   views.compliance,         name="exec_compliance"),
    path("exec/audit-log/",                    views.audit_log,          name="exec_audit_log"),
    path("exec/reports/",                      views.reports,            name="exec_reports"),
    path("exec/settings/users/",               views.user_management,    name="exec_user_management"),
    path("exec/sla/",                          views.sla_dashboard,      name="exec_sla"),
]
