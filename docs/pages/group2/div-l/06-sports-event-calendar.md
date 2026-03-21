# 06 — Sports Event Calendar

> **URL:** `/group/sports/calendar/`
> **File:** `06-sports-event-calendar.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P1
> **Roles:** Sports Director G3 (full) · Sports Coordinator G3 (full) · Cultural Head G3 (view) · Chairman/CEO G5/G4 (view via governance)

---

## 1. Purpose

Central calendar of all sports events across all branches — inter-branch tournaments, sports days, practice fixtures, external competitions, and state/national events. Provides a group-wide visual overview to prevent scheduling conflicts, identify overloaded weeks, and allow the Sports Coordinator to manage logistics for upcoming events.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Sports Director | G3 | Full — create, edit, delete events | Approve tournaments from here |
| Sports Coordinator | G3 | Full — create, edit events; manage logistics | Day-to-day operations |
| Cultural Head | G3 | View — shared calendar to avoid clashes | No sports write access |
| Group CEO / Chairman | G4/G5 | View via links from dashboards | Not primary audience |
| Branch Staff | Branch G2 | View events for their branch only | Branch-scoped view |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Sports Event Calendar
```

### 3.2 Page Header
```
Sports Event Calendar                              [+ Add Event]  [Export Calendar ↓]
AY [academic year]  ·  [N] events scheduled  ·  Showing: [Month/Week/List] view
```

### 3.3 View Switcher
- **Month** (default) · **Week** · **List** — tabs at top right of calendar area.
- Active view persisted in URL parameter: `?view=month|week|list`.

---

## 4. Calendar Views

### 4.1 Month View
- Standard month grid (Mon–Sun headers)
- Events shown as coloured tags within date cells (max 3 visible per cell + "+N more" overflow link)
- Overflow click: Opens popover listing all events for that day

**Event colours by type:**
| Event Type | Colour |
|---|---|
| Inter-Branch Tournament | Blue |
| Sports Day | Green |
| External Competition | Orange |
| Practice Fixture | Grey |
| State / National Event | Purple |
| Medical Fitness Camp | Teal |

**Click event tag:** Opens `sports-event-detail` drawer.

**Click empty date:** Opens `sports-event-create` drawer with date pre-filled.

### 4.2 Week View
- 7-column grid (Mon–Sun) × 24-hour time slots
- Events shown as blocks with duration
- Same colour coding as month view

### 4.3 List View
- All events in chronological order — full table

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Date | Date | ✅ | |
| Event Name | Text | ✅ | |
| Type | Badge | ✅ | Colour-coded |
| Sport | Badge | ✅ | |
| Branches Involved | Number | ✅ | "All" if group-wide |
| Venue | Text | ❌ | |
| Status | Badge | ✅ | Planned · Confirmed · Ongoing · Completed · Cancelled |
| Actions | — | ❌ | View · Edit · Cancel |

**Pagination (list view):** Server-side · 25/page.

---

## 5. Filters (all views)

**Slide-in filter drawer — applies to all views:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Sport | Multi-select | Cricket · Football · Volleyball · Kabaddi · Athletics · Badminton · Chess · Table Tennis · Basketball · All |
| Event Type | Multi-select | Tournament · Sports Day · External · Practice · State/National |
| Status | Multi-select | Planned · Confirmed · Ongoing · Completed · Cancelled |
| Date Range | Date range picker | Custom range — default current month |

Active filters shown as chips above calendar. "Clear All" link.

---

## 6. Drawers & Modals

### 6.1 Drawer: `sports-event-create`
- **Trigger:** [+ Add Event] header · Empty date click
- **Width:** 640px
- **Tabs:** Details · Branches · Venue · Logistics

#### Tab: Details
| Field | Type | Required | Validation |
|---|---|---|---|
| Event Name | Text | ✅ | Min 3, max 150 |
| Event Type | Select | ✅ | Tournament · Sports Day · External Competition · Practice Fixture · State/National · Medical Fitness Camp |
| Sport | Select | ✅ | From group sports list |
| Start Date | Date | ✅ | |
| End Date | Date | ✅ | ≥ Start Date |
| Start Time | Time | ❌ | |
| Duration Note | Text | ❌ | e.g. "Full day", "Morning session" |
| Description | Textarea | ❌ | Max 500 chars |
| Status | Select | ✅ | Planned (default) · Confirmed |

#### Tab: Branches
| Field | Type | Required | Validation |
|---|---|---|---|
| Applies To | Radio | ✅ | All Branches · Selected Branches |
| Select Branches | Multi-select | Conditional | |
| Host Branch | Select | ❌ | If one branch is hosting |

#### Tab: Venue
| Field | Type | Required | Validation |
|---|---|---|---|
| Venue Name | Text | ❌ | |
| Venue Type | Select | ❌ | Branch Ground · Neutral Venue · External Stadium |
| Address | Textarea | ❌ | |
| Confirmed | Toggle | ❌ | Default Off |

#### Tab: Logistics
| Field | Type | Required | Notes |
|---|---|---|---|
| Coordinator Assigned | Search + select | ❌ | From group staff |
| Equipment Needed | Textarea | ❌ | Free text list |
| Medical Staff On-Site | Toggle | ❌ | |
| Transport Arranged | Toggle | ❌ | |
| Notes | Textarea | ❌ | Internal notes |

### 6.2 Drawer: `sports-event-detail`
- **Width:** 640px
- **Tabs:** Overview · Branches · Results · Logistics
- **Overview:** All event metadata read-only + [Edit Event] button (Sports Dir/Coord only)
- **Branches:** Participating branches list + registration status per branch
- **Results:** Results entry table (post-event) — if event type = Tournament, links to tournament manager
- **Logistics:** Checklist items (same as coordinator dashboard logistics section)

### 6.3 Modal: `cancel-event-confirm`
- **Width:** 420px
- **Fields:** Cancellation reason (required, min 20 chars) · Notify participants? (checkbox default on)
- **Buttons:** [Cancel Event] (danger) + [Back]

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Event created | "Event [Name] added to calendar. Branches notified." | Success | 4s |
| Event updated | "Event [Name] updated." | Success | 4s |
| Event cancelled | "Event [Name] cancelled. Participants notified." | Warning | 6s |
| Export started | "Calendar export generating…" | Info | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No events this month | "No events scheduled this month" | "Add sports events to the group calendar" | [+ Add Event] |
| No events match filters | "No events match your filters" | "Try adjusting the sport, type, or date range" | [Clear Filters] |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: view switcher + calendar grid placeholder |
| View switch | Grid/table skeleton matching new view |
| Filter apply | Calendar re-render skeleton (300ms) |
| Event create drawer | Spinner in drawer |
| Month navigation | Shimmer overlay on calendar grid |

---

## 10. Role-Based UI Visibility

| Element | Sports Dir/Coord G3 | Cultural Head G3 | Others |
|---|---|---|---|
| [+ Add Event] button | ✅ | ❌ | ❌ |
| [Edit] / [Cancel] on events | ✅ | ❌ | ❌ |
| [Export Calendar] | ✅ | ✅ (their events only) | ❌ |
| Logistics tab in drawer | ✅ | ❌ (hidden tab) | ❌ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/sports/calendar/` | JWT (G3) | Events list (with date range + filters) |
| POST | `/api/v1/group/{id}/sports/events/` | JWT (G3 Dir/Coord) | Create event |
| GET | `/api/v1/group/{id}/sports/events/{eid}/` | JWT (G3) | Event detail |
| PUT | `/api/v1/group/{id}/sports/events/{eid}/` | JWT (G3 Dir/Coord) | Update event |
| POST | `/api/v1/group/{id}/sports/events/{eid}/cancel/` | JWT (G3) | Cancel event |
| GET | `/api/v1/group/{id}/sports/calendar/export/` | JWT (G3) | Export calendar (iCal/CSV) |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Month navigation | `click` | GET `.../sports/calendar/?month={m}&year={y}` | `#calendar-grid` | `innerHTML` |
| View switch | `click` | GET `.../sports/calendar/?view={v}` | `#calendar-area` | `innerHTML` |
| Filter apply | `click` | GET `.../sports/calendar/?filters={…}` | `#calendar-area` | `innerHTML` |
| Click event tag | `click` | GET `.../sports/events/{id}/` | `#drawer-body` | `innerHTML` |
| Click empty date | `click` | GET `.../sports/events/create-form/?date={d}` | `#drawer-body` | `innerHTML` |
| Submit event form | `submit` | POST `.../sports/events/` | `#drawer-body` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
