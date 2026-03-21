# 12 — Inter-Branch Competition Tracker

> **URL:** `/group/cultural/competitions/`
> **File:** `12-inter-branch-competition-tracker.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P1
> **Roles:** Group Cultural Activities Head (Role 99, G3) · Group Sports Director (Role 97, G3)

---

## 1. Purpose

Tracks all inter-branch cultural competitions run across the group — registrations, participants, result entry, winner publishing, and certificate generation. Competitions covered include debate, quiz, essay, art, music, dance, elocution, drama/theatre, and other literary and creative contests. Both group-initiated inter-branch contests and external competitions (state-level Youth Festivals, CBSE cluster events, national cultural events) where group students are nominated are tracked here.

The page serves four sequential workflows:

1. **Planning:** Cultural Head creates a competition record with categories, participant limits per branch, and registration deadline.
2. **Registration:** Cultural Head (and, by extension, branch cultural teachers through the branch-level portal) records which branches have registered and which students/teams are nominated per category.
3. **Result entry:** After the competition date, Cultural Head enters position-wise results per category.
4. **Certificate generation:** Cultural Head generates and downloads winner, runner-up, and participation certificates as PDFs in bulk.

Scale: 20–60 competitions per academic year; each competition has 5–50 branches participating, 1–5 categories, and 5–100 student participants per branch.

---

## 2. Role Access

| Role | Role ID | Level | Access | Notes |
|---|---|---|---|---|
| Group Cultural Activities Head | 99 | G3 | Full — create, edit, cancel, enter results, generate certificates | Primary owner |
| Group Sports Director | 97 | G3 | View only — all competitions visible | Cross-reference joint competitions that involve sports; no edit capability |
| Group Sports Coordinator | 98 | G3 | No access | — |
| Group NSS/NCC Coordinator | 100 | G3 | No access | Cross-listed NSS events visible on Calendar (Page 11); competition detail not accessible |
| Group Library Head | 101 | G2 | No access | — |
| All other roles | — | — | No access | Redirected to own dashboard |

> **Access enforcement:** Django decorator `@require_role(['cultural_head'])` on all write, result-entry, and certificate endpoints. `@require_role(['cultural_head', 'sports_director'])` on read endpoints. Role 97 sees all data read-only; all action buttons (`[Enter Results]`, `[Issue Certificates]`, `[Edit]`, `[Cancel]`) are hidden server-side.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Inter-Branch Competition Tracker
```

### 3.2 Page Header
```
Inter-Branch Competition Tracker              [+ New Competition]  [Export ↓]
Group Cultural Activities Head — [Officer Name]
AY [academic year]  ·  [N] Competitions  ·  [N] Registration Open  ·  [N] Results Pending
```

`[+ New Competition]` — opens `competition-create` drawer. Role 99 only.
`[Export ↓]` — exports filtered competition list to PDF or XLSX. Available to Roles 99 and 97.

### 3.3 Alert Banners (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| Registration deadline within 7 days | "[N] competition(s) have registration deadlines within 7 days." | Amber |
| Past competition(s) with no results entered | "[N] completed competition(s) are missing results. Enter results to proceed with certificates." | Amber |
| Certificates generated but not downloaded in > 7 days | "[N] certificate batch(es) are ready and awaiting download." | Blue (Info) |
| No competitions created this AY | "No competitions have been created for this academic year." | Blue (Info) |
| All competitions have results and certificates | No banner shown | — |

---

## 4. KPI Summary Bar

Five metric cards displayed horizontally. Refreshed on load and every 5 minutes via HTMX polling.

| # | Card | Metric | Calculation | Colour Rule | HTMX Target |
|---|---|---|---|---|---|
| 1 | Total Competitions This AY | Competition records for current AY excluding Cancelled | `CompetitionRecord.objects.filter(ay=current_ay).exclude(status='cancelled').count()` | Indigo (neutral) | `#kpi-total-competitions` |
| 2 | Registration Open Now | Competitions where registration deadline ≥ today and status = Registration Open | `CompetitionRecord.objects.filter(registration_deadline__gte=today, status='registration_open').count()` | Green if > 0; Indigo if 0 | `#kpi-registration-open` |
| 3 | Results Pending Entry | Competitions held but results not yet entered | `CompetitionRecord.objects.filter(date__lt=today, results_status__in=['pending','partially_entered']).count()` | Red if > 0; Green if 0 | `#kpi-results-pending` |
| 4 | Certificates Issued This Month | Certificate batches generated in current calendar month | `CertificateBatch.objects.filter(generated_at__month=today.month).count()` | Indigo (neutral) | `#kpi-certs-month` |
| 5 | Branches — Zero Participation | Branches with no competition registration this AY | `Branch.objects.exclude(competition_registrations__ay=current_ay).count()` | Red if > 20% of branches; Amber if > 0; Green if 0 | `#kpi-zero-participation` |

```
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  Total This AY       │ │  Registration Open   │ │  Results Pending     │ │  Certs This Month    │ │  Zero-Participation  │
│         42           │ │          5           │ │          3           │ │         18           │ │          4           │
│     ● Indigo         │ │      ● Green         │ │       ● Red          │ │      ● Indigo        │ │       ● Amber        │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

> **HTMX note:** `<div id="comp-kpi-bar" hx-get="/api/v1/cultural/competitions/kpi-summary/" hx-trigger="load, every 300s" hx-swap="innerHTML">`. Each card shimmers on first load.

---

## 5. Sections

### 5.1 Competition List (Main Table)

**Search bar:** Full-width text input, debounced 400 ms. Searches `competition_name` and `activity_type`.

**Inline filter chips:** `[Activity Type ▾]` `[Status ▾]` `[Results Status ▾]` `[AY ▾]` `[More Filters ▾ (opens slide-in drawer)]`

| Column | Source Field | Sortable | Notes |
|---|---|---|---|
| Competition Name | `competition_name` | ▲▼ | Clickable — opens `competition-detail` drawer |
| Activity Type | `activity_type` | ▲▼ | Colour badge: Debate (Blue) / Quiz (Teal) / Art (Orange) / Music (Purple) / Dance (Pink) / Essay (Indigo) / Elocution (Amber) / Other (Grey) |
| Date | `date` (+ `end_date` if multi-day) | ▲▼ | `DD MMM YYYY`; red text if past and results pending |
| Branches Registered | `branch_registration_count` | ▲▼ | Count; "0" shown in red |
| Categories Count | `category_count` | ▲▼ | Number of judged categories in this competition |
| Results Status | `results_status` | ▲▼ | Badge: Pending (Amber) / Partially Entered (Orange) / Completed (Green) |
| Certificates | `certificate_status` | ▲▼ | Badge: Not Issued (Grey) / Generated (Blue) / Downloaded (Green) |
| Actions | — | — | `[View]` · `[Enter Results]` (Role 99; shown if `results_status != Completed`) · `[Issue Certificates]` (Role 99; shown if `results_status = Completed`) · `[Edit]` (Role 99) |

**Default sort:** `date` ascending (nearest upcoming first).
**Pagination:** 25 rows per page. Controls: `« Previous  Page N of N  Next »`. Rows-per-page selector: 25 / 50 / 100.

**Slide-in Filter Drawer (360 px):**

| Filter | Control | Options |
|---|---|---|
| Activity Type | Multi-select checkbox | Debate / Quiz / Art / Music / Dance / Essay / Elocution / Other |
| Status | Multi-select checkbox | Upcoming / Registration Open / Ongoing / Completed / Cancelled |
| Results Status | Multi-select checkbox | Pending / Partially Entered / Completed |
| Academic Year | Select | Current AY (default) + previous 2 AYs |

Active filters shown as removable chips above table. `[Reset Filters]` clears all.

### 5.2 Registration Open — Deadline Approaching (Alert Section)

Displayed as a collapsible panel directly above the main table when one or more competitions have `registration_deadline` within 7 days.

**Panel header:** "Registration Deadlines Approaching — [N] competition(s)" with amber warning icon. `[▸ Expand]` / `[▾ Collapse]` toggle.

When expanded, shows a compact card list — one card per qualifying competition:

| Element | Content |
|---|---|
| Competition name + activity type badge | Bold heading + badge |
| Deadline | "Deadline: DD MMM YYYY" — shown in red if within 48 hours |
| Branch registration status | Mini table: Branch Name · Registered (Yes/No badge) · Participants Count |
| Action | `[View Full Details]` — opens `competition-detail` drawer to the Registrations tab |

### 5.3 Results Awaiting Entry (Compact Table)

Displayed as a collapsible panel below the alert section when one or more past competitions have `results_status = Pending` or `Partially Entered`.

**Panel header:** "Results Awaiting Entry — [N] competition(s)" with amber clock icon.

Compact table (no pagination — shows up to 10 rows; `[View All]` links to filtered main table):

| Column | Notes |
|---|---|
| Competition Name | Clickable — opens detail drawer to Results tab |
| Activity Type | Badge |
| Date | `DD MMM YYYY` |
| Results Status | Pending / Partially Entered badge |
| Action | `[Enter Results]` — opens `result-entry-form` drawer (Role 99 only) |

---

## 6. Drawers & Modals

### 6.1 `competition-create` Drawer — 680 px, right-slide

**Trigger:** `[+ New Competition]` header button. Role 99 only.

**Header:**
```
New Competition
Define the competition, its categories, participating branches, and awards.
```

**Tab 1 — Details**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Competition Name | Text input | Yes | Min 3, max 150 characters |
| Activity Type | Select | Yes | Debate / Quiz / Art / Music / Dance / Essay / Elocution / Other |
| Date | Date picker | Yes | Start date of the competition |
| End Date | Date picker | Yes | Must be ≥ Date; defaults to same day |
| Organizing Branch | Select | No | Branch responsible for hosting; "Group HQ" as default option |
| Description | Textarea | No | Max 500 characters |
| External Competition? | Toggle | No | Default off; when on, indicates this is an external event (state/national); enables External Organizer and Registration URL fields |
| External Organizer | Text input | Conditional | Shown when External Competition = on; max 150 chars |
| Registration URL | URL input | Conditional | Shown when External Competition = on; validated as URL |

**Tab 2 — Categories**

Dynamic row table. Minimum 1 category required; maximum 10.

| Column | Type | Required | Validation / Notes |
|---|---|---|---|
| Category Name | Text input | Yes | Max 100 chars; e.g. "Senior Debate (Cl 11–12)" |
| Age Group / Class | Select | Yes | Classes 6–8 (Junior) / Classes 9–10 (Middle) / Classes 11–12 (Senior) / Open |
| Max Participants Per Branch | Number input | Yes | Positive integer; 1–100 |
| Judging Criteria | Textarea | No | Max 300 chars; e.g. "Content 40%, Delivery 30%, Language 30%" |

`[+ Add Category]` button below the table adds a new blank row.
`[× Remove]` icon on each row (disabled when only 1 row remains).

**Tab 3 — Branches**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Invite | Radio buttons | Yes | All Branches / Selected Branches |
| Select Branches | Multi-select checkbox | Conditional | Required if "Selected Branches"; lists all active branches; searchable |
| Registration Deadline | Date picker | Yes | Required; must be ≤ Date (competition date) |
| Allow Late Registration | Toggle | No | Default off; when on, Cultural Head can register a branch after deadline from the detail drawer |

**Tab 4 — Awards**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Positions to Award | Number input | Yes | Default 3; range 1–10 |
| Trophy | Checkbox | No | Default unchecked |
| Certificate — Winner | Checkbox | No | Default checked |
| Certificate — Runner-Up | Checkbox | No | Default checked |
| Certificate — Participation | Checkbox | No | Default checked |
| Prize Details per Position | Textarea | No | Max 500 chars; e.g. "1st: ₹5,000 + Trophy, 2nd: ₹3,000, 3rd: ₹1,500" |

**Footer:** `[Cancel]`  `[Save as Draft]`  `[Publish — Open Registration]`

`[Save as Draft]` → `status = Upcoming` (not visible to branches).
`[Publish — Open Registration]` → `status = Registration Open` (visible to branch teachers in branch portal).

---

### 6.2 `competition-detail` Drawer — 680 px, right-slide

**Trigger:** Clicking competition name in table, or `[View]` action button.

**Header:**
```
[Competition Name]                              [Edit ✎]  [Cancel]  [×]
[Activity Type badge]  ·  Status: [status pill]  ·  [Date] – [End Date]
[Organizing Branch]  ·  [N] Categories  ·  [N] Branches Registered
```

`[Edit ✎]` — opens competition fields inline for editing. Role 99 only; disabled for Completed/Cancelled.
`[Cancel]` — opens `cancel-competition` modal. Role 99 only.

**Tab 1 — Overview**

Full metadata: Competition Name, Activity Type, Date, End Date, Organizing Branch, Description, External Competition flag (External Organizer / Registration URL if external), Status, Positions to Award, Trophy/Certificate flags, Prize Details, Registration Deadline, Allow Late Registration, Created By, Created At.

Category list displayed as a sub-table:

| Category Name | Age Group / Class | Max Per Branch | Judging Criteria |
|---|---|---|---|
| Senior Debate | Classes 11–12 | 2 | Content 40%, Delivery 30%… |

**Tab 2 — Registrations**

Table of branch registration status:

| Column | Notes |
|---|---|
| Branch Name | — |
| Category | Which category this row applies to (one row per branch × category combination) |
| Participants Registered | Count; clickable to expand inline list of participant names |
| Participant Names (expand) | Inline expandable row: table of Student Name · Class · Confirmed |
| Registration Status | Badge: Registered (Green) / Not Registered (Grey) / Late Registration (Amber) / Declined (Red) |
| Actions | `[View Details]` (expands participant names) · `[Register Branch]` (Role 99; shown if Not Registered; opens mini form with branch select + participant name entry) |

`[Download Registration List CSV]` button above table. Role 99 only.

**Tab 3 — Results**

Per-category result entry section. Shown for all statuses; editable only when `date` < today.

For each category, a sub-section with heading "[Category Name]":

| Column | Notes |
|---|---|
| Position | 1st / 2nd / 3rd (gold / silver / bronze badge) |
| Branch | Select from registered branches for this category |
| Student / Team Name | Text input |
| Score / Marks | Number input (optional) |
| Notes | Text input (optional) |

`[Save Draft Results]` — saves without publishing; visible to other roles as "Results Pending".
`[Publish Results]` — Role 99 only; makes results visible group-wide; sets `results_status = Completed`; cannot be undone via UI (requires admin).

**Tab 4 — Certificates**

Shown when `results_status = Completed`.

| Element | Notes |
|---|---|
| Recipients scope | Radio: All Participants / Position Winners Only / Custom Selection |
| Custom selection | Multi-select of individual participants (shown if Custom selected) |
| Certificate Type | Select: Winner / Runner-Up / Participation / All Types |
| Signature Authority | Text input (optional); max 100 chars; e.g. "Group Cultural Activities Head" |
| Certificate Date | Date picker; defaults to today |
| Generate button | `[Generate Certificates]` — triggers async PDF generation; progress bar shown |
| Download | After generation: `[Download All as ZIP]` + individual download links per certificate |
| History | Table of previous generation batches: Date · Recipients Count · Generated By · Download |

**Tab 5 — Report**

| Field | Notes |
|---|---|
| Total Participants | Auto-calculated from registrations; editable override |
| Branches Participated | Auto-calculated count |
| Highlights | Textarea; max 1000 chars |
| Overall Winner Branch | Auto-populated from results if applicable |
| Export Summary | `[Export Competition Report PDF]` button |

---

### 6.3 `result-entry-form` Drawer — 560 px, right-slide

**Trigger:** `[Enter Results]` action button in main table, or in §5.3 results-pending panel.

**Header:**
```
Enter Results — [Competition Name]
[Activity Type badge]  ·  Date: [DD MMM YYYY]
```

| Field | Type | Required | Notes |
|---|---|---|---|
| Select Category | Select | Yes | Dropdown of competition categories; "All Categories" option shows accordion for each |
| Position | Select per row | Yes | 1st / 2nd / 3rd (up to `positions_to_award` rows) |
| Branch | Select per row | Yes | Filtered to branches registered for this category |
| Student / Team Name | Text input per row | Yes | Max 150 chars |
| Score / Marks | Number per row | No | Optional; positive decimal |
| Notes | Text input per row | No | Max 200 chars |

`[+ Add Special Award]` repeating row: Award Name + Recipient Name + Branch.

**Footer:** `[Cancel]`  `[Save Draft]`  `[Publish Results]`

`[Publish Results]` shows a confirmation: "Publishing results will make them visible across the group. This cannot be easily reversed. Proceed?" `[Cancel]` / `[Confirm & Publish]`.

---

### 6.4 `certificate-generate` Modal — 480 px, centred

**Trigger:** `[Issue Certificates]` action in main table row, or `[Generate Certificates]` button in detail drawer Tab 4.

**Header:**
```
Generate Certificates
[Competition Name]
```

| Field | Type | Required | Notes |
|---|---|---|---|
| Competition | Read-only | — | Pre-filled from context |
| Recipients | Radio | Yes | All Participants / Position Winners Only (1st–Nth) / Custom selection |
| Certificate Type | Select | Yes | Winner / Runner-Up / Participation / All Types |
| Signature Authority | Text input | No | Max 100 chars |
| Certificate Date | Date picker | Yes | Defaults to today |

**Footer:** `[Cancel]`  `[Generate →]`

After clicking `[Generate →]`:
- Modal body transitions to progress state: progress bar with label "Generating [N] certificates…"
- On completion: `[Download All as ZIP]` button replaces progress bar
- Toast: "[N] certificates generated."

---

### 6.5 `cancel-competition` Modal — 420 px, centred

**Trigger:** `[Cancel]` button in competition-detail drawer header. Role 99 only.

**Header:**
```
Cancel Competition
This cannot be undone. Branches will be notified if notification is enabled.
```

| Field | Type | Required | Validation |
|---|---|---|---|
| Cancellation Reason | Textarea | Yes | Min 20 characters |
| Notify Registered Branches | Checkbox | — | Default checked |

**Footer:** `[Go Back]`  `[Confirm Cancellation]`

On confirm: `status` → Cancelled; `cancel_reason` stored; notifications dispatched if checked.

---

## 7. Charts

Charts are placed in a two-column row below the KPI bar, above the alert sections. `[▸ Hide Charts]` toggle collapses the row.

### 7.1 Participation Rate by Branch — Horizontal Bar Chart

| Property | Value |
|---|---|
| Chart type | Horizontal bar (Chart.js 4.x) |
| Data | For each branch: `(competitions participated / total competitions this AY) × 100` |
| X-axis | Participation percentage (0–100%) |
| Y-axis | Branch names; show top 15 most active (sorted descending); `[Show All]` button expands to full list |
| Bar colours | Green if ≥ 70%; Amber if 40–69%; Red if < 40% |
| Tooltip | "[Branch Name]: [N] competitions ([N]%)" |
| HTMX load | `hx-get="/api/v1/cultural/competitions/charts/participation-by-branch/"` `hx-trigger="load"` |

### 7.2 Activity Type Distribution — Donut Chart

| Property | Value |
|---|---|
| Chart type | Donut (Chart.js 4.x) |
| Data | Count of competitions per `activity_type` for current AY; excludes Cancelled |
| Segment colours | Match activity type badge colours from §5.1 |
| Legend | Right-side legend with type name + count |
| Tooltip | "[Activity Type]: [N] competitions ([N]%)" |
| Centre label | Total competitions count |
| HTMX load | `hx-get="/api/v1/cultural/competitions/charts/by-type/"` `hx-trigger="load"` |

---

## 8. Toast Messages

| Action | Toast Text | Type |
|---|---|---|
| Competition created — Draft | "Competition '[Name]' saved as draft." | Success |
| Competition created — Registration Open | "Competition '[Name]' published. Registration is now open for branches." | Success |
| Competition updated | "Changes to '[Name]' saved." | Success |
| Competition cancelled | "Competition '[Name]' cancelled. [N] branch(es) notified." | Success |
| Results saved as draft | "Draft results saved for '[Name]'." | Success |
| Results published | "Results published for '[Name]'. All branches can now view the outcome." | Success |
| Certificate generation started | "Generating [N] certificates for '[Name]'…" | Info |
| Certificates ready | "[N] certificates ready for '[Name]'. Click to download." | Success |
| Registration deadline today | "Registration deadline for '[Name]' is today." | Warning |
| Export complete | "Competition list exported to [format]." | Success |
| Required field missing | "Please complete all required fields before saving." | Error |
| Network / server error | "Could not save. Please try again." | Error |
| Result publish attempt — no results entered | "Enter at least one position result before publishing." | Error |

---

## 9. Empty States

| Context | Illustration | Heading | Sub-text | Action |
|---|---|---|---|---|
| No competitions in current AY | Trophy icon | "No Competitions Recorded" | "Create your first inter-branch competition for this academic year." | `[+ New Competition]` (Role 99 only) |
| No competitions match filters | Funnel icon | "No Competitions Match Filters" | "Try adjusting your filters or reset to see all competitions." | `[Reset Filters]` |
| Registrations tab — no registrations | Clipboard icon | "No Branches Registered" | "Registration is open. Branches can register via the branch portal." | — |
| Results tab — date not reached | Hourglass icon | "Competition Not Yet Held" | "Results can be entered after the competition date has passed." | — |
| Results tab — date past, no results | Clipboard icon | "No Results Entered" | "Enter position results for each category to proceed with certificate generation." | `[Enter Results]` (Role 99 only) |
| Certificates tab — results pending | Lock icon | "Results Not Yet Published" | "Publish competition results before generating certificates." | `[Publish Results]` (Role 99 only) |
| §5.3 panel — no pending results | Checkmark icon | "All Results Up to Date" | "Every past competition has results recorded." | — |

---

## 10. Loader States

| Context | Loader Behaviour |
|---|---|
| Initial page load | KPI bar: 5 shimmer cards. Alert panels: shimmer card. Charts: 2 shimmer rectangles. Table: 8 shimmer rows |
| Filter or search change | Table rows replaced by 6 shimmer rows + indigo spinner below toolbar |
| Competition detail drawer opening | Drawer slides in; shimmer tab bar + shimmer content; real content replaces on API response |
| Registrations tab (lazy load) | Tab content: shimmer table rows while fetching |
| Results tab (lazy load) | Shimmer form rows per category |
| Certificates tab (lazy load) | Shimmer rows for history table |
| `[Enter Results]` drawer | Drawer slides in; shimmer category rows; real content replaces |
| `[Save Draft Results]` / `[Publish Results]` | Button disabled + "Saving…" + spinner; re-enables on response |
| `[Generate Certificates]` | Progress bar in modal: "Generating [N] certificates…"; replaces with `[Download All as ZIP]` on completion |
| Export | `[Export ↓]` disabled + "Preparing…" + spinner |
| KPI auto-refresh | Cards pulse; values update in place |

---

## 11. Role-Based UI Visibility

| UI Element | Role 99 (Cultural Head) | Role 97 (Sports Director) | All Others |
|---|---|---|---|
| KPI Summary Bar | Full | Full | Hidden |
| Charts row | Visible | Visible | Hidden |
| Competition table — all rows | Visible | Visible | Hidden |
| `[+ New Competition]` button | Visible | Hidden | Hidden |
| `[Export ↓]` button | Visible | Visible | Hidden |
| Filter drawer | Full | Full | Hidden |
| `[View]` action | Visible | Visible | Hidden |
| `[Enter Results]` action | Visible | Hidden | Hidden |
| `[Issue Certificates]` action | Visible | Hidden | Hidden |
| `[Edit]` in detail drawer | Visible | Hidden | Hidden |
| `[Cancel]` in detail drawer | Visible | Hidden | Hidden |
| Registration tab — `[Register Branch]` | Visible | Hidden | Hidden |
| Registration tab — download CSV | Visible | Hidden | Hidden |
| Results tab — `[Save Draft]` / `[Publish]` | Visible | Hidden | Hidden |
| Certificates tab — full access | Visible | Hidden | Hidden |
| Alert banners (§3.3) | Full | Full | Hidden |
| §5.2 alert panel | Visible | Visible | Hidden |
| §5.3 results-pending panel | Visible | Visible (read-only) | Hidden |

---

## 12. API Endpoints

### 12.1 List Competitions
```
GET /api/v1/cultural/competitions/
```

| Query Parameter | Type | Description |
|---|---|---|
| `activity_type` | string (multi) | `debate` · `quiz` · `art` · `music` · `dance` · `essay` · `elocution` · `other` |
| `status` | string (multi) | `upcoming` · `registration_open` · `ongoing` · `completed` · `cancelled` |
| `results_status` | string (multi) | `pending` · `partially_entered` · `completed` |
| `academic_year` | string | e.g. `2025-26`; defaults to current AY |
| `search` | string | Searches `competition_name` |
| `page` | integer | Default 1 |
| `page_size` | integer | 25 · 50 · 100; default 25 |
| `ordering` | string | `date` · `-date` · `competition_name` · `results_status` |

Response: `{ count, next, previous, results: [...] }`.

### 12.2 Create Competition
```
POST /api/v1/cultural/competitions/
```
Body: JSON — all fields from §6.1. Role 99 only.
Response: 201 Created — competition object.

### 12.3 Retrieve Competition Detail
```
GET /api/v1/cultural/competitions/{competition_id}/
```
Response: 200 OK — full competition object including categories, registration summary.

### 12.4 Update Competition
```
PATCH /api/v1/cultural/competitions/{competition_id}/
```
Body: JSON partial update. Role 99 only; Cancelled competitions return HTTP 403.
Response: 200 OK.

### 12.5 Cancel Competition
```
POST /api/v1/cultural/competitions/{competition_id}/cancel/
```
Body: `{ "cancel_reason": "string", "notify_branches": true }`. Role 99 only.
Response: 200 OK — updated competition with `status = cancelled`.

### 12.6 Registrations — List
```
GET /api/v1/cultural/competitions/{competition_id}/registrations/
```
Returns per-branch, per-category registration records including participant names.
Response: `{ count, results: [...] }`.

### 12.7 Register a Branch
```
POST /api/v1/cultural/competitions/{competition_id}/registrations/
```
Body: `{ "branch_id": "...", "category_id": "...", "participants": [ { "name": "...", "class": "..." } ] }`. Role 99 only (or branch teacher via branch portal).
Response: 201 Created.

### 12.8 Results — List
```
GET /api/v1/cultural/competitions/{competition_id}/results/
```
Returns all result entries per category.

### 12.9 Results — Save / Publish
```
POST /api/v1/cultural/competitions/{competition_id}/results/
```
Body: `{ "category_id": "...", "entries": [ { "position": 1, "branch_id": "...", "student_name": "...", "score": 95.5, "notes": "..." } ], "special_awards": [...], "publish": false }`.
`publish: true` sets `results_status = completed` and makes results group-visible.
Role 99 only. Response: 201 Created.

### 12.10 Certificates — Generate
```
POST /api/v1/cultural/competitions/{competition_id}/certificates/generate/
```
Body: `{ "recipients": "all|winners|custom", "custom_participant_ids": [...], "certificate_type": "winner|runner_up|participation|all", "signature_authority": "...", "certificate_date": "YYYY-MM-DD" }`.
Role 99 only. Response: 202 Accepted — `{ "job_id": "..." }`.
Poll: `GET /api/v1/cultural/competitions/{competition_id}/certificates/status/{job_id}/` → `{ "status": "pending|processing|ready|failed", "count": N, "download_url": "..." }`.

### 12.11 KPI Summary
```
GET /api/v1/cultural/competitions/kpi-summary/
```
Query: `academic_year` (optional).
Response: `{ "total_this_ay": N, "registration_open": N, "results_pending": N, "certs_this_month": N, "zero_participation_branches": N }`.

### 12.12 Deadline Alert Data
```
GET /api/v1/cultural/competitions/deadline-alerts/
```
Returns competitions with `registration_deadline` within 7 days, including per-branch registration status.
Response: `{ "results": [...] }`.

### 12.13 Chart Data
```
GET /api/v1/cultural/competitions/charts/participation-by-branch/
GET /api/v1/cultural/competitions/charts/by-type/
```
Both accept optional `academic_year`.

### 12.14 Export
```
GET /api/v1/cultural/competitions/export/
```
Query: all filter params from §12.1 + `format` (`pdf` · `xlsx`).
Response: File download.

---

## 13. HTMX Patterns

### 13.1 KPI Bar
```html
<div id="comp-kpi-bar"
     hx-get="/api/v1/cultural/competitions/kpi-summary/"
     hx-trigger="load, every 300s"
     hx-swap="innerHTML"
     hx-indicator="#kpi-spinner">
</div>
```

### 13.2 Competition Table Initialisation
```html
<div id="competition-table"
     hx-get="/api/v1/cultural/competitions/?page=1&page_size=25"
     hx-trigger="load"
     hx-swap="innerHTML"
     hx-indicator="#table-spinner">
</div>
```

### 13.3 Search (Debounced)
```html
<input type="text"
       id="comp-search"
       name="search"
       placeholder="Search competitions…"
       hx-get="/api/v1/cultural/competitions/"
       hx-trigger="keyup changed delay:400ms"
       hx-target="#competition-table"
       hx-swap="innerHTML"
       hx-include="#filter-activity-type, #filter-status, #filter-results-status, #filter-ay">
```

### 13.4 Filter Application
```html
<select name="status"
        id="filter-status"
        hx-get="/api/v1/cultural/competitions/"
        hx-trigger="change"
        hx-target="#competition-table"
        hx-swap="innerHTML"
        hx-include="#comp-search, #filter-activity-type, #filter-results-status, #filter-ay">
</select>
```

### 13.5 Competition Detail Drawer Open
```html
<button hx-get="/htmx/cultural/competitions/{{ competition_id }}/detail/"
        hx-target="#drawer-container"
        hx-swap="innerHTML"
        hx-trigger="click"
        class="text-indigo-600 hover:underline text-sm font-medium">
  View
</button>
```

### 13.6 Result Entry Drawer Open
```html
<button hx-get="/htmx/cultural/competitions/{{ competition_id }}/result-entry/"
        hx-target="#drawer-container"
        hx-swap="innerHTML"
        hx-trigger="click">
  Enter Results
</button>
```

### 13.7 Result Entry Form Submission
```html
<form id="result-entry-form"
      hx-post="/api/v1/cultural/competitions/{{ competition_id }}/results/"
      hx-encoding="application/json"
      hx-target="#competition-table"
      hx-swap="innerHTML"
      hx-on::after-request="closeDrawer(); showToast(event); refreshKPI();">
</form>
```

### 13.8 Publish Results Confirmation
```html
<button hx-post="/api/v1/cultural/competitions/{{ competition_id }}/results/"
        hx-vals='{"publish": true}'
        hx-encoding="application/json"
        hx-target="#competition-table"
        hx-swap="innerHTML"
        hx-confirm="Publishing results will make them visible group-wide. This cannot be easily reversed. Proceed?"
        hx-on::after-request="closeDrawer(); showToast(event); refreshKPI();">
  Publish Results
</button>
```

### 13.9 Certificate Generation Modal Submission
```html
<form hx-post="/api/v1/cultural/competitions/{{ competition_id }}/certificates/generate/"
      hx-encoding="application/json"
      hx-target="#cert-modal-body"
      hx-swap="innerHTML"
      hx-on::after-request="showToast(event); pollCertStatus('{{ competition_id }}', htmx.find('#job-id').value);">
</form>
```

### 13.10 Detail Drawer Tab Switching (Lazy Load)
```html
<button hx-get="/htmx/cultural/competitions/{{ competition_id }}/tab/registrations/"
        hx-target="#comp-drawer-tab-content"
        hx-swap="innerHTML"
        hx-trigger="click">
  Registrations
</button>
```
All five tabs lazy-load their content on first click. Overview is pre-fetched on drawer open. Certificates tab additionally fetches certificate history. Each tab shows a shimmer skeleton while loading.

### 13.11 Deadline Alert Panel Load
```html
<div id="deadline-alert-panel"
     hx-get="/api/v1/cultural/competitions/deadline-alerts/"
     hx-trigger="load"
     hx-swap="innerHTML"
     hx-indicator="#deadline-spinner">
</div>
```

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
