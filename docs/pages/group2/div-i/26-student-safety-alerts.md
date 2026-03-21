# 26 — Student Safety Alerts

> **URL:** `/group/transport/safety/alerts/`
> **File:** `26-student-safety-alerts.md`
> **Template:** `portal_base.html`
> **Priority:** P0
> **Role:** Group Transport Safety Officer (primary) · Transport Director · Branch Transport

---

## 1. Purpose

Real-time and historical feed of all student safety alerts triggered during transport operations. Alerts are generated automatically by the GPS system (late bus, geo-fence breach, SOS) or manually by branch staff (missing student, parent complaint, driver behaviour concern).

Parents of affected students are notified via WhatsApp/SMS for relevant alert types. The Safety Officer resolves alerts, links them to incidents if needed, and maintains a clean audit trail.

Alert types:
- **Late Bus** (GPS-triggered) — Bus delayed > 15 min from scheduled stop time
- **Geo-fence Breach** (GPS-triggered) — Bus left approved route corridor
- **SOS Alert** (Device-triggered) — Driver pressed SOS button
- **Student Not Boarded** (Manual) — Student expected but did not board at stop
- **Student Not Dropped** (Manual) — Student not confirmed at drop point
- **Overcrowding Alert** (Manual) — Bus over capacity with students standing
- **Driver Behaviour Concern** (Manual) — Parent/staff complaint about driver
- **Bus Breakdown with Students** (Manual) — Vehicle broken down mid-route with students

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Transport Safety Officer | G3 | Full — view, resolve, escalate all alerts | Primary owner |
| Group Transport Director | G3 | View + escalate Sev 1–2 | Oversight |
| Branch Transport In-Charge | Branch G3 | View own branch alerts + raise manual alerts | Scoped |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Student Safety Alerts
```

### 3.2 Page Header
- **Title:** `Student Safety Alerts`
- **Subtitle:** `[N] Active Alerts · [N] Resolved Today · [N] Alerts This Week`
- **Right controls:** `+ Raise Manual Alert` · `Advanced Filters` · `Export`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| SOS alert active | "🚨 SOS ACTIVE: Bus [No] at [Branch]. Immediate response required." | Critical Red |
| Student not dropped 30min past school time | "[N] students not confirmed at drop point > 30 min after school end." | Red |
| Multiple late buses | "[N] buses are delayed > 30 minutes at current stop." | Amber |

---

## 4. KPI Summary Bar

| Card | Metric | Colour Rule |
|---|---|---|
| Active Alerts (Now) | Unresolved | Red > 0 · Green = 0 |
| SOS Alerts (Today) | | Red > 0 |
| Late Bus Alerts (Today) | | Yellow > 0 |
| Student Not Boarded/Dropped (Today) | | Red > 0 |
| Parent Notifications Sent (Today) | Count | Blue |
| Avg Resolution Time | Minutes | Green < 15 · Yellow 15–30 · Red > 30 |

---

## 5. Main Table — Alert Feed

**Search:** Bus number, student name, branch, route. 300ms debounce.

**Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Alert Type | Checkbox | Late Bus / SOS / Geo-fence / Not Boarded / Not Dropped / Overcrowding / Driver Concern / Breakdown |
| Status | Radio | Active / Resolved / Escalated |
| Severity | Checkbox | Critical / High / Medium / Low |
| Date Range | Date picker | |

**Columns:**
| Column | Sortable | Notes |
|---|---|---|
| Alert ID | ✅ | |
| Time | ✅ | When triggered |
| Branch | ✅ | |
| Alert Type | ✅ | Badge + icon |
| Bus No | ✅ | |
| Route | ✅ | |
| Students Affected | ✅ | Count |
| Parent Notified | ✅ | ✅ Yes · — Not yet |
| Status | ✅ | Active / Resolved badge |
| Time to Resolve | ✅ | Minutes (if resolved) |
| Actions | ❌ | View · Resolve · Escalate · Notify Parents |

**Default sort:** Time descending (newest first). Active alerts pinned to top.
**Pagination:** Server-side · 25/page.
**Auto-refresh:** Every 60 seconds for Active status column and alert count.

---

## 6. Drawers

### 6.1 Drawer: `alert-detail`
- **Width:** 600px
- **Tabs:** Alert · Response · Parent Notifications
- **Alert:** Alert type, time, bus, route, driver, location (map if GPS), students affected
- **Response:** Resolution notes, actions taken, linked incident (if any), resolved by, resolution time
- **Parent Notifications:** WhatsApp/SMS messages sent to affected parents with timestamps and delivery status

### 6.2 Drawer: `raise-manual-alert`
- **Width:** 520px
- **Fields:** Branch · Bus No · Route · Alert Type · Severity · Description · Students Affected (names, if known) · Time of Occurrence · Notify Parents (checkbox) · Notify Transport Director (checkbox for Sev 1–2)

### 6.3 Modal: `resolve-alert`
- **Width:** 480px
- **Fields:** Resolution Summary · Actions Taken · Link to Incident (if applicable) · Parent Follow-up Required (checkbox)

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Alert raised | "Safety alert [ID] raised. Relevant staff notified." | Warning | 6s |
| Alert resolved | "Alert [ID] resolved in [N] minutes." | Success | 4s |
| Parent notified | "WhatsApp notification sent to [N] parents." | Info | 4s |
| SOS acknowledged | "SOS alert acknowledged. Emergency response activated." | Warning | 8s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No active alerts | "No Active Safety Alerts" | "All student safety alerts for today have been resolved." | — |
| No alerts on record | "No Safety Alerts" | "No transport safety alerts have been recorded." | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 6 KPI cards + alert table |
| Auto-refresh | Shimmer on Active column and KPI counts |
| Alert detail drawer | 600px skeleton |

---

## 10. Role-Based UI Visibility

| Element | Safety Officer G3 | Transport Director G3 | Branch Transport |
|---|---|---|---|
| View All Branches | ✅ | ✅ | Own branch only |
| Raise Manual Alert | ✅ | ✅ | ✅ |
| Resolve Alert | ✅ | ✅ | Own branch only |
| Escalate to Director/COO | ✅ | — | ✅ |
| Notify Parents | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/safety-alerts/` | JWT (G3+) | Alert list |
| POST | `/api/v1/group/{group_id}/transport/safety-alerts/` | JWT (G3+) | Raise manual alert |
| GET | `/api/v1/group/{group_id}/transport/safety-alerts/{id}/` | JWT (G3+) | Alert detail |
| POST | `/api/v1/group/{group_id}/transport/safety-alerts/{id}/resolve/` | JWT (G3+) | Resolve alert |
| POST | `/api/v1/group/{group_id}/transport/safety-alerts/{id}/notify-parents/` | JWT (G3+) | Send parent notification |
| GET | `/api/v1/group/{group_id}/transport/safety-alerts/kpis/` | JWT (G3+) | KPI cards |
| GET | `/api/v1/group/{group_id}/transport/gps/alerts/` | JWT (G3+) | GPS-triggered alerts (for SOS/geo-fence) |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
