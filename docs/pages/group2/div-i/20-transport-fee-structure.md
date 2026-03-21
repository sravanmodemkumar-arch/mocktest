# 20 — Transport Fee Structure

> **URL:** `/group/transport/fees/structure/`
> **File:** `20-transport-fee-structure.md`
> **Template:** `portal_base.html`
> **Priority:** P0
> **Role:** Group Transport Fee Manager (primary) · Transport Director · CFO (view)

---

## 1. Purpose

Defines and manages transport fee plans across all branches. Transport fees are charged based on route distance zones, bus type (AC/non-AC), or specific route. A student's transport fee is determined by their assigned route's fee plan.

Fee plans are configured per branch and per zone/route. Small groups may have one flat fee per branch; large groups may have 10–20 distance slabs per branch. The Fee Manager creates and updates fee plans; changes take effect from the next billing cycle (term or month).

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Transport Fee Manager | G3 | Full — create, edit, activate fee plans | Primary owner |
| Group Transport Director | G3 | View + approve major revisions | Oversight |
| Group CFO | G1 | Read-only — cost review | View only |
| Group Route Planning Manager | G3 | Read — fee per route reference | View only |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Transport Fee Structure
```

### 3.2 Page Header
- **Title:** `Transport Fee Structure`
- **Subtitle:** `[N] Active Plans · [N] Branches · AY [current]`
- **Right controls:** `+ New Fee Plan` · `Copy Plans from Last AY` · `Export`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| Routes with no fee plan | "[N] active routes have no fee plan — students cannot be billed." | Red |
| Fee plan not set for new AY | "[N] branches have no fee plan configured for AY [next]." | Amber |

---

## 4. KPI Summary Bar

| Card | Metric | Colour Rule |
|---|---|---|
| Total Fee Plans | Active across all branches | Blue |
| Branches with All Routes Covered | % | Green = 100% · Red < 100% |
| Routes Without Fee Plan | Must-fix | Red > 0 |
| Avg Fee per Student/Month | ₹ across all plans | Blue |
| Highest Fee Plan | ₹/month | Blue (informational) |
| Lowest Fee Plan | ₹/month | Blue (informational) |

---

## 5. Main Table — Fee Plans

**Search:** Branch, plan name, route. 300ms debounce.

**Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Fee Type | Radio | All / Zone-based / Route-specific / Flat |
| Status | Radio | All / Active / Draft / Retired |
| Academic Year | Select | Current AY / Past AYs |

**Columns:**
| Column | Sortable | Notes |
|---|---|---|
| Branch | ✅ | |
| Plan Name | ✅ | Link → plan detail drawer |
| Fee Type | ✅ | Zone / Route / Flat |
| Zone / Route | ✅ | Applicable scope |
| Fee Per Month (₹) | ✅ | |
| Fee Per Term (₹) | ✅ | × 4 months per term |
| Annual Fee (₹) | ✅ | |
| Students Enrolled | ✅ | On this plan |
| AY | ✅ | |
| Status | ✅ | Active / Draft / Retired badge |
| Actions | ❌ | View · Edit · Clone · Retire |

**Pagination:** Server-side · 25/page.

---

## 6. Drawers

### 6.1 Drawer: `create-fee-plan`
- **Trigger:** + New Fee Plan
- **Width:** 600px
- **Fields:** Branch · Plan Name · Academic Year · Fee Type (Zone-based / Route-specific / Flat) · Route(s) applicable (multi-select) · Fee Per Month (₹) · Billing Frequency (Monthly / Per Term / Annual) · Late Payment Penalty (₹/day after due date) · Grace Period (days) · Effective From (date) · Notes
- **Validation:** Fee must be > 0 · At least one route must be selected unless Flat type

### 6.2 Drawer: `fee-plan-detail`
- **Width:** 600px
- **Tabs:** Plan Details · Routes Linked · Students · History
- **Plan Details:** All fee configuration fields
- **Routes Linked:** All routes using this plan with student counts
- **Students:** All students on this fee plan
- **History:** AY-by-AY fee history, revision log

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Fee plan created | "Fee plan [Name] created for [Branch]." | Success | 4s |
| Fee plan updated | "Fee plan updated. Changes effective from [date]." | Info | 4s |
| Plan cloned | "Fee plan cloned for AY [next year]. Review and activate." | Info | 4s |
| Plan retired | "Fee plan [Name] retired. Affected students: [N]." | Warning | 5s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No fee plans | "No Transport Fee Plans" | "Create fee plans for each branch before billing students." | [+ New Fee Plan] |
| No routes without plans | "All Routes Have Fee Plans" | "Every active route has a fee plan configured." | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 6 KPI cards + fee plan table |
| Filter/search | Table body skeleton |
| Create / detail drawer | 600px skeleton |

---

## 10. Role-Based UI Visibility

| Element | Fee Manager G3 | Transport Director G3 | CFO G1 | Route Planning Mgr G3 |
|---|---|---|---|---|
| Create Fee Plan | ✅ | ✅ (major revision) | ❌ | ❌ |
| Edit Fee Plan | ✅ | ❌ | ❌ | ❌ |
| Retire Fee Plan | ✅ | ✅ | ❌ | ❌ |
| View All Plans | ✅ | ✅ | ✅ | ✅ |
| Clone to Next AY | ✅ | ❌ | ❌ | ❌ |
| Export | ✅ | ✅ | ✅ | ✅ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/fees/plans/` | JWT (G3+) | Fee plan list |
| POST | `/api/v1/group/{group_id}/transport/fees/plans/` | JWT (G3+) | Create plan |
| GET | `/api/v1/group/{group_id}/transport/fees/plans/{id}/` | JWT (G3+) | Plan detail |
| PATCH | `/api/v1/group/{group_id}/transport/fees/plans/{id}/` | JWT (G3+) | Update plan |
| POST | `/api/v1/group/{group_id}/transport/fees/plans/{id}/clone/` | JWT (G3+) | Clone for next AY |
| POST | `/api/v1/group/{group_id}/transport/fees/plans/{id}/retire/` | JWT (G3+) | Retire plan |
| GET | `/api/v1/group/{group_id}/transport/fees/plans/kpis/` | JWT (G3+) | KPI cards |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
