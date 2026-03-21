# 13 — Cultural Event Register

> **URL:** `/group/cultural/events/`
> **File:** `13-cultural-event-register.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P1
> **Roles:** Group Cultural Activities Head (Role 99, G3) · Group Sports Director (Role 97, G3) · Group NSS/NCC Coordinator (Role 100, G3)

---

## 1. Purpose

Serves as the authoritative master register of all cultural events across all branches — including branch-level events reported up to group headquarters, group-initiated events, and external events in which students participated. Distinct from the Calendar (Page 11, which handles visual scheduling and planning) and the Competition Tracker (Page 12, which handles registrations and results for scored contests). The Register is the permanent record of completed and documented events: outcomes, attendance figures, budgets, uploaded evidence, and approval status.

The workflow is:

1. **Group-initiated events** are created directly by the Cultural Head; they are Approved immediately on creation.
2. **Branch-reported events** are submitted by branch cultural teachers via the branch portal (not this page) and appear in this register with `approval_status = Pending Review`. The Cultural Head reviews them and approves or rejects. Rejected records may be returned to the branch for resubmission.
3. **External participation events** (students representing the group at external events) are recorded by the Cultural Head with external event details.

Scale: 200–600 event records per academic year across all branches. The register is the compliance and reporting source — it is queried for group-level cultural activity reports, management presentations, and annual review data.

---

## 2. Role Access

| Role | Role ID | Level | Access | Notes |
|---|---|---|---|---|
| Group Cultural Activities Head | 99 | G3 | Full CRUD — create, edit, approve, reject, archive, export | Primary owner; approval authority |
| Group Sports Director | 97 | G3 | View only — all records visible | Cross-reference awareness; no edit or approval capability |
| Group NSS/NCC Coordinator | 100 | G3 | View only — cross-listed events (NSS/NCC Event type) visible | Filtered view; other event types not visible |
| Group Sports Coordinator | 98 | G3 | No access | — |
| Group Library Head | 101 | G2 | No access | — |
| All other roles | — | — | No access | Redirected to own dashboard |

> **Access enforcement:** Django decorator `@require_role(['cultural_head'])` on all write, approval, reject, and archive endpoints. `@require_role(['cultural_head', 'sports_director', 'nss_ncc_coordinator'])` on read; NSS/NCC Coordinator has an additional server-side queryset filter to return only records where `event_type = nss_ncc_event`. Role 97 sees all records read-only with no action buttons other than `[View]`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Cultural Event Register
```

### 3.2 Page Header
```
Cultural Event Register                      [+ New Record]  [Export ↓]
Group Cultural Activities Head — [Officer Name]
AY [academic year]  ·  [N] Total Records  ·  [N] Pending Review  ·  [N] Approved  ·  [N] Rejected
```

`[+ New Record]` — opens `event-record-create` drawer. Role 99 only.
`[Export ↓]` — dropdown: Export to PDF / Export to XLSX (current filtered view). Roles 99 and 97.

### 3.3 Alert Banners (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| Branch-submitted events pending review > 0 | "[N] branch-reported event(s) are awaiting your review and approval." | Amber |
| Event records with missing evidence uploaded > 10% of AY total | "[N] approved event records have no evidence uploaded. Request uploads from branches." | Amber |
| Rejected records not resubmitted after 14 days | "[N] rejected record(s) have not been resubmitted by branches. Follow up if needed." | Blue (Info) |
| No records for current AY | "No cultural event records have been added for this academic year." | Blue (Info) |
| All pending reviews cleared | No banner shown | — |

---

## 4. KPI Summary Bar

Four metric cards displayed horizontally. Refreshed on load and every 5 minutes via HTMX polling.

| # | Card | Metric | Calculation | Colour Rule | HTMX Target |
|---|---|---|---|---|---|
| 1 | Total Events This AY | All non-Archived event records for current AY | `CulturalEventRecord.objects.filter(ay=current_ay).exclude(status='archived').count()` | Indigo (neutral) | `#kpi-total-events` |
| 2 | Group-Initiated Events | Group-created events approved this AY | `CulturalEventRecord.objects.filter(ay=current_ay, record_source='group', approval_status='approved').count()` | Indigo (neutral) | `#kpi-group-initiated` |
| 3 | Branch-Reported Pending Review | Branch submissions awaiting Cultural Head approval | `CulturalEventRecord.objects.filter(approval_status='pending_review').count()` | Red if > 0; Green if 0 | `#kpi-pending-review` |
| 4 | External Events Participated | Approved external event participation records this AY | `CulturalEventRecord.objects.filter(ay=current_ay, external_event=True, approval_status='approved').count()` | Indigo (neutral) | `#kpi-external-events` |

```
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  Total Events AY     │ │  Group-Initiated     │ │  Pending Review      │ │  External Events     │
│        324           │ │         58           │ │          9           │ │         21           │
│     ● Indigo         │ │      ● Indigo        │ │       ● Red          │ │      ● Indigo        │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

> **HTMX note:** `<div id="register-kpi-bar" hx-get="/api/v1/cultural/events/kpi-summary/" hx-trigger="load, every 300s" hx-swap="innerHTML">`. Cards shimmer on first load.

---

## 5. Sections

### 5.1 Event Register (Main Table)

**Search bar:** Full-width text input, debounced 400 ms. Searches `event_name`, `branch_name`, `submitted_by_name`.

**Inline filter chips:** `[Branch ▾]` `[Type ▾]` `[Approval Status ▾]` `[Evidence ▾]` `[Date Range ▾]` `[AY ▾]` `[More Filters ▾]`

| Column | Source Field | Sortable | Notes |
|---|---|---|---|
| Event Name | `event_name` | ▲▼ | Clickable — opens `event-record-detail` drawer |
| Branch | `branch_name` | ▲▼ | Link to branch profile; "Group HQ" for group-initiated events |
| Type | `event_type` | ▲▼ | Colour badge (see §5.3) |
| Date | `date_held` | ▲▼ | `DD MMM YYYY`; most recent first by default |
| Attendance Count | `attendance_count` | ▲▼ | Total attendance number |
| Budget Used (₹) | `actual_expenditure` | ▲▼ | Currency formatted; "—" if not recorded |
| Outcome / Result | `outcome_summary` | — | Truncated at 60 chars; full text in detail drawer; tooltip on hover |
| Evidence | `evidence_status` | ▲▼ | Badge: `bg-green-100 text-green-700` Uploaded / `bg-red-100 text-red-700` Missing |
| Submitted By | `submitted_by_name` | ▲▼ | Name of submitter |
| Approval Status | `approval_status` | ▲▼ | Colour-coded badge (see §5.4) |
| Actions | — | — | `[View]` · `[Approve]` (Role 99; Pending Review only) · `[Reject]` (Role 99; Pending Review only) · `[Edit]` (Role 99; Approved or group-initiated) · `[Archive]` (Role 99; Completed/Approved only) |

**Default sort:** `date_held` DESC (most recent first).
**Pagination:** 25 rows per page. Controls: `« Previous  Page N of N  Next »`. Rows-per-page: 25 / 50 / 100.

**Slide-in Filter Drawer (360 px):**

| Filter | Control | Options |
|---|---|---|
| Branch | Multi-select checkbox | All branches; searchable |
| Event Type | Multi-select checkbox | All types from §5.3 |
| Approval Status | Multi-select checkbox | Approved / Pending Review / Rejected |
| Evidence | Radio | All / Uploaded / Missing |
| Date Range | Dual date picker | Applied to `date_held` |
| Academic Year | Select | Current AY + previous 2 AYs |
| Record Source | Radio | All / Group-Initiated / Branch-Reported / External |

Active filter chips above table; `[Reset All Filters]` clears and refreshes.

### 5.2 Pending Review Panel

Collapsible panel displayed directly above the main table when `approval_status = pending_review` count > 0.

**Panel header:** "Branch-Reported Events Pending Review — [N] record(s)" with amber icon. `[▸ Expand]` / `[▾ Collapse]` toggle. When collapsed, just the header bar is visible.

When expanded, shows the same main table but pre-filtered to `approval_status = pending_review`, with a prominent `[Approve]` and `[Reject]` button per row. Pagination: 10 rows; `[View All Pending]` links to main table with filter applied.

The panel updates via HTMX independently of the main table — after an approve or reject action, the panel refreshes its own row count badge without requiring a full page reload.

### 5.3 Event Type Colour Map

| Event Type | Badge Classes (Tailwind) |
|---|---|
| Annual Day | `bg-amber-100 text-amber-800` |
| Inter-Branch Competition | `bg-blue-100 text-blue-800` |
| Debate / Quiz | `bg-teal-100 text-teal-800` |
| Cultural Fest / Mela | `bg-violet-100 text-violet-800` |
| External Competition | `bg-orange-100 text-orange-800` |
| Workshop / Seminar | `bg-gray-100 text-gray-700` |
| NSS/NCC Event | `bg-green-100 text-green-800` |
| Talent Show | `bg-pink-100 text-pink-800` |
| Branch Cultural Event | `bg-slate-100 text-slate-700` |
| Other | `bg-zinc-100 text-zinc-700` |

### 5.4 Approval Status Colour Coding

| Status | Badge Classes | Description |
|---|---|---|
| Approved | `bg-green-100 text-green-700` | Reviewed and accepted; included in group record |
| Pending Review | `bg-amber-100 text-amber-700` | Branch-submitted; awaiting Cultural Head review |
| Rejected | `bg-red-100 text-red-700` | Not accepted; reason recorded; branch may resubmit |

Group-initiated records are set to Approved automatically on creation and display an "Auto-Approved" note in the detail view.

---

## 6. Drawers & Modals

### 6.1 `event-record-create` Drawer — 680 px, right-slide

**Trigger:** `[+ New Record]` header button. Role 99 only.

**Header:**
```
New Cultural Event Record
Records created here are automatically approved. Use this for group-initiated events.
```

**Tab 1 — Details**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Event Name | Text input | Yes | Min 3, max 150 characters |
| Branch | Select | Yes | All active branches in group; "Group HQ / Group-Wide" option for multi-branch events |
| Event Type | Select | Yes | All types from §5.3 |
| Date Held | Date picker | Yes | Cannot be a future date |
| Duration | Text input | No | Max 50 chars; free text, e.g. "Full Day" / "2 hours" |
| Venue | Text input | No | Max 150 characters |
| Audience Type | Select | Yes | Students Only / Students + Parents / Students + Parents + Staff / Open to Public |
| Outcome / Result Summary | Textarea | Yes | Min 50, max 1000 characters; describe what happened and the outcome |
| External Event? | Toggle | No | Default off; when on, shows External Event Name and External Organizer fields |
| External Event Name | Text input | Conditional | Max 150 chars; required if External Event toggle is on |
| External Organizer | Text input | Conditional | Max 150 chars |

**Tab 2 — Participants**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Total Attendance | Number input | Yes | Positive integer; sum of all attendees |
| Students Count | Number input | Yes | Positive integer; must be ≤ Total Attendance |
| Staff Count | Number input | No | Positive integer |
| Guests / Judges Count | Number input | No | Positive integer |
| Award Winners List | Textarea | No | Max 1000 chars; free text listing names and awards; e.g. "1st Prize — Aisha Verma (Cl 11A, Branch X)" |

Inline validation: Students Count + Staff Count + Guests / Judges Count should not exceed Total Attendance; if exceeded, an inline warning is shown but save is not blocked (to allow for rounding / crowd estimates).

**Tab 3 — Budget**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Budget Allocated (₹) | Currency input | No | Positive decimal, 2 dp |
| Actual Expenditure (₹) | Currency input | No | Positive decimal, 2 dp |
| Sponsor Name | Text input | No | Max 150 chars |
| Sponsor Amount (₹) | Currency input | No | Positive decimal, 2 dp; shown only if Sponsor Name is filled |
| Budget Notes | Textarea | No | Max 500 chars |

**Tab 4 — Evidence**

| Field | Type | Required | Validation / Notes |
|---|---|---|---|
| Photos | Multi-file image upload | No | JPG / PNG only; max 5 files; max 5 MB per file |
| Video Link | URL input | No | YouTube or Vimeo URL; validated as URL format |
| Newspaper / Media Coverage Link | URL input | No | Validated as URL format |
| Report Document | File upload | No | PDF only; max 10 MB |
| Certificate Copies | File upload | No | PDF only; max 10 MB total |

Evidence status is automatically set to "Uploaded" if at least one file or link is saved; "Missing" otherwise.

**Footer:** `[Cancel]`  `[Save Record]`

On save: `approval_status = approved` (auto-approved for Cultural Head); `record_source = group`.

---

### 6.2 `event-record-detail` Drawer — 680 px, right-slide

**Trigger:** Clicking event name in table, or `[View]` action button.

**Header:**
```
[Event Name]                                   [Edit ✎]  [Approve]  [Reject]  [Archive]  [×]
[Event Type badge]  ·  [Branch Name]  ·  [Date Held]
Approval Status: [badge]  ·  Submitted by: [Name]  ·  Source: [Group-Initiated / Branch-Reported / External]
```

`[Edit ✎]` — Role 99; visible when `approval_status = approved` or record is group-initiated.
`[Approve]` — Role 99; visible only when `approval_status = pending_review`.
`[Reject]` — Role 99; visible only when `approval_status = pending_review`; opens `reject-event` modal.
`[Archive]` — Role 99; visible when `approval_status = approved`; moves record to archived state (not deleted; excluded from default table view).

**Tab 1 — Overview**

Two-column layout of all Detail and Participants fields (read-only):

| Field | Notes |
|---|---|
| Event Name | — |
| Branch | Link to branch profile |
| Event Type | Badge |
| Date Held | — |
| Duration | — |
| Venue | — |
| Audience Type | — |
| Outcome / Result Summary | Full text; scrollable if long |
| External Event? | "Yes — [External Event Name] by [External Organizer]" or "No" |
| Total Attendance | — |
| Students Count | — |
| Staff Count | — |
| Guests / Judges Count | — |
| Award Winners List | Full text |
| Record Source | Group-Initiated / Branch-Reported / External |
| Approval Status | Badge + approved/rejected by name and date |
| Rejection Reason | Shown if status = Rejected; full text |
| Created By / Created At | Audit |
| Last Updated By / At | Audit |

**Tab 2 — Participants**

Repeats Participants block from Overview in a more prominent layout. Also shows the award winners list in a structured display if populated.

**Tab 3 — Budget**

| Field | Value |
|---|---|
| Budget Allocated (₹) | Amount or "Not recorded" |
| Actual Expenditure (₹) | Amount or "Not recorded" |
| Variance (₹) | Auto-calculated: Allocated − Actual; shown in green if under budget, red if over |
| Sponsor Name | — |
| Sponsor Amount (₹) | — |
| Notes | Full text |

**Tab 4 — Evidence**

| Element | Notes |
|---|---|
| Photos | Thumbnail grid (100×100 px); click opens full-size in new tab; "No photos uploaded" empty state if none |
| Video Link | Card with YouTube/Vimeo embed thumbnail; click opens in new tab |
| Newspaper / Media Coverage | Link displayed as clickable URL with external icon |
| Report Document | Download link with file name and size |
| Certificate Copies | Download link with file name and size |
| Evidence Status badge | "Uploaded" (green) / "Missing" (red) at top of tab |

For Role 99: `[Upload Additional Evidence]` button opens a mini upload form within the tab. For Role 97 and 100: read-only.

---

### 6.3 `reject-event` Modal — 420 px, centred

**Trigger:** `[Reject]` button in event-record-detail drawer header. Role 99 only; shown only when `approval_status = pending_review`.

**Header:**
```
Reject Event Record
The branch will be informed of the rejection reason.
```

| Field | Type | Required | Validation |
|---|---|---|---|
| Rejection Reason | Textarea | Yes | Min 20 characters; explain what is missing or incorrect |
| Return to Branch for Resubmission? | Checkbox | — | Default checked; if checked, branch sees a "Resubmit" option in branch portal; if unchecked, record is closed as Rejected with no resubmission path |

**Footer:** `[Go Back]`  `[Confirm Rejection]`

On confirm: `approval_status` → Rejected; `rejection_reason` and `rejected_by` stored; notification dispatched to branch if Return to Branch is checked.

---

## 7. Charts

Charts appear in a two-column row below the KPI bar and above the pending review panel. `[▸ Hide Charts]` / `[▾ Show Charts]` toggle collapses the row.

### 7.1 Event Count by Branch (Top 10 Most Active) — Bar Chart

| Property | Value |
|---|---|
| Chart type | Vertical bar (Chart.js 4.x) |
| Data | Count of approved event records per branch for current AY; top 10 branches by count |
| X-axis | Branch name (abbreviated) |
| Y-axis | Event count |
| Bar colour | Indigo; bars for the top 3 rendered in a slightly darker shade |
| Tooltip | "[Branch Name]: [N] events" |
| Footer note | "Showing top 10 of [N] total branches. [View Full Report]" link opens a modal with the full bar chart across all branches |
| HTMX load | `hx-get="/api/v1/cultural/events/charts/by-branch/"` `hx-trigger="load"` |

### 7.2 Events by Type Distribution — Donut Chart

| Property | Value |
|---|---|
| Chart type | Donut (Chart.js 4.x) |
| Data | Count of approved records per `event_type` for current AY |
| Segment colours | Match event type badge colours from §5.3 |
| Legend | Right-side legend with type name + count |
| Tooltip | "[Event Type]: [N] events ([N]%)" |
| Centre label | Total approved events count |
| HTMX load | `hx-get="/api/v1/cultural/events/charts/by-type/"` `hx-trigger="load"` |

---

## 8. Toast Messages

| Action | Toast Text | Type |
|---|---|---|
| Record created | "Event record '[Name]' saved and approved." | Success |
| Record updated | "Event record '[Name]' updated." | Success |
| Record approved | "Event '[Name]' from [Branch] has been approved and added to the register." | Success |
| Record rejected | "Event '[Name]' from [Branch] has been rejected. Branch notified." | Success |
| Record archived | "Event '[Name]' has been archived." | Info |
| Evidence uploaded | "Evidence added to '[Name]'." | Success |
| Export complete | "Event register exported to [format]." | Success |
| Approve — network error | "Could not approve record. Please try again." | Error |
| Reject — missing reason | "Please provide a rejection reason of at least 20 characters." | Error |
| Save — required field missing | "Please complete all required fields before saving." | Error |
| Record — server error | "Could not save record. Please try again." | Error |

---

## 9. Empty States

| Context | Illustration | Heading | Sub-text | Action |
|---|---|---|---|---|
| No records in current AY (full register) | Folder icon | "No Event Records This Year" | "No cultural events have been recorded for this academic year. Create the first record or wait for branch submissions." | `[+ New Record]` (Role 99 only) |
| No records match filters | Funnel icon | "No Records Match Filters" | "Try adjusting your filters or reset to see all records." | `[Reset Filters]` |
| Pending review panel — no pending records | Checkmark icon | "No Records Pending Review" | "All branch-submitted events have been reviewed. Great work." | — |
| Evidence tab — no evidence | Document icon | "No Evidence Uploaded" | "No photos, videos, or documents have been attached to this record." | `[Upload Additional Evidence]` (Role 99 only) |
| Budget tab — no budget data | Wallet icon | "No Budget Data" | "Budget details have not been recorded for this event." | `[Edit]` (Role 99 only) |
| Participants tab — no participant count | People icon | "No Participant Data" | "Attendance and participant counts have not been recorded." | `[Edit]` (Role 99 only) |
| Role 100 — filtered view with no NSS/NCC events | Flag icon | "No NSS/NCC Events Found" | "No NSS or NCC events are recorded in the register for this period." | — |

---

## 10. Loader States

| Context | Loader Behaviour |
|---|---|
| Initial page load | KPI bar: 4 shimmer cards. Charts row: 2 shimmer rectangles. Pending review panel: shimmer header bar. Table: 8 shimmer rows |
| Filter or search change | Table rows replaced by 6 shimmer rows + 20 px indigo spinner below toolbar |
| Event record detail drawer opening | Drawer slides in; shimmer tab bar + shimmer metadata rows; real content replaces on API response |
| Tab switching in drawer (lazy load) | Tab content replaced by shimmer rows while fetching |
| Evidence tab loading | Thumbnail grid shimmers until images confirmed reachable |
| `[Upload Additional Evidence]` — file upload | Per-file progress bar: "Uploading [filename]… [N]%" |
| `[Approve]` button click | Button → disabled + "Approving…" + spinner; re-enables on response |
| `[Confirm Rejection]` in modal | Modal button → disabled + "Rejecting…" + spinner; modal closes on success |
| Export | `[Export ↓]` disabled + "Preparing…" + spinner; file triggers download on ready |
| KPI auto-refresh | Cards pulse; values update in place without full shimmer |

---

## 11. Role-Based UI Visibility

| UI Element | Role 99 (Cultural Head) | Role 97 (Sports Director) | Role 100 (NSS/NCC Coord) | All Others |
|---|---|---|---|---|
| KPI Summary Bar | Full (all 4 cards) | Full | Full | Hidden |
| Charts row | Visible | Visible | Visible (filtered data) | Hidden |
| Event table — all rows | All records | All records | NSS/NCC Event type only | Hidden |
| Pending Review panel | Full — approve/reject actions | Visible — read-only | Hidden | Hidden |
| `[+ New Record]` button | Visible | Hidden | Hidden | Hidden |
| `[Export ↓]` button | Visible | Visible | Visible | Hidden |
| Filter drawer | Full options | Full options | Partial (Type filter pre-locked to NSS/NCC) | Hidden |
| `[View]` action | Visible | Visible | Visible | Hidden |
| `[Approve]` action | Visible (Pending only) | Hidden | Hidden | Hidden |
| `[Reject]` action | Visible (Pending only) | Hidden | Hidden | Hidden |
| `[Edit]` action | Visible (Approved only) | Hidden | Hidden | Hidden |
| `[Archive]` action | Visible (Approved only) | Hidden | Hidden | Hidden |
| Overview tab — all fields | Full | Full | Full | Hidden |
| Budget tab | Full | Visible (read-only) | Visible (read-only) | Hidden |
| Evidence tab — `[Upload Additional Evidence]` | Visible | Hidden | Hidden | Hidden |
| Reject modal | Visible | Hidden | Hidden | Hidden |
| Alert banners (§3.3) | Full | Full | Full (relevant only) | Hidden |

---

## 12. API Endpoints

### 12.1 List Event Records
```
GET /api/v1/cultural/events/
```

| Query Parameter | Type | Description |
|---|---|---|
| `branch` | string (multi) | Filter by branch ID(s); comma-separated |
| `event_type` | string (multi) | Filter by event type slug(s) |
| `approval_status` | string (multi) | `approved` · `pending_review` · `rejected` |
| `evidence` | string | `uploaded` · `missing` |
| `date_from` | date (YYYY-MM-DD) | Filter `date_held` from |
| `date_to` | date (YYYY-MM-DD) | Filter `date_held` to |
| `academic_year` | string | e.g. `2025-26`; defaults to current AY |
| `record_source` | string | `group` · `branch` · `external` |
| `search` | string | Searches `event_name`, `branch_name`, `submitted_by_name` |
| `page` | integer | Default 1 |
| `page_size` | integer | 25 · 50 · 100; default 25 |
| `ordering` | string | `-date_held` (default) · `date_held` · `event_name` · `branch_name` · `approval_status` |

Role 100 (NSS/NCC Coordinator): server enforces `event_type = nss_ncc_event` regardless of query params.

Response: `{ count, next, previous, results: [...] }`.

### 12.2 Create Event Record
```
POST /api/v1/cultural/events/
```
Body: `multipart/form-data` — all fields from §6.1 tabs Details, Participants, Budget, plus optional Evidence files (`photos[]`, `report_document`, `certificate_copies`) and links (`video_link`, `media_coverage_link`). Role 99 only.
Response: 201 Created — full record object; `approval_status = approved`.

### 12.3 Retrieve Event Record Detail
```
GET /api/v1/cultural/events/{event_id}/
```
Response: 200 OK — full record object including participants, budget, evidence metadata, audit fields.

### 12.4 Update Event Record
```
PATCH /api/v1/cultural/events/{event_id}/
```
Body: JSON / multipart — partial update. Role 99 only; rejected records return HTTP 403 (must approve first if resubmitted).
Response: 200 OK.

### 12.5 Approve Record
```
POST /api/v1/cultural/events/{event_id}/approve/
```
Body: `{}` (no body required). Role 99 only; record must have `approval_status = pending_review`.
Response: 200 OK — `{ "approval_status": "approved", "approved_by": "...", "approved_at": "..." }`.

### 12.6 Reject Record
```
POST /api/v1/cultural/events/{event_id}/reject/
```
Body: `{ "rejection_reason": "string", "return_for_resubmission": true }`. Role 99 only; record must have `approval_status = pending_review`.
Response: 200 OK — `{ "approval_status": "rejected", "rejection_reason": "...", "rejected_by": "...", "rejected_at": "..." }`.

### 12.7 Archive Record
```
POST /api/v1/cultural/events/{event_id}/archive/
```
Body: `{}`. Role 99 only; record must be Approved.
Response: 200 OK — `{ "archived": true }`. Archived records excluded from default listing; accessible via `?include_archived=true` filter.

### 12.8 Upload Additional Evidence
```
POST /api/v1/cultural/events/{event_id}/evidence/
```
Body: `multipart/form-data` — `photos[]` (JPG/PNG, max 5 files, 5 MB each), `report_document` (PDF, max 10 MB), `certificate_copies` (PDF), `video_link` (URL), `media_coverage_link` (URL). Role 99 only.
Response: 201 Created — updated evidence metadata.

### 12.9 Pending Review List (for Panel)
```
GET /api/v1/cultural/events/pending-review/
```
Returns records with `approval_status = pending_review`, paginated to 10 rows for the panel.
Query: `page`, `page_size` (default 10).

### 12.10 KPI Summary
```
GET /api/v1/cultural/events/kpi-summary/
```
Query: `academic_year` (optional).
Response: `{ "total_events_ay": N, "group_initiated": N, "pending_review": N, "external_events": N }`.

### 12.11 Chart Data
```
GET /api/v1/cultural/events/charts/by-branch/
GET /api/v1/cultural/events/charts/by-type/
```
Both accept optional `academic_year`.
`by-branch` response: `{ "labels": [...], "data": [...], "total_branches": N }` (sorted descending, top 10).
`by-type` response: `{ "labels": [...], "data": [...] }`.

### 12.12 Export
```
GET /api/v1/cultural/events/export/
```
Query: all filter params from §12.1 + `format` (`pdf` · `xlsx`).
Response: File download (`Content-Disposition: attachment`).

---

## 13. HTMX Patterns

### 13.1 KPI Bar Initialisation and Auto-Refresh
```html
<div id="register-kpi-bar"
     hx-get="/api/v1/cultural/events/kpi-summary/"
     hx-trigger="load, every 300s"
     hx-swap="innerHTML"
     hx-indicator="#kpi-spinner">
</div>
```

### 13.2 Event Table Initialisation
```html
<div id="cultural-event-register-table"
     hx-get="/api/v1/cultural/events/?page=1&page_size=25"
     hx-trigger="load"
     hx-swap="innerHTML"
     hx-indicator="#table-spinner">
</div>
```

### 13.3 Search (Debounced)
```html
<input type="text"
       id="register-search"
       name="search"
       placeholder="Search events, branches, submitters…"
       hx-get="/api/v1/cultural/events/"
       hx-trigger="keyup changed delay:400ms"
       hx-target="#cultural-event-register-table"
       hx-swap="innerHTML"
       hx-include="#filter-branch, #filter-type, #filter-approval-status,
                   #filter-evidence, #filter-date-from, #filter-date-to, #filter-ay">
```

### 13.4 Filter Application
```html
<select name="approval_status"
        id="filter-approval-status"
        hx-get="/api/v1/cultural/events/"
        hx-trigger="change"
        hx-target="#cultural-event-register-table"
        hx-swap="innerHTML"
        hx-include="#register-search, #filter-branch, #filter-type,
                    #filter-evidence, #filter-date-from, #filter-date-to, #filter-ay">
</select>
```

### 13.5 Event Record Detail Drawer Open
```html
<button hx-get="/htmx/cultural/events/{{ event_id }}/detail/"
        hx-target="#drawer-container"
        hx-swap="innerHTML"
        hx-trigger="click"
        class="text-indigo-600 hover:underline text-sm font-medium">
  View
</button>
```

### 13.6 Approve Record (Inline)
```html
<button hx-post="/api/v1/cultural/events/{{ event_id }}/approve/"
        hx-encoding="application/json"
        hx-target="#register-row-{{ event_id }}"
        hx-swap="outerHTML"
        hx-on::after-request="showToast(event); refreshKPI(); refreshPendingPanel();"
        class="text-green-600 hover:underline text-sm font-medium">
  Approve
</button>
```
Swapping `outerHTML` of the individual row allows the approval to update that row's status badge and actions in place without a full table reload.

### 13.7 Reject Record — Opens Modal, Then Submits
```html
<!-- Trigger button opens reject modal -->
<button hx-get="/htmx/cultural/events/{{ event_id }}/reject-modal/"
        hx-target="#modal-container"
        hx-swap="innerHTML"
        hx-trigger="click">
  Reject
</button>

<!-- Inside the modal, form submits the rejection -->
<form hx-post="/api/v1/cultural/events/{{ event_id }}/reject/"
      hx-encoding="application/json"
      hx-target="#register-row-{{ event_id }}"
      hx-swap="outerHTML"
      hx-on::after-request="closeModal(); showToast(event); refreshKPI(); refreshPendingPanel();">
</form>
```

### 13.8 Pending Review Panel Independent Refresh
```html
<div id="pending-review-panel"
     hx-get="/api/v1/cultural/events/pending-review/"
     hx-trigger="load, refreshPendingPanel from:body"
     hx-swap="innerHTML"
     hx-indicator="#pending-panel-spinner">
</div>
```
The `refreshPendingPanel` custom event is dispatched from the approve/reject HTMX after-request handlers, causing this panel to independently reload without affecting the main table.

### 13.9 Detail Drawer Tab Switching (Lazy Load)
```html
<button hx-get="/htmx/cultural/events/{{ event_id }}/tab/budget/"
        hx-target="#event-drawer-tab-content"
        hx-swap="innerHTML"
        hx-trigger="click">
  Budget
</button>
```
All four tabs (Overview / Participants / Budget / Evidence) load lazily on first click. Overview is pre-fetched when the drawer opens. The Evidence tab additionally shimmers thumbnail cells until image URL reachability is confirmed.

### 13.10 Evidence Upload (in Detail Drawer)
```html
<form hx-post="/api/v1/cultural/events/{{ event_id }}/evidence/"
      hx-encoding="multipart/form-data"
      hx-target="#evidence-tab-content"
      hx-swap="innerHTML"
      hx-indicator="#evidence-upload-progress"
      hx-on::after-request="showToast(event);">
</form>
```

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
