# 02 — Sports Coordinator Dashboard

> **URL:** `/group/sports/coordinator/`
> **File:** `02-sports-coordinator-dashboard.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P0
> **Role:** Group Sports Coordinator (Role 98, G3) — exclusive post-login landing

---

## 1. Purpose

Primary post-login landing for the Group Sports Coordinator. The Coordinator is the operational backbone of the group's sports program — managing coaches, tracking equipment inventory across branches, maintaining the sports calendar, and ensuring upcoming events are fully resourced. Where the Sports Director sets policy and approves tournaments, the Coordinator executes day-to-day operations.

Core responsibilities surfaced here:
- Coach assignment gaps (branches needing a coach for a specific sport)
- Equipment requests pending procurement approval
- Sports calendar — upcoming events requiring logistics action
- Team roster health (teams without minimum player count)

Scale: 20–50 branches · 3–8 coaches per branch · 200–500 equipment requests per year.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Sports Coordinator | G3 | Full — all sections, all actions | Exclusive dashboard |
| Group Sports Director | G3 | — | Has own dashboard `/group/sports/director/` |
| All others | — | — | Redirected |

> **Access enforcement:** `@require_role('sports_coordinator')`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Sports Coordinator Dashboard
```

### 3.2 Page Header
```
Welcome back, [Coordinator Name]                 [+ Add Coach]  [+ Log Equipment Request]
[Group Name] — Sports Coordinator · Last login: [date time]
AY [current academic year]  ·  [N] Coaches Active  ·  [N] Equipment Requests Pending
```

### 3.3 Alert Banner (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| Branch with no coach in any sport | "[N] branch(es) have no assigned coach: [list]." | Red |
| Equipment request overdue > 14 days | "[N] equipment requests have been pending for over 14 days." | Amber |
| Team with < minimum player count | "[N] team(s) are below minimum player requirement and cannot participate in upcoming tournament." | Amber |
| Upcoming tournament < 7 days, logistics incomplete | "[Tournament Name] starts in [N] days — venue confirmation and fixture sheet not finalized." | Amber |

---

## 4. KPI Summary Bar (6 cards)

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| Coaches Active | Active coaches group-wide | Blue always | → Coach Registry page 09 |
| Coach Vacancy Rate | Branches with at least one coaching gap / total | Green = 0% · Yellow > 0% · Red > 10% | → Coach Registry page 09 |
| Equipment Requests Pending | Open requests not yet procured | Green = 0 · Yellow 1–5 · Red > 5 | → Equipment Inventory page 10 |
| Events This Month | Sports events in current calendar month | Blue always | → Sports Calendar page 06 |
| Teams Below Min Roster | Teams with fewer than required player count | Green = 0 · Red > 0 | → Sports Team Registry page 08 |
| Tournament This Week | Tournaments actively running or starting within 7 days | Blue (info) — pulsing if > 0 | → Tournament Manager page 07 |

**HTMX:** `hx-trigger="every 5m"` `hx-get="/api/v1/group/{id}/sports/coordinator/kpi/"` `hx-target="#kpi-bar"` `hx-swap="innerHTML"`.

---

## 5. Sections

### 5.1 Coach Coverage Gap Table

> Branches and sports where no coach is currently assigned.

**Display:** Table — all gaps across group.

**Search:** Branch name, sport. Debounce 300ms.

**Filters:** Branch, Sport, Gap duration (>7d / >14d / >30d).

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Branch | Text + link | ✅ | |
| Sport | Badge | ✅ | Football · Cricket · etc. |
| Gap Since | Date | ✅ | When last coach left or role was created |
| Days Vacant | Number | ✅ | Red if > 30 |
| Teams Affected | Number | ✅ | Teams with no coach |
| Actions | — | ❌ | [Assign Coach] [View Coaches] |

**[Assign Coach]:** Opens `coach-detail` drawer pre-filtered to available coaches for that sport → can assign directly.

**Default sort:** Days Vacant descending.

**Pagination:** 25/page.

---

### 5.2 Equipment Request Queue

> Pending equipment requests from branch sports staff.

**Display:** Table — max 10 rows, "View All →" to page 10.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Request ID | Text | ✅ | e.g. EQ-2026-042 |
| Branch | Text | ✅ | |
| Sport | Badge | ✅ | |
| Item Requested | Text | ✅ | e.g. "Cricket Batting Gloves" |
| Quantity | Number | ✅ | |
| Est. Cost ₹ | Currency | ✅ | |
| Requested By | Text | ❌ | Branch sports teacher name |
| Days Pending | Number | ✅ | Red if > 14 |
| Status | Badge | ✅ | Pending · Approved · Ordered · Delivered |
| Actions | — | ❌ | [Approve] [Reject] [View] |

**[Approve]:** Confirm modal (420px) — cost shown prominently.
**[Reject]:** Reason modal (420px) — min 20 chars.

**Default sort:** Days Pending descending.

---

### 5.3 Sports Calendar — This Week + Next Week

**Display:** 2-week horizontal calendar grid (Mon–Sun × 2 rows).

**Events shown:** Matches · Practice fixtures · Tournament days · Sports Day · External competitions.

**Event colours:** Tournament (blue) · Practice (grey) · Sports Day (green) · External (orange).

**Click event:** Opens event detail.

**[+ Add Event] button:** Opens `sports-event-create` form (within sports calendar page 06).

**"View Full Calendar →"** link to page 06.

---

### 5.4 Upcoming Tournament — Logistics Checklist

> For the next upcoming tournament — coordinator's pre-tournament checklist.

**Display:** Single card (if tournament exists in next 14 days) with inline checklist.

**Card header:** Tournament name · Sport · Date · Venue · Registered teams count.

**Checklist items:**
- [ ] Venue booking confirmed
- [ ] Fixture schedule published
- [ ] Referees / umpires assigned
- [ ] First aid arrangement confirmed
- [ ] Transport for visiting teams arranged
- [ ] Trophies / medals ordered
- [ ] Branch principals notified

**Each item:** Toggle (Coordinator can check off) · Updated at timestamp.

**"View Tournament Details →"** link to page 07.

---

## 6. Drawers & Modals

### 6.1 Modal: `equipment-approve`
- **Width:** 420px
- **Content:** "Approve request for [item] × [quantity] from [Branch]? Estimated cost: ₹[amount]"
- **Optional note:** Textarea
- **Buttons:** [Approve] (primary) + [Cancel]

### 6.2 Modal: `equipment-reject`
- **Width:** 420px
- **Fields:** Reason (required, min 20 chars)
- **Buttons:** [Reject] (danger) + [Cancel]

### 6.3 Drawer: `coach-assign` (from gap table)
- **Width:** 560px
- **Context:** Branch + Sport pre-filled
- **Content:** List of available coaches — name, qualifications, current assignments, sport specializations
- **[Assign] button:** Per row — opens confirm modal (380px) → on confirm: coach assigned, branch notified

---

## 7. Charts

### 7.1 Equipment Request Volume (last 6 months)
- **Type:** Bar chart
- **Data:** Monthly equipment requests received vs resolved
- **X-axis:** Last 6 months
- **Y-axis:** Request count
- **Colours:** Blue (received) · Green (resolved)
- **Tooltip:** Month · Received: N · Resolved: N · Pending: N
- **Export:** PNG

### 7.2 Coach Coverage by Branch
- **Type:** Horizontal bar chart
- **Data:** Coach count per branch (sorted ascending)
- **X-axis:** Coach count
- **Y-axis:** Branch names
- **Benchmark line:** Minimum required coaches (configurable, default 3)
- **Colour:** Red if below minimum, green otherwise
- **Export:** PNG

---

## 8. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Equipment approved | "Equipment request [ID] approved. Branch notified." | Success | 4s |
| Equipment rejected | "Equipment request rejected. Branch notified with reason." | Success | 4s |
| Coach assigned | "[Coach Name] assigned to [Branch] — [Sport]." | Success | 4s |
| Checklist item saved | "Checklist updated" | Info | 3s |
| API error | "Failed to load data. Refresh the page." | Error | Manual |

---

## 9. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No coach gaps | "All coaching positions filled" | "Every branch has a coach for all active sports" | — |
| No pending equipment requests | "No equipment requests pending" | "Equipment requests from branches will appear here" | — |
| No events this week | "No sports events this week" | "Add events to the sports calendar" | [Go to Calendar] |
| No upcoming tournament | "No tournament in next 14 days" | "Next tournament logistics checklist will appear here when one is scheduled" | — |

---

## 10. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: 6 KPI cards + gap table (5 rows) + equipment table (5 rows) + calendar grid |
| Table filter/search | Inline skeleton rows |
| Equipment approve / reject | Spinner in button + disabled |
| Coach assign confirm | Spinner in confirm button |
| KPI auto-refresh | Shimmer on card values |

---

## 11. Role-Based UI Visibility

| Element | Sports Coordinator G3 | Others |
|---|---|---|
| Page | ✅ | ❌ Redirected |
| [Approve] / [Reject] equipment | ✅ | N/A |
| [Assign Coach] in gap table | ✅ | N/A |
| [+ Add Coach] header button | ✅ | N/A |
| Tournament checklist toggle | ✅ | N/A |
| [+ Log Equipment Request] | ✅ | N/A |

---

## 12. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/sports/coordinator/dashboard/` | JWT (G3 Coord) | Full dashboard data |
| GET | `/api/v1/group/{id}/sports/coordinator/kpi/` | JWT (G3) | KPI auto-refresh |
| GET | `/api/v1/group/{id}/sports/coaches/gaps/` | JWT (G3) | Coach coverage gaps |
| POST | `/api/v1/group/{id}/sports/coaches/{cid}/assign/` | JWT (G3) | Assign coach to branch+sport |
| GET | `/api/v1/group/{id}/sports/equipment/?status=pending` | JWT (G3) | Equipment requests queue |
| POST | `/api/v1/group/{id}/sports/equipment/{eid}/approve/` | JWT (G3) | Approve equipment request |
| POST | `/api/v1/group/{id}/sports/equipment/{eid}/reject/` | JWT (G3) | Reject with reason |
| GET | `/api/v1/group/{id}/sports/calendar/?range=2weeks` | JWT (G3) | 2-week calendar events |
| PATCH | `/api/v1/group/{id}/sports/tournaments/{tid}/logistics/{item}/` | JWT (G3) | Toggle logistics checklist item |
| GET | `/api/v1/group/{id}/sports/analytics/equipment-trend/` | JWT (G3) | Equipment request volume chart |
| GET | `/api/v1/group/{id}/sports/analytics/coach-coverage/` | JWT (G3) | Coach coverage by branch chart |

---

## 13. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Coach gap table search | `input delay:300ms` | GET `.../coaches/gaps/?q=` | `#gap-table-body` | `innerHTML` |
| Equipment queue filter | `click` | GET `.../equipment/?status=pending&filters=` | `#equipment-table-section` | `innerHTML` |
| Approve equipment | `click` | POST `.../equipment/{id}/approve/` | `#eq-row-{id}` | `outerHTML` |
| Logistics checklist toggle | `change` | PATCH `.../tournaments/{tid}/logistics/{item}/` | `#checklist-item-{item}` | `outerHTML` |
| KPI auto-refresh | `every 5m` | GET `.../coordinator/kpi/` | `#kpi-bar` | `innerHTML` |
| Open coach assign drawer | `click` | GET `.../coaches/?sport={s}&available=true` | `#drawer-body` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
