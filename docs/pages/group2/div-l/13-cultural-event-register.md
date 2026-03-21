# 13 — Cultural Event Register

> **URL:** `/group/cultural/events/`
> **File:** `13-cultural-event-register.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P1
> **Roles:** Cultural Activities Head G3 (full) · Branch Cultural Teacher Branch G2 (own branch events)

---

## 1. Purpose

Full register of all cultural events across the group — both group-level inter-branch events and individual branch-level cultural programs. Each event record includes planning checklists, participant lists, results, photos, and post-event reports. Serves as the definitive historical log of all cultural activity across all branches for the academic year.

Distinct from the Competition Tracker (page 12), which focuses on scored competitions with rankings. The Event Register covers all cultural programming including Annual Days, cultural weeks, fests, talent shows, awareness drives, and non-competitive events.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Cultural Activities Head | G3 | Full CRUD all events | |
| Branch Cultural Teacher | Branch G2 | Create and manage own branch events | Cannot see other branches |
| Branch Principal | Branch G3 | View own branch events | |
| All others | — | — | No access |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Cultural Event Register
```

### 3.2 Page Header
```
Cultural Event Register                            [+ New Event]  [Export ↓]
AY [academic year]  ·  [N] Total Events  ·  [N] Branches  ·  [N] Students Participated
```

---

## 4. Events Table

**Search:** Event name, branch, type. Debounce 300ms.

**Advanced Filters:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Type | Multi-select | Annual Day · Cultural Week · Talent Show · Awareness Drive · Art Exhibition · Literary · Music Fest · Dance · Drama · Other |
| Level | Multi-select | Group-wide · Branch-level |
| Status | Multi-select | Planning · In Progress · Completed · Cancelled |
| Date Range | Date range | |
| Report Submitted | Toggle | Show events without post-event report |

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Event Name | Text + link | ✅ | Opens `cultural-event-detail` drawer |
| Branch | Text | ✅ | "All Branches" for group events |
| Type | Badge | ✅ | |
| Level | Badge | ✅ | Group / Branch |
| Date | Date | ✅ | |
| Students | Number | ✅ | Participants count |
| Audience | Number | ✅ | Total attendees (students + parents + staff) |
| Status | Badge | ✅ | |
| Report | Badge | ✅ | ✅ Submitted · ❌ Pending · — N/A |
| Actions | — | ❌ | View · Edit · Submit Report · Cancel |

**Default sort:** Date descending (most recent first).

**Pagination:** 25/page.

---

## 5. Drawers & Modals

### 5.1 Drawer: `cultural-event-full-detail`
- **Width:** 680px
- **Tabs:** Overview · Planning Checklist · Participants · Results · Photos & Report

#### Tab: Overview
Full event metadata. [Edit Event] button (Cultural Head / Branch Teacher for own branch).

Key fields displayed:
| Field | Value |
|---|---|
| Event Name | |
| Type | |
| Branch | |
| Date | |
| Venue | |
| Chief Guest | |
| Organizer | |
| Theme (if any) | |
| Budget Allocated ₹ | |
| Actual Expenditure ₹ | |

#### Tab: Planning Checklist
Standard checklist with toggleable items. Cultural Head defines template; branch teacher completes.

**Default checklist items:**
- [ ] Theme and programme sequence finalized
- [ ] Rehearsal schedule published
- [ ] Venue decoration plan approved
- [ ] Chief Guest / Dignitaries confirmed
- [ ] Invitations sent (Parents / Management)
- [ ] Audio-visual setup arranged
- [ ] Refreshments arranged
- [ ] Photographer / Videographer booked
- [ ] Safety / first aid arrangement in place
- [ ] Principal approval obtained

Each item: Toggle · Updated by · Updated at · Notes.

#### Tab: Participants
Table: Student Name · Class · Event Performed/Participated in · Role (Performer/Organizer/Audience Rep) · Confirmed.
[+ Add Participant] button. Bulk import from CSV.

#### Tab: Results (for competitive events)
Winner · Runner-up · Special awards. Same as competition result entry flow.

#### Tab: Photos & Report
**Photos:** Multi-file image upload (JPG/PNG — max 20 photos, 5MB each). Gallery view after upload.

**Post-Event Report:**
| Field | Type | Required |
|---|---|---|
| Report Narrative | Textarea (rich text) | ✅ (if status = Completed) |
| Total Participants | Number | ✅ |
| Total Audience | Number | ❌ |
| Highlights | Textarea | ❌ |
| Issues / Learnings | Textarea | ❌ |
| Budget Spent ₹ | Number | ❌ |
| Attachments | File upload | ❌ |

[Submit Report] button → status changes to "Report Submitted".

### 5.2 Modal: `cancel-event`
- **Width:** 420px
- **Fields:** Reason (required, min 20 chars) · Notify participants (checkbox on)
- **Buttons:** [Cancel Event] (danger) + [Back]

---

## 6. Charts

### 6.1 Events by Branch (current AY)
- **Type:** Horizontal bar
- **Data:** Event count per branch (all events including branch-level)
- **Export:** PNG

### 6.2 Participation by Event Type (current AY)
- **Type:** Donut
- **Data:** Student participation count per event type
- **Export:** PNG

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Event created | "Cultural event [Name] created." | Success | 4s |
| Report submitted | "Post-event report submitted for [Name]." | Success | 4s |
| Photos uploaded | "[N] photos uploaded for [Name]." | Info | 4s |
| Event cancelled | "Event cancelled. Participants notified." | Warning | 6s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No events this AY | "No cultural events recorded" | "Create your first cultural event" | [+ New Event] |
| Reports pending | "Post-event reports missing" | "Events without reports shown when filter is applied" | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: table (8 rows) + charts |
| Filter/search | Inline skeleton rows |
| Drawer tab switch | Skeleton for tab content |
| Photo upload | Progress bar per file |
| Report submit | Spinner in submit button |

---

## 10. Role-Based UI Visibility

| Element | Cultural Head G3 | Branch Teacher (own branch) |
|---|---|---|
| [+ New Event] | ✅ | ✅ (branch-level only) |
| Edit any event | ✅ | Own branch only |
| Planning checklist toggle | ✅ | ✅ (own branch) |
| Submit Report | ✅ | ✅ (own branch) |
| View all branches | ✅ | Own branch only |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/cultural/events/` | JWT (G3) | Events register |
| POST | `/api/v1/group/{id}/cultural/events/` | JWT (G3) | Create event |
| GET | `/api/v1/group/{id}/cultural/events/{eid}/` | JWT (G3) | Event detail (all tabs) |
| PUT | `/api/v1/group/{id}/cultural/events/{eid}/` | JWT (G3) | Update event |
| PATCH | `/api/v1/group/{id}/cultural/events/{eid}/checklist/{item}/` | JWT (G3) | Toggle checklist item |
| POST | `/api/v1/group/{id}/cultural/events/{eid}/report/` | JWT (G3) | Submit post-event report |
| POST | `/api/v1/group/{id}/cultural/events/{eid}/photos/` | JWT (G3) | Upload photos |
| POST | `/api/v1/group/{id}/cultural/events/{eid}/cancel/` | JWT (G3) | Cancel event |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Table search | `input delay:300ms` | GET `.../cultural/events/?q=` | `#events-table-body` | `innerHTML` |
| Filter apply | `click` | GET `.../cultural/events/?filters=` | `#events-table-section` | `innerHTML` |
| Open event detail | `click` | GET `.../cultural/events/{id}/` | `#drawer-body` | `innerHTML` |
| Drawer tab switch | `click` | GET `.../cultural/events/{id}/{tab}/` | `#drawer-tab-content` | `innerHTML` |
| Checklist item toggle | `change` | PATCH `.../events/{id}/checklist/{item}/` | `#checklist-item-{item}` | `outerHTML` |
| Submit report | `submit` | POST `.../events/{id}/report/` | `#drawer-body` | `innerHTML` |
| Pagination | `click` | GET `.../cultural/events/?page=` | `#events-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
