# 23 — Accident & Incident Register

> **URL:** `/group/transport/safety/incidents/`
> **File:** `23-accident-incident-register.md`
> **Template:** `portal_base.html`
> **Priority:** P0
> **Role:** Group Transport Safety Officer (primary) · Transport Director · Fleet Manager (view)

---

## 1. Purpose

Complete register of all transport accidents and safety incidents across every branch. Each record documents the incident — vehicle, route, driver, students involved, injuries, location, immediate actions, investigation outcome, and corrective measures.

Incident severity classification:
- **Severity 1 (Critical)** — Accident with student injuries, fatality, or major vehicle damage
- **Severity 2 (Serious)** — Near-miss with students, breakdown with students stranded, SOS activation
- **Severity 3 (Moderate)** — Minor vehicle damage, driver misconduct, route deviation
- **Severity 4 (Minor)** — Late bus, missed stop, minor complaint

Severity 1 and 2 incidents require mandatory reporting to Transport Director and Group COO within 2 hours. All incidents require corrective action documentation before closure.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Transport Safety Officer | G3 | Full — create, investigate, close | Primary owner |
| Group Transport Director | G3 | Full view + escalate to COO | Oversight |
| Group Fleet Manager | G3 | Read — vehicle damage context | View only |
| Group COO | G4 | View Sev 1–2 only | Via operations dashboard |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Accident & Incident Register
```

### 3.2 Page Header
- **Title:** `Accident & Incident Register`
- **Subtitle:** `[N] Open · [N] Under Investigation · [N] Closed (AY) · Incident-Free Days: [N]`
- **Right controls:** `+ Report Incident` · `Advanced Filters` · `Export`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| Severity 1 open | "CRITICAL: [N] Severity 1 incident(s) open. Immediate escalation required." | Red |
| Severity 2 unresolved > 24h | "[N] Severity 2 incidents unresolved for > 24 hours." | Amber |
| Investigation overdue > 7 days | "[N] incidents under investigation for > 7 days without update." | Amber |
| Corrective action not documented | "[N] closed incidents have no corrective action documented." | Amber |

---

## 4. KPI Summary Bar

| Card | Metric | Colour Rule |
|---|---|---|
| Total Open Incidents | All branches | Red > 0 · Green = 0 |
| Severity 1 Open | Critical | Red > 0 |
| Severity 2 Open | Serious | Red > 0 |
| Incident-Free Days | Since last any incident | Green > 30 · Yellow 7–30 · Red < 7 |
| Incidents (YTD) | All types | Blue |
| Incidents Closed (Month) | Blue | |

---

## 5. Main Table — Incident Register

**Search:** Incident ID, bus number, branch, driver. 300ms debounce.

**Advanced Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Severity | Checkbox | 1 Critical / 2 Serious / 3 Moderate / 4 Minor |
| Status | Checkbox | Open / Under Investigation / Awaiting Corrective Action / Closed |
| Incident Type | Checkbox | Accident / Near-Miss / Breakdown / Driver Misconduct / SOS / Route Deviation / Late Bus |
| Date Range | Date picker | Incident date range |
| Has Injuries | Checkbox | Show only incidents with injuries |

**Columns:**
| Column | Sortable | Notes |
|---|---|---|
| Incident ID | ✅ | Auto-generated |
| Date | ✅ | |
| Branch | ✅ | |
| Bus No | ✅ | |
| Route | ✅ | |
| Driver | ✅ | |
| Incident Type | ✅ | |
| Severity | ✅ | 1–4 colour-coded badge |
| Students Involved | ✅ | Count · Red if > 0 |
| Injuries | ✅ | Yes / No |
| Status | ✅ | Badge |
| Days Open | ✅ | |
| Actions | ❌ | View · Investigate · Close |

**Default sort:** Severity ascending · Date descending.
**Pagination:** Server-side · 25/page.

---

## 6. Drawers

### 6.1 Drawer: `incident-detail` — View
- **Width:** 700px
- **Tabs:** Incident · Students · Investigation · Corrective Action · Timeline
- **Incident:** All incident fields, location map, photos uploaded
- **Students:** Names, class, injuries (if any), parent notification status
- **Investigation:** Findings, root cause, contributing factors, responsible driver notes
- **Corrective Action:** Actions taken/planned, owner, deadline, completion status
- **Timeline:** Status changes with timestamps and updated-by user

### 6.2 Drawer: `report-incident`
- **Trigger:** + Report Incident
- **Width:** 680px
- **Fields:** Branch · Date/Time · Bus No · Route · Driver (searchable) · Conductor (searchable) · Incident Type · Severity (1–4) · Location (address + GPS if available) · Students Involved (count + names) · Injuries (Yes/No + description) · Vehicle Damage (Yes/No + description) · Immediate Actions Taken · Photos/Documents (upload) · Notify Transport Director (checkbox — mandatory Sev 1–2) · Notify COO (checkbox — mandatory Sev 1)
- **Validation:** Severity 1 → COO notification mandatory · Injuries must include count if Yes

### 6.3 Drawer: `investigation-update`
- **Trigger:** Actions → Investigate
- **Width:** 600px
- **Fields:** Investigation Status (In Progress / Findings Documented) · Root Cause · Contributing Factors · Driver Accountability (Negligent / Not Negligent / Under Review) · Findings Summary · Upload Investigation Report
- **On save:** Status updates to "Under Investigation" or "Awaiting Corrective Action"

### 6.4 Modal: `close-incident`
- **Width:** 480px
- **Fields:** Resolution Summary · Corrective Actions Taken (multi-row: action, owner, completion date) · Lessons Learned · Preventive Measures · Upload Final Report
- **Validation:** At least one corrective action must be documented

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Incident reported | "Incident [ID] reported at [Branch]. [Notifications sent per severity]." | Warning | 6s |
| Severity 1 escalated | "Severity 1 incident escalated to COO. Emergency response activated." | Warning | 8s |
| Investigation updated | "Investigation updated for Incident [ID]." | Info | 4s |
| Incident closed | "Incident [ID] closed. Corrective actions documented." | Success | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No open incidents | "No Open Incidents" | "All transport safety incidents are resolved." | — |
| No incidents on record | "No Incidents Recorded" | "No transport incidents have been reported this AY." | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 6 KPI cards + incident table |
| Filter/search | Table body skeleton |
| Incident detail drawer | 700px skeleton; tabs load lazily |
| Report incident submit | Spinner on Save |

---

## 10. Role-Based UI Visibility

| Element | Safety Officer G3 | Transport Director G3 | Fleet Manager G3 | COO G4 |
|---|---|---|---|---|
| Report Incident | ✅ | ✅ | ❌ | ❌ |
| Investigate | ✅ | ✅ | ❌ | ❌ |
| Close Incident | ✅ | ✅ | ❌ | ❌ |
| Escalate to COO | ✅ | ✅ | ❌ | — |
| View Sev 1–2 | ✅ | ✅ | ✅ | ✅ |
| View All Severities | ✅ | ✅ | ✅ (fleet context) | Sev 1–2 only |
| Export | ✅ | ✅ | ✅ | ✅ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/incidents/` | JWT (G3+) | Paginated incident list |
| POST | `/api/v1/group/{group_id}/transport/incidents/` | JWT (G3+) | Report incident |
| GET | `/api/v1/group/{group_id}/transport/incidents/{id}/` | JWT (G3+) | Incident detail |
| PATCH | `/api/v1/group/{group_id}/transport/incidents/{id}/` | JWT (G3+) | Update investigation |
| POST | `/api/v1/group/{group_id}/transport/incidents/{id}/close/` | JWT (G3+) | Close incident |
| POST | `/api/v1/group/{group_id}/transport/incidents/{id}/escalate/` | JWT (G3+) | Escalate to COO |
| GET | `/api/v1/group/{group_id}/transport/incidents/kpis/` | JWT (G3+) | KPI cards |
| GET | `/api/v1/group/{group_id}/transport/incidents/export/` | JWT (G3+) | Export |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
