# Group 1 — Division A: Executive Dashboard Pages Reference

> **Role access:** CEO · CFO · CTO · COO · Platform Owner
> **Base URL prefix:** `/exec/`
> **Theme:** Dark (`portal_base_dark.html`)
> **Status key:** ✅ Spec done · 🔨 In progress · ⬜ Not started

---

## Dashboard Core

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-01 | Executive Dashboard | `/exec/dashboard/` | ✅ | P0 | Main command center — KPI bar, Platform Health, Business Overview, Exam Ops, Revenue, Activity Feed |
| div-a-02 | Platform Health Detail | `/exec/platform-health/` | ⬜ | P0 | Full-page uptime/latency/error-rate charts, SLA tracker, incident timeline, service-by-service breakdown |
| div-a-03 | Exam Operations | `/exec/exam-ops/` | ⬜ | P0 | Full exam table with advanced filters, bulk actions, live user heatmap, capacity alerts |

---

## Institution & Growth

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-04 | Institution Growth | `/exec/institution-growth/` | ⬜ | P1 | MoM/YoY institution onboarding trend, geo choropleth map, cohort analysis, churn risk table |
| div-a-05 | Institution Detail | `/exec/institutions/<id>/` | ⬜ | P1 | Single institution drill-down — usage stats, exam history, student count, billing status, health score |
| div-a-06 | Institution List | `/exec/institutions/` | ⬜ | P1 | Searchable/filterable institution table — tier, region, status, ARR, last active |
| div-a-07 | Student Analytics | `/exec/student-analytics/` | ⬜ | P2 | Total enrollment trends, subject distribution, pass/fail rates, geographic spread |

---

## Financial

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-08 | Financial Overview | `/exec/financial-overview/` | ⬜ | P0 | MTD/YTD revenue, ARR/MRR, subscription mix donut, forecast with confidence band, payment failure alerts |
| div-a-09 | Revenue by Institution | `/exec/revenue/institutions/` | ⬜ | P1 | Per-institution revenue table — plan tier, MRR, invoicing status, renewal date, churn risk |
| div-a-10 | Billing & Invoices | `/exec/billing/` | ⬜ | P1 | Invoice list with status (paid/overdue/draft), download PDF, resend, filter by period |
| div-a-11 | Subscription Plans | `/exec/subscriptions/` | ⬜ | P2 | Plan catalog — pricing tiers, feature matrix, upgrade/downgrade actions, active subscriber counts |

---

## Operations

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-12 | Incident Manager | `/exec/incidents/` | ⬜ | P0 | Active + historical incidents, severity classification, MTTR tracker, post-mortem links |
| div-a-13 | Incident Detail | `/exec/incidents/<id>/` | ⬜ | P1 | Timeline of events, impacted services, affected institutions, resolution steps, assignee |
| div-a-14 | Alerting Rules | `/exec/alerts/` | ⬜ | P2 | View/edit threshold rules — metric, operator, threshold, channel (email/Slack/webhook) |
| div-a-15 | Scheduled Maintenance | `/exec/maintenance/` | ⬜ | P2 | Upcoming + past maintenance windows, create/edit/cancel windows, notification log |

---

## Compliance & Security

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-16 | Compliance Dashboard | `/exec/compliance/` | ⬜ | P1 | SOC2/ISO27001/GDPR status widgets, control pass rate, upcoming audit dates, evidence tracker |
| div-a-17 | Audit Log | `/exec/audit-log/` | ⬜ | P1 | Full audit trail — actor, action, resource, IP, timestamp; exportable; filterable by category |
| div-a-18 | Security Events | `/exec/security/` | ⬜ | P2 | Failed logins, suspicious IPs, privilege escalations, anomaly alerts, SIEM-style feed |
| div-a-19 | Data Residency | `/exec/data-residency/` | ⬜ | P3 | Region-by-region data storage map, GDPR DPA status per institution, retention policy viewer |

---

## Content & Exam Management

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-20 | Exam Catalog | `/exec/exam-catalog/` | ⬜ | P2 | All exam templates — subject, type (MCQ/Descriptive/Mixed), institution, status, usage count |
| div-a-21 | Exam Detail | `/exec/exams/<id>/` | ⬜ | P1 | Exam metadata, live attempt count, student results table, issue log, time-series attempt chart |
| div-a-22 | Question Bank | `/exec/question-bank/` | ⬜ | P3 | Question inventory by subject/difficulty, usage frequency, flag/unflag, bulk import/export |
| div-a-23 | Proctoring Overview | `/exec/proctoring/` | ⬜ | P2 | AI proctoring stats — flagged sessions, violation categories, escalation queue, false-positive rate |

---

## Reports & Analytics

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-24 | Executive Reports | `/exec/reports/` | ⬜ | P1 | Scheduled + on-demand reports — revenue, usage, compliance; export PDF/CSV/XLSX |
| div-a-25 | Usage Analytics | `/exec/usage/` | ⬜ | P2 | API call volume, feature adoption heatmap, peak usage times, slowest endpoints |
| div-a-26 | SLA Dashboard | `/exec/sla/` | ⬜ | P1 | Per-tier SLA commitments vs actuals — uptime, response time, resolution time; breach history |
| div-a-27 | Cohort Analysis | `/exec/cohorts/` | ⬜ | P3 | Institution retention cohorts, student enrollment cohorts, churn waterfall |

---

## Settings & Administration

| ID | Page Name | URL | Status | Priority | Description |
|----|-----------|-----|--------|----------|-------------|
| div-a-28 | Platform Settings | `/exec/settings/platform/` | ⬜ | P2 | Feature flags, global rate limits, maintenance mode toggle, SMTP config, OAuth providers |
| div-a-29 | User Management | `/exec/settings/users/` | ⬜ | P1 | Admin + exec user list — roles, last login, 2FA status, suspend/activate, invite |
| div-a-30 | Role & Permissions | `/exec/settings/roles/` | ⬜ | P2 | RBAC role editor — assign permissions per role, view effective permissions per user |
| div-a-31 | API Keys & Webhooks | `/exec/settings/api/` | ⬜ | P2 | API key management (create/revoke/scope), webhook endpoint config, delivery log |

---

## Drawers & Overlays (used across pages)

| ID | Component | Trigger | Width | Description |
|----|-----------|---------|-------|-------------|
| drawer-A | Preferences | Toolbar avatar → Preferences | 360px | Theme, notification preferences, default date range |
| drawer-B | Service Detail | Platform Health → service row click | 480px | Service health tabs: Overview / Logs / Metrics / Config |
| drawer-C | Exam Detail | Exam Ops → eye icon | 640px | Exam info + Students tab (table + pagination) + Issues tab |
| drawer-D | Institution Detail | Institution rows | 480px | Summary, contact, billing status, quick actions |
| drawer-E | Incident Detail | Incident row | 600px | Timeline, impacted services, resolution steps, assignee |

---

## Implementation Priority Order

```
P0 — Must have for MVP launch
  div-a-01  Executive Dashboard        ✅ spec done
  div-a-02  Platform Health Detail
  div-a-03  Exam Operations (full page)
  div-a-08  Financial Overview
  div-a-12  Incident Manager
  div-a-26  SLA Dashboard

P1 — Required within sprint 2
  div-a-04  Institution Growth
  div-a-05  Institution Detail
  div-a-06  Institution List
  div-a-09  Revenue by Institution
  div-a-10  Billing & Invoices
  div-a-13  Incident Detail
  div-a-16  Compliance Dashboard
  div-a-17  Audit Log
  div-a-21  Exam Detail
  div-a-24  Executive Reports
  div-a-29  User Management

P2 — Sprint 3
  div-a-07, 11, 14, 15, 18, 20, 23, 25, 28, 30, 31

P3 — Backlog
  div-a-19, 22, 27
```

---

## Page Spec Template

Each page spec lives at `docs/pages/group1/div-a/div-a-XX.md` and must include:

1. **Page Header** — title, URL, role access, polling/refresh rules
2. **Layout** — shell + HTMX partials list
3. **Filters / Search** — field names, operators, default values
4. **Table / Chart / Panel specs** — exact column names, data types, sort rules
5. **Empty states** — per-panel empty state copy + illustration
6. **Drawers** — which drawers open, trigger element, width, tabs, content
7. **Pagination** — page size, URL params
8. **API Endpoints** — path, method, query params, response shape
9. **Edge cases** — loading, error, empty, permission-denied states
10. **Component references** — which components from `docs/pages/components/` are used

---

*Last updated: 2026-03-20*
