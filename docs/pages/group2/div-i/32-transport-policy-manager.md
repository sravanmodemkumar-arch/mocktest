# 32 — Transport Policy Manager

> **URL:** `/group/transport/policies/`
> **File:** `32-transport-policy-manager.md`
> **Template:** `portal_base.html`
> **Priority:** P2
> **Role:** Group Transport Director (primary) · Transport Safety Officer

---

## 1. Purpose

Manages all transport-related policy documents — fleet policy, driver conduct policy, route approval standards, safety protocols, GPS usage policy, student transport eligibility, and escalation procedures. Policies are versioned, published to relevant roles, and require acknowledgement from branch transport staff.

The Transport Director is the policy owner. All policies are drafted here, approved, and then distributed to branches. When a policy is updated, affected branches must re-acknowledge.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Transport Director | G3 | Full — create, edit, publish, retire | Primary owner |
| Group Transport Safety Officer | G3 | Create safety policies + view all | Shared authorship |
| Group Fleet Manager | G3 | Read — fleet policies | View only |
| Branch Transport In-Charge | Branch G3 | Read + acknowledge | View own applicable policies |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Transport Policy Manager
```

### 3.2 Page Header
- **Title:** `Transport Policy Manager`
- **Subtitle:** `[N] Active Policies · [N] Pending Acknowledgement · Last Updated: [date]`
- **Right controls:** `+ New Policy` · `Export All Policies`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| Policies not reviewed in > 180 days | "[N] policies are overdue for annual review." | Amber |
| Branches with pending acknowledgements | "[N] branches have unacknowledged policy updates." | Amber |

---

## 4. KPI Summary Bar

| Card | Metric | Colour Rule |
|---|---|---|
| Total Active Policies | Blue | |
| Branches Fully Acknowledged | % | Green = 100% · Red < 90% |
| Policies Due for Review | Past 180-day cycle | Yellow > 0 |

---

## 5. Policy Library Table

**Filters:** Policy Type · Status (Active / Draft / Retired) · Acknowledgement (All / Pending / Complete)

**Policy Types:**
- Fleet Management Policy
- Driver Conduct & Behaviour Policy
- Route Approval Standards
- GPS Usage & Monitoring Policy
- Student Transport Eligibility Policy
- Incident Reporting & Escalation Policy
- Safety Inspection Standards
- Fee & Bus Pass Policy

**Columns:** Policy Name · Type · Version · Last Updated · Applicable Roles · Status · Acknowledgement % · Actions (View · Edit · Publish · Retire)

---

## 6. Drawers

### 6.1 Drawer: `policy-create`
- **Width:** 700px
- **Fields:** Policy Name · Type · Version (auto-incremented) · Content (rich text editor — headings, bullet points, tables) · Applicable Roles (multi-select) · Applicable Branches (All / Select) · Review Cycle (days) · Effective Date

### 6.2 Drawer: `policy-detail`
- **Width:** 700px
- **Tabs:** Content · Acknowledgements · Version History
- **Content:** Full policy text, rendered
- **Acknowledgements:** Branch-wise acknowledgement status with dates; Send Reminder button
- **Version History:** All versions with diff summary, author, date

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Policy published | "Policy [Name] v[N] published to [N] branches." | Success | 4s |
| Acknowledgement reminder | "Reminder sent to [N] branches." | Info | 4s |
| Policy retired | "Policy [Name] retired." | Info | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No policies | "No Transport Policies" | "Create transport policies to govern operations." | [+ New Policy] |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 3 KPI cards + policy table |
| Policy detail drawer | 700px skeleton; rich text content renders progressively |

---

## 10. Role-Based UI Visibility

| Element | Transport Director G3 | Safety Officer G3 | Fleet Manager G3 | Branch Transport |
|---|---|---|---|---|
| Create Policy | ✅ | ✅ (safety only) | ❌ | ❌ |
| Edit Policy | ✅ | ✅ (safety only) | ❌ | ❌ |
| Publish Policy | ✅ | ❌ (Director approves) | ❌ | ❌ |
| Acknowledge | ❌ | ❌ | ❌ | ✅ |
| View All Policies | ✅ | ✅ | ✅ | ✅ (applicable only) |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/policies/` | JWT (G3+) | Policy list |
| POST | `/api/v1/group/{group_id}/transport/policies/` | JWT (G3+) | Create policy |
| GET | `/api/v1/group/{group_id}/transport/policies/{id}/` | JWT (G3+) | Policy detail |
| PATCH | `/api/v1/group/{group_id}/transport/policies/{id}/` | JWT (G3+) | Update policy |
| POST | `/api/v1/group/{group_id}/transport/policies/{id}/publish/` | JWT (G3+) | Publish |
| POST | `/api/v1/group/{group_id}/transport/policies/{id}/acknowledge/` | JWT (Branch) | Acknowledge |
| POST | `/api/v1/group/{group_id}/transport/policies/{id}/reminder/` | JWT (G3+) | Send acknowledgement reminder |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
