# 04 — NSS / NCC Coordinator Dashboard

> **URL:** `/group/nss/coordinator/`
> **File:** `04-nss-ncc-coordinator-dashboard.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P0
> **Role:** Group NSS / NCC Coordinator (Role 100, G3) — exclusive post-login landing

---

## 1. Purpose

Primary post-login landing for the Group NSS/NCC Coordinator. Manages National Service Scheme (NSS) and National Cadet Corps (NCC) programs across all branches, plus civic education and social outreach activities.

**NSS:** Each branch must maintain a registered NSS unit with a Programme Officer. Each NSS student must complete 240 hours of service annually. Annual Special Camps are mandatory once per year per unit. The Coordinator tracks unit registration status, enrolment numbers, activity hours, and special camp completion.

**NCC:** Each branch with NCC must have an Associated NCC Officer (ANO). Cadets earn A, B, and C certificates through annual camps. The Coordinator tracks cadet enrolment, camp registrations, certificate achievement, and officer appointments.

**Civic Programmes:** Community service drives, blood donation camps, literacy programs, environment campaigns — logged as civic activity records.

Scale: 20–50 branches · NSS units in 60–80% of branches · NCC units in 30–50% of branches · 1,000–8,000 NSS students · 300–3,000 NCC cadets.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group NSS/NCC Coordinator | G3 | Full — all sections, all actions | Exclusive dashboard |
| Group Cultural Activities Head | G3 | View civic events calendar only | No NSS/NCC data |
| Group Chairman / CEO | G5 / G4 | View via Governance Reports | Not this URL |
| All others | — | — | Redirected |

> **Access enforcement:** `@require_role('nss_ncc_coordinator')`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  NSS / NCC Coordinator Dashboard
```

### 3.2 Page Header
```
Welcome back, [Coordinator Name]                 [+ Log Activity]  [Export NSS/NCC Report ↓]
[Group Name] — NSS/NCC Coordinator · Last login: [date time]
AY [current academic year]  ·  [N] NSS Units  ·  [N] NCC Units  ·  [N] Special Camps Completed
```

### 3.3 Alert Banner (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| NSS unit not registered at eligible branch | "[N] branch(es) eligible for NSS unit have not registered one this AY." | Red |
| Annual Special Camp not completed | "[N] NSS unit(s) have not completed the mandatory Annual Special Camp." | Red |
| ANO vacancy at NCC branch | "[N] NCC unit(s) have no Associated NCC Officer assigned." | Amber |
| Students below 200 hours with AY ending < 60 days | "[N] NSS students are below 200 hours with less than 60 days to AY end." | Amber |

---

## 4. KPI Summary Bar (8 cards)

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| NSS Units Active | Branches with a registered, active NSS unit this AY | Blue always | → NSS Programme Tracker page 14 |
| Total NSS Students | Students enrolled in NSS across all branches | Blue always | → NSS Programme Tracker page 14 |
| NSS Hours Completed (Avg) | Average hours per enrolled NSS student this AY | Green ≥ 180hrs · Yellow 120–180 · Red < 120 | → NSS Programme Tracker page 14 |
| Annual Special Camps Done | NSS units with mandatory special camp completed | Green = all units · Red if any missing | → NSS Programme Tracker page 14 |
| NCC Units Active | Branches with an active NCC unit | Blue always | → NCC Camp Register page 15 |
| Total NCC Cadets | Cadets enrolled in NCC across all branches | Blue always | → NCC Camp Register page 15 |
| Upcoming Camps (30d) | NSS special camps + NCC annual camps within 30 days | Blue always | → Section 5.3 |
| Civic Programmes (AY) | Total civic activity programmes conducted this year | Blue always | → Civic Programme Register page 16 |

**HTMX:** `hx-trigger="every 5m"` `hx-get="/api/v1/group/{id}/nss/coordinator/kpi/"` `hx-target="#kpi-bar"` `hx-swap="innerHTML"`.

---

## 5. Sections

### 5.1 NSS Unit Status Table

> All NSS units across branches — enrolment, hours, special camp status.

**Search:** Branch name, Programme Officer name. Debounce 300ms.

**Filters:** State, Camp Completed (Yes/No), Hours Status (On Track / At Risk / Critical).

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Branch | Text + link | ✅ | |
| NSS Unit No. | Text | ✅ | University registration number |
| Programme Officer | Text | ✅ | Red "Vacant" if no PO assigned |
| Students Enrolled | Number | ✅ | |
| Avg Hours Completed | Number + bar | ✅ | Of 240-hour target. Colour-coded |
| Special Camp | Badge | ✅ | ✅ Done · ❌ Pending · 📅 Scheduled |
| Regular Activities (this AY) | Number | ✅ | Count of logged activities |
| Actions | — | ❌ | View · Log Activity · Schedule Camp |

**Default sort:** Avg Hours Completed ascending (lowest hours first).

**Pagination:** 25/page.

---

### 5.2 NCC Unit Status Table

> All NCC units across branches — cadet count, ANO, certificate progress.

**Search:** Branch name, ANO name. Debounce 300ms.

**Filters:** State, Wing (Army/Navy/Air Force), Certificate Level Focus.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Branch | Text + link | ✅ | |
| NCC Unit | Text | ✅ | e.g. "3 AP BN NCC" |
| Wing | Badge | ✅ | Army · Navy · Air Force |
| ANO (Assoc. NCC Officer) | Text | ✅ | Red "Vacant" if not assigned |
| Total Cadets | Number | ✅ | |
| 'A' Cert Holders | Number | ✅ | |
| 'B' Cert Holders | Number | ✅ | |
| 'C' Cert Holders | Number | ✅ | |
| Upcoming Camp | Date | ✅ | "None" if not scheduled |
| Actions | — | ❌ | View · Register Camp |

**Default sort:** Branch name ascending.

**Pagination:** 25/page.

---

### 5.3 Upcoming Camps (next 60 days)

**Display:** Card list (max 6) — sorted by date ascending, "View All →" to pages 14 & 15.

**Card fields:** Camp name · Type badge (NSS Special / NCC Annual / NCC Combined) · Branch / Location · Dates · Cadets/Students Registered · Status (Planned/Registration Open/Confirmed).

---

### 5.4 Recent Civic Activities

**Display:** Compact table — last 10 activities, "View All →" to page 16.

**Columns:** Date · Activity Type · Branch · Students Participated · Description (truncated) · Verified?.

---

## 6. Drawers & Modals

### 6.1 Drawer: `nss-activity-log`
- **Trigger:** [+ Log Activity] header button or NSS table → Log Activity
- **Width:** 480px
- **Tabs:** Activity · Date · Hours · Students
- **Fields:**
  | Field | Type | Required | Validation |
  |---|---|---|---|
  | Branch | Select | ✅ | |
  | NSS Unit | Auto-filled | — | Based on branch |
  | Activity Type | Select | ✅ | Regular Activity · Special Camp Day · Community Service · Awareness Drive · Blood Donation · Environmental · Literary |
  | Activity Date | Date | ✅ | Cannot be future |
  | Duration (hours) | Number | ✅ | 1–8 hours per day |
  | Students Present | Number | ✅ | ≤ enrolled count |
  | Activity Description | Textarea | ✅ | Min 20 chars, 500 max |
  | Attendance Sheet | File upload | ❌ | PDF/JPG, max 5MB |
  | Programme Officer Signature | Toggle | ✅ | Checkbox confirming PO verified |

- **On submit:** Hours credited to participating students; activity appears in branch NSS log.

### 6.2 Drawer: `ncc-camp-create` (see also page 15)
- **Width:** 560px
- **Tabs:** Camp · Cadets · Dates · Officers
- **Camp tab:** Camp name, type (Annual Training / Combined Annual · Thal Sainik · Vayu Sainik), NCC directorate, unit
- **Cadets tab:** Multi-select cadets from enrolled list + import from CSV
- **Dates tab:** Start date, end date, reporting time, release date
- **Officers tab:** ANO assigned, camp commandant, medical officer (name + contact)

### 6.3 Modal: `schedule-special-camp`
- **Width:** 480px
- **Fields:** Branch (pre-filled), Proposed dates (date range), Location (text), Estimated students (number), Programme Officer (select from branch staff)
- **Buttons:** [Schedule Camp] + [Cancel]

---

## 7. Charts

### 7.1 NSS Hours Completion Distribution (current AY)
- **Type:** Histogram / bar chart
- **Data:** Count of NSS students grouped by hours-completed buckets (0–60, 61–120, 121–180, 181–240, 240+)
- **X-axis:** Hours bucket
- **Y-axis:** Student count
- **Benchmark line:** 240 (target)
- **Colours:** Red (0–60) · Orange (61–120) · Yellow (121–180) · Green (181–240) · Dark green (240+)
- **Export:** PNG

### 7.2 NCC Certificate Progress by Branch (current AY)
- **Type:** Stacked horizontal bar chart
- **Data:** Per branch — cadets at A / B / C certificate levels
- **X-axis:** Cadet count
- **Y-axis:** Branch names (NCC branches only)
- **Colours:** A=Blue · B=Green · C=Gold
- **Export:** PNG

---

## 8. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Activity logged | "NSS activity logged. Hours credited to [N] students." | Success | 4s |
| Camp scheduled | "NSS Special Camp scheduled for [Branch] on [date]." | Success | 4s |
| NCC camp created | "NCC camp [Name] created." | Success | 4s |
| Export started | "NSS/NCC report generating…" | Info | 4s |
| API error | "Failed to load data." | Error | Manual |

---

## 9. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No NSS units registered | "No NSS units found" | "No branches have registered NSS units for this academic year" | — |
| No NCC units registered | "No NCC units found" | "No branches have active NCC units this year" | — |
| No upcoming camps | "No camps in next 60 days" | "No NSS or NCC camps are scheduled in the next 60 days" | [Schedule Camp] |
| No civic activities | "No civic activities logged" | "Log your first civic programme activity" | [+ Log Activity] |

---

## 10. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: 8 KPI cards + NSS table (5 rows) + NCC table (5 rows) + charts |
| Table search/filter | Inline skeleton rows |
| Activity log submit | Spinner in submit button |
| KPI auto-refresh | Shimmer on card values |

---

## 11. Role-Based UI Visibility

| Element | NSS/NCC Coordinator G3 | Others |
|---|---|---|
| Page | ✅ | ❌ Redirected |
| [+ Log Activity] header button | ✅ | N/A |
| [Log Activity] per NSS row | ✅ | N/A |
| [Register Camp] per NCC row | ✅ | N/A |
| [Schedule Camp] per NSS row | ✅ | N/A |
| [Export NSS/NCC Report] | ✅ | N/A |

---

## 12. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/nss/coordinator/dashboard/` | JWT (G3 NSS) | Full dashboard |
| GET | `/api/v1/group/{id}/nss/coordinator/kpi/` | JWT (G3) | KPI auto-refresh |
| GET | `/api/v1/group/{id}/nss/units/` | JWT (G3) | NSS unit status table |
| GET | `/api/v1/group/{id}/nss/ncc/units/` | JWT (G3) | NCC unit status table |
| GET | `/api/v1/group/{id}/nss/camps/?days=60&upcoming=true` | JWT (G3) | Upcoming camps |
| POST | `/api/v1/group/{id}/nss/activities/` | JWT (G3) | Log NSS activity |
| POST | `/api/v1/group/{id}/nss/ncc/camps/` | JWT (G3) | Create NCC camp |
| POST | `/api/v1/group/{id}/nss/units/{uid}/camps/` | JWT (G3) | Schedule NSS special camp |
| GET | `/api/v1/group/{id}/nss/activities/recent/` | JWT (G3) | Recent civic activities |
| GET | `/api/v1/group/{id}/nss/analytics/hours-distribution/` | JWT (G3) | Hours completion histogram |
| GET | `/api/v1/group/{id}/nss/analytics/ncc-certificates/` | JWT (G3) | NCC certificate progress chart |

---

## 13. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| NSS table search | `input delay:300ms` | GET `.../nss/units/?q=` | `#nss-table-body` | `innerHTML` |
| NCC table filter | `click` | GET `.../nss/ncc/units/?filters=` | `#ncc-table-section` | `innerHTML` |
| Open activity log drawer | `click` | GET `.../nss/activities/new-form/` | `#drawer-body` | `innerHTML` |
| Submit activity log | `submit` | POST `.../nss/activities/` | `#drawer-body` | `innerHTML` |
| KPI auto-refresh | `every 5m` | GET `.../nss/coordinator/kpi/` | `#kpi-bar` | `innerHTML` |
| NSS table pagination | `click` | GET `.../nss/units/?page=` | `#nss-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
