# 01 — Sports Director Dashboard

> **URL:** `/group/sports/director/`
> **File:** `01-sports-director-dashboard.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P0
> **Role:** Group Sports Director (Role 97, G3) — exclusive post-login landing

---

## 1. Purpose

Primary post-login landing for the Group Sports Director. Command centre for sports program oversight across all branches — active tournaments, branches without any sports program, state team nominations pending, coach vacancies, and policy compliance. The Sports Director sets group-wide sports policy, approves inter-branch tournament proposals, nominates students to state and national teams, and ensures every branch runs at least a minimum sports calendar.

Scale: 20–50 branches · 8–20 teams per branch per sport type · 5–15 inter-branch tournaments per year · 100–500 student athletes nominated for external events.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Sports Director | G3 | Full — all sections, all actions | Exclusive dashboard |
| Group Sports Coordinator | G3 | — | Has own dashboard `/group/sports/coordinator/` |
| Group Cultural Activities Head | G3 | — | Separate domain |
| Group Chairman / CEO | G5 / G4 | View sports analytics via Governance Reports | Not this URL |
| All other roles | — | — | Redirected to own dashboard |

> **Access enforcement:** Django view decorator `@require_role('sports_director')`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Sports Director Dashboard
```

### 3.2 Page Header
```
Welcome back, [Director Name]                    [+ New Tournament]  [Export Sports Report ↓]
[Group Name] — Group Sports Director · Last login: [date time]
AY [current academic year]  ·  [N] Branches  ·  [N] Active Tournaments  ·  [N] Teams Registered
```

### 3.3 Alert Banner (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| Branch with zero sports participation this term | "[N] branch(es) have no registered sports teams this term: [list]. Action required." | Red |
| State nomination deadline approaching | "State sports nomination deadline is [date] — [N] students pending Medical Fitness Certificate." | Amber |
| Tournament without assigned coordinator | "[N] upcoming tournament(s) have no assigned coordinator." | Amber |
| Coach vacancy >30 days | "[N] coaching vacancies open for >30 days at branches: [list]." | Amber |

---

## 4. KPI Summary Bar (7 cards)

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| Branches with Active Sports | Branches with ≥1 registered team this term / total | Green = all · Yellow = 1–3 missing · Red = 4+ missing | → Sports Team Registry page 08 |
| Active Tournaments | Count of tournaments in Upcoming / Ongoing status | Blue always | → Tournament Manager page 07 |
| Total Registered Athletes | Students enrolled in at least one sport group-wide | Blue always | → Sports Team Registry page 08 |
| Tournaments Pending Approval | Tournament proposals submitted from branches awaiting Director approval | Red if > 0 | → Section 5.1 |
| State / National Nominations | Students nominated for state/national team this AY | Blue always | → Achievement Register page 19 |
| Coach Vacancies | Branches with unfilled coaching positions | Green = 0 · Yellow 1–3 · Red > 3 | → Coach Registry page 09 |
| Upcoming Events (30d) | Sports events across all branches in next 30 days | Blue always | → Sports Calendar page 06 |

**HTMX:** `hx-trigger="every 5m"` `hx-get="/api/v1/group/{id}/sports/director/kpi/"` `hx-target="#kpi-bar"` `hx-swap="innerHTML"`.

---

## 5. Sections

### 5.1 Tournament Approval Queue

> Branches submit tournament proposals — Sports Director reviews and approves.

**Display:** Table — up to 8 rows, "View All →" link to page 07.

**Search:** Tournament name, branch, sport. Debounce 300ms.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Tournament Name | Text | ✅ | e.g. "Inter-Branch Football Cup 2026" |
| Sport | Badge | ✅ | Football · Cricket · Volleyball · etc. |
| Proposed By | Text | ✅ | Branch name |
| Proposed Dates | Date range | ✅ | Start – End |
| Venue | Text | ❌ | Branch or neutral venue |
| Teams Expected | Number | ✅ | Estimated participating branches |
| Submitted On | Date | ✅ | |
| Days Pending | Number | ✅ | Red if > 7 |
| Actions | — | ❌ | [Approve] [Reject] [View Details] |

**[Approve]:** `hx-post` → success toast · row removed · branch notified.
**[Reject]:** 420px modal — required reason (min 20 chars) · communicated to submitting branch.
**[View Details]:** Opens `tournament-detail` drawer in view mode with [Approve] / [Reject] in Action tab.

**Default sort:** Days Pending descending.

---

### 5.2 Branch Sports Program Status

> Quick view of which branches are active vs inactive in sports this term.

**Search:** Branch name, city. Debounce 300ms.

**Filters:** State, Type (Day/Hostel), Status (Active/No Teams/Onboarding).

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Branch | Text + link | ✅ | → Branch Detail |
| City | Text | ✅ | |
| Teams Registered | Number | ✅ | Green ≥ 5 · Yellow 1–4 · Red = 0 |
| Total Athletes | Number | ✅ | Students in at least one team |
| Sports Offered | Tags | ❌ | Cricket, Football, etc. |
| Last Tournament | Date | ✅ | Red if > 180 days ago |
| Coach Coverage | Badge | ✅ | Full · Partial · No Coach |
| Actions | — | ❌ | View Teams · View Calendar |

**Default sort:** Teams Registered ascending (branches with fewest first).

**Pagination:** Server-side · Default 25/page.

---

### 5.3 Upcoming Tournaments (next 60 days — approved)

**Display:** Card list — max 6, grouped by sport, "View Full Calendar →" link.

**Card fields:** Tournament name · Sport badge · Dates · Venue · Registered teams count / total invited · Status (Registration Open / Closed / Ongoing).

---

### 5.4 State / National Nominations Tracker

> Students nominated this academic year for state or national-level representation.

**Display:** Compact table — max 10 rows, "View All in Achievement Register →" link.

**Columns:** Student Name · Branch · Class · Sport · Level (State/National/International) · Nomination Date · Medical Certificate (✅/❌) · Outcome (Pending/Selected/Not Selected).

**Default sort:** Nomination Date descending.

---

### 5.5 Quick Links

| Tile | Link |
|---|---|
| Sports Event Calendar | page 06 |
| Tournament Manager | page 07 |
| Sports Team Registry | page 08 |
| Coach & Staff Registry | page 09 |
| Student Achievement Register | page 19 |
| Extra-Curricular Analytics | page 20 |

---

## 6. Drawers & Modals

### 6.1 Drawer: `tournament-detail` (from approval queue)
- **Width:** 680px
- **Tabs:** Overview · Teams · Schedule · Venue · Action
- **Overview:** Tournament name, sport, proposed dates, format (knockout/league/combined)
- **Teams:** Branches invited, confirmed registrations
- **Schedule:** Proposed fixture schedule (if submitted)
- **Venue:** Address, facilities checklist, seating capacity
- **Action tab (Director only):** [Approve Tournament] (green) · [Reject with Reason] (red) · [Request Modification] (amber) — opens inline reason field

### 6.2 Modal: `tournament-reject`
- **Width:** 420px
- **Fields:** Reason (required, min 20 chars, 400 char limit with counter)
- **Buttons:** [Reject Tournament] (danger) + [Cancel]

---

## 7. Charts

### 7.1 Sports Participation Trend (last 3 Academic Years)
- **Type:** Grouped bar chart
- **Data:** Total registered athletes per AY (Day Scholars vs Hostelers)
- **X-axis:** Academic years
- **Y-axis:** Student count
- **Tooltip:** AY · Day Scholar athletes: N · Hosteler athletes: N · Total: N
- **Export:** PNG

### 7.2 Sport-wise Team Distribution (current AY)
- **Type:** Horizontal bar chart
- **Data:** Number of teams registered per sport across all branches
- **X-axis:** Team count
- **Y-axis:** Sport names
- **Colour:** Single colour, sorted descending
- **Export:** PNG

---

## 8. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Tournament approved | "Tournament approved. Branch notified." | Success | 4s |
| Tournament rejected | "Tournament proposal rejected. Reason sent to branch." | Success | 4s |
| Export started | "Sports report generating… download will start shortly" | Info | 4s |
| KPI load error | "Failed to refresh KPI data." | Error | Manual |

---

## 9. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No tournament proposals | "No tournament proposals pending" | "Branches haven't submitted any tournament proposals yet" | — |
| No branches with teams (new group) | "No sports teams registered" | "Start by adding teams in the Sports Team Registry" | [Go to Team Registry] |
| No nominations this year | "No state nominations yet" | "Student nominations for state/national teams will appear here" | — |

---

## 10. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: 7 KPI cards + approval table (5 rows) + branch table (5 rows) + charts |
| Approval table filter/search | Inline skeleton rows |
| Approve / Reject action | Spinner in button + disabled |
| Chart data load | Spinner centred in chart area |
| KPI auto-refresh | Shimmer on card values |

---

## 11. Role-Based UI Visibility

| Element | Sports Director G3 | All others |
|---|---|---|
| Page | ✅ | ❌ Redirected |
| [Approve] / [Reject] in approval queue | ✅ | N/A |
| [+ New Tournament] header button | ✅ | N/A |
| [Export Sports Report] | ✅ | N/A |
| State nominations table (write) | ✅ | N/A |

> All write controls rendered server-side. G1/G2 visiting any sports page see read-only views.

---

## 12. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/sports/director/dashboard/` | JWT (G3 Director) | Full dashboard data |
| GET | `/api/v1/group/{id}/sports/director/kpi/` | JWT (G3) | KPI cards (auto-refresh) |
| GET | `/api/v1/group/{id}/sports/tournaments/?status=pending_approval` | JWT (G3) | Tournament approval queue |
| POST | `/api/v1/group/{id}/sports/tournaments/{tid}/approve/` | JWT (G3 Director) | Approve tournament |
| POST | `/api/v1/group/{id}/sports/tournaments/{tid}/reject/` | JWT (G3 Director) | Reject with reason |
| GET | `/api/v1/group/{id}/sports/branches/status/` | JWT (G3) | Branch sports program status |
| GET | `/api/v1/group/{id}/sports/tournaments/?status=upcoming&days=60` | JWT (G3) | Upcoming tournaments |
| GET | `/api/v1/group/{id}/sports/nominations/` | JWT (G3) | State/national nominations |
| GET | `/api/v1/group/{id}/sports/analytics/participation-trend/` | JWT (G3) | Participation trend chart |
| GET | `/api/v1/group/{id}/sports/analytics/sport-distribution/` | JWT (G3) | Sport-wise team distribution |

---

## 13. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Approval queue search | `input delay:300ms` | GET `.../tournaments/?status=pending&q=` | `#approval-table-body` | `innerHTML` |
| Branch table filter | `click` | GET `.../sports/branches/status/?filters=` | `#branch-table-section` | `innerHTML` |
| Approve tournament | `click` | POST `.../tournaments/{id}/approve/` | `#approval-row-{id}` | `outerHTML` |
| Open tournament detail drawer | `click` | GET `.../tournaments/{id}/` | `#drawer-body` | `innerHTML` |
| KPI auto-refresh | `every 5m` | GET `.../sports/director/kpi/` | `#kpi-bar` | `innerHTML` |
| Branch table pagination | `click` | GET `.../sports/branches/status/?page=` | `#branch-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
