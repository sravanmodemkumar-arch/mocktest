# 02 — Fleet Manager Dashboard

> **URL:** `/group/transport/fleet/`
> **File:** `02-fleet-manager-dashboard.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P0
> **Role:** Group Fleet Manager (Role 80, G3) — exclusive post-login landing

---

## 1. Purpose

Primary post-login landing for the Group Fleet Manager. Complete command centre for vehicle fleet management across all branches — vehicle register, maintenance scheduling, fitness certificates, permits, insurance tracking, and fuel consumption.

The Fleet Manager ensures every vehicle in the group's fleet is roadworthy, legally compliant, and operationally ready. A vehicle with an expired fitness cert or lapsed insurance cannot legally carry students — the Fleet Manager's primary duty is zero-lapse compliance. Large groups operate 200–500 buses; the Fleet Manager must proactively track expiry dates weeks in advance.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Fleet Manager | G3 | Full — all vehicles, all branches | Exclusive dashboard |
| Group Transport Director | G3 | View — fleet summary via own dashboard | Not this URL |
| Group Transport Safety Officer | G3 | Read — vehicle details for safety checks | View only |
| All other transport roles | G3 | — | View own sections only |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Fleet Manager Dashboard
```

### 3.2 Page Header
```
Welcome back, [Manager Name]              [+ Add Vehicle]  [Export Fleet Report ↓]  [Settings ⚙]
Group Fleet Manager · [N] Total Vehicles  ·  AY [current academic year]
Operational: [N]  ·  Under Maintenance: [N]  ·  Compliance Issues: [N]
```

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| Fitness cert expired | "[N] vehicles have expired fitness certificates. Cannot be operated." | Red |
| Insurance expired | "[N] vehicles have expired insurance. Immediate action required." | Red |
| Permit expired | "[N] vehicles have expired route permits." | Red |
| Fitness cert expiring ≤ 7 days | "[N] fitness certificates expire within 7 days." | Amber |
| Insurance expiring ≤ 15 days | "[N] insurance policies expire within 15 days." | Amber |
| Overdue maintenance | "[N] vehicles have overdue scheduled maintenance." | Amber |
| Vehicle breakdown reported | "Breakdown reported: [Bus No] at [Branch]. Replacement dispatched?" | Red |

---

## 4. KPI Summary Bar (8 cards)

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| Total Fleet | All registered vehicles | Blue always | → Page 07 |
| Operational Today | Available and deployed | Green if = Total · Yellow if < 100% | → Page 07 |
| Under Maintenance | In workshop | Yellow > 0 · Red > 5% of fleet | → Page 08 |
| Fitness Compliant | % with valid fitness cert | Green ≥ 98% · Yellow 90–98% · Red < 90% | → Page 09 |
| Insurance Compliant | % with valid insurance | Green ≥ 98% · Yellow 90–98% · Red < 90% | → Page 09 |
| Permit Compliant | % with valid route permit | Green ≥ 98% · Yellow 90–98% · Red < 90% | → Page 09 |
| Scheduled Maintenance Due (7d) | Count needing service in 7 days | Yellow > 5 · Red > 15 | → Page 08 |
| Avg Vehicle Age | Years | Green < 8yr · Yellow 8–12yr · Red > 12yr | → Page 07 |

**HTMX:** `hx-trigger="every 10m"` → KPI auto-refresh.

---

## 5. Sections

### 5.1 Fleet Compliance Summary Table (Branch-wise)

> Per-branch compliance overview — Fleet Manager's primary monitoring view.

**Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Compliance Status | Radio | All / Fully Compliant / Issues Found |
| Vehicle Type | Checkbox | Bus (Full) / Mini Bus / Van |

**Columns:**
| Column | Sortable | Notes |
|---|---|---|
| Branch | ✅ | Link → branch fleet detail drawer |
| Total Vehicles | ✅ | Registered at this branch |
| Operational | ✅ | Available today |
| Fitness OK | ✅ | Count + % |
| Insurance OK | ✅ | Count + % |
| Permit OK | ✅ | Count + % |
| Maintenance Due | ✅ | Count |
| Overall Compliance | ✅ | % colour-coded |
| Actions | ❌ | View · Flag Issue |

**Default sort:** Overall Compliance ascending.
**Pagination:** Server-side · 25/page.

---

### 5.2 Upcoming Expiry Alerts

> All vehicles with fitness cert / permit / insurance expiring within 30 days.

**Columns:** Bus No · Branch · Document Type · Expiry Date · Days Left · Renewal Status · [Action]

Action options: Mark Renewal In Progress · Mark Renewed · Send Reminder to Branch.

"View full compliance dashboard →" → Page 31.

---

### 5.3 Maintenance Queue

> Vehicles with scheduled or overdue maintenance.

**Columns:** Bus No · Branch · Last Service Date · Next Service Due · Mileage · Status · [Schedule →]

"View full maintenance tracker →" → Page 08.

---

### 5.4 Fleet Age Distribution (Chart)

**Chart — Age Distribution (Bar)**
- X-axis: Age brackets (0–3yr / 4–6yr / 7–10yr / 11–15yr / 15yr+)
- Y-axis: Number of vehicles
- Colour: Green < 8yr · Yellow 8–12yr · Red > 12yr

---

## 6. Drawers

### 6.1 Drawer: `vehicle-add`
- **Trigger:** + Add Vehicle
- **Width:** 640px
- **Fields:** Bus Number · Branch · Vehicle Type · Seating Capacity · Manufacturer · Model · Year of Manufacture · RC Number · Engine Number · Chassis Number · Fuel Type · GPS Device ID (optional) · Purchased / Leased · Purchase Date
- **Validation:** RC Number unique · Bus number unique within group

### 6.2 Drawer: `branch-fleet-detail`
- **Width:** 640px
- **Tabs:** Vehicles · Maintenance · Compliance · Incidents
- **Vehicles:** Full list with status, compliance, assignment
- **Maintenance:** Scheduled and completed maintenance history
- **Compliance:** All fitness/permit/insurance expiry dates
- **Incidents:** Breakdown and accident history

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Vehicle added | "[Bus No] added to fleet registry." | Success | 4s |
| Renewal marked | "Fitness certificate renewed for [Bus No]." | Success | 4s |
| Maintenance scheduled | "Maintenance scheduled for [Bus No] on [date]." | Info | 4s |
| Vehicle flagged | "[Bus No] flagged as non-operational. Branch transport head notified." | Warning | 6s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No vehicles registered | "No Fleet Registered" | "Add vehicles to start managing the transport fleet." | [+ Add Vehicle] |
| No compliance issues | "Full Fleet Compliance" | "All vehicles have valid fitness, insurance, and permits." | — |
| No maintenance due | "No Maintenance Due" | "No scheduled maintenance in the next 7 days." | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 8 KPI cards + compliance table + expiry alerts + maintenance queue |
| Table filter | Inline skeleton rows |
| KPI auto-refresh | Shimmer on card values |
| Add vehicle drawer | 640px drawer skeleton |

---

## 10. Role-Based UI Visibility

| Element | Fleet Manager G3 | Transport Director G3 | Safety Officer G3 |
|---|---|---|---|
| Add Vehicle | ✅ | ✅ (approve) | ❌ |
| Edit Vehicle Details | ✅ | ❌ | ❌ |
| Mark Vehicle Non-Operational | ✅ | ✅ | ❌ |
| Schedule Maintenance | ✅ | ❌ | ❌ |
| Mark Renewal | ✅ | ❌ | ❌ |
| View All Vehicles | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/fleet/dashboard/` | JWT (G3+) | Dashboard data |
| GET | `/api/v1/group/{group_id}/transport/fleet/kpi-cards/` | JWT (G3+) | KPI auto-refresh |
| GET | `/api/v1/group/{group_id}/transport/fleet/compliance-summary/` | JWT (G3+) | Branch-wise compliance table |
| GET | `/api/v1/group/{group_id}/transport/fleet/expiry-alerts/` | JWT (G3+) | Expiry alerts within 30 days |
| GET | `/api/v1/group/{group_id}/transport/fleet/maintenance-queue/` | JWT (G3+) | Maintenance due list |
| POST | `/api/v1/group/{group_id}/transport/fleet/vehicles/` | JWT (G3+) | Add vehicle |
| GET | `/api/v1/group/{group_id}/transport/fleet/branches/{id}/detail/` | JWT (G3+) | Branch fleet drawer |
| GET | `/api/v1/group/{group_id}/transport/fleet/age-distribution/` | JWT (G3+) | Age chart data |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-get/post | hx-target | hx-swap |
|---|---|---|---|---|
| KPI auto-refresh | `every 10m` | GET `.../fleet/kpi-cards/` | `#kpi-bar` | `innerHTML` |
| Compliance table filter | `click` | GET `.../fleet/compliance-summary/?{filters}` | `#compliance-table-section` | `innerHTML` |
| Open branch drawer | `click` | GET `.../fleet/branches/{id}/detail/` | `#drawer-body` | `innerHTML` |
| Add vehicle submit | `click` | POST `.../fleet/vehicles/` | `#fleet-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
