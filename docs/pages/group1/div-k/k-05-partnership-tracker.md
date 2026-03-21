# K-05 — Partnership Tracker

**Route:** `GET /group1/k/partnerships/`
**Method:** Django `ListView` + HTMX part-loads + drawer-based detail
**Primary role:** Partnership Manager (#61)
**Also sees:** B2B Sales Manager (#57 — view + approve MoU status changes)

---

## Purpose

Track and manage government contracts, coaching chain MoUs, state board agreements, and institutional partnership deals. These are multi-institution agreements where a single signed contract can enable onboarding of 5–50+ institutions at once. A state board MoU can unlock 200+ schools; a coaching chain agreement can cover 28 centres in one stroke. This page is the Partnership Manager's primary workspace for pipeline management, document storage, expiry tracking, and renewal scheduling. It is also where the Sales Manager comes to approve status moves to MOU_SIGNED and ACTIVE.

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| KPI strip | `sales_partnership` aggregates | 5 min |
| Partnership table | `sales_partnership` | No cache — live |
| Document metadata | S3 object metadata via mou_s3_path | 10 min |
| Activity log (in drawer) | `partnership_activity` WHERE partnership_id | 5 min |
| Institutions covered | `sales_partnership.institutions_covered` (nightly Celery update) | No additional cache |
| Renewal calendar | `sales_partnership` WHERE mou_expires_at IS NOT NULL | 10 min |

---

## URL Parameters

| Param | Values | Effect |
|---|---|---|
| `?status` | `all`, `prospecting`, `negotiation`, `mou_signed`, `active`, `expired` | Filter by status; default shows all non-terminated active records |
| `?type` | `state_board`, `coaching_chain`, `govt_contract`, `ngo`, `university_affiliate`, `district_authority` | Filter by partner_type |
| `?territory` | Territory string | Filter by territory |
| `?expiry_within` | `30`, `60`, `90`, `any` | Filter by mou_expires_at window |
| `?q` | String | ILIKE search on partner_name |
| `?sort` | `name`, `contract_value`, `expiry`, `institutions` | Sort column; default `name` |
| `?page` | Integer | Pagination; 25 rows per page default |

---

## HTMX Part-Load Routes

| Route | Component | Trigger | Target ID |
|---|---|---|---|
| `htmx/k/partnerships/table/` | Partnership table | Filter/page change | `#k-partnerships-table` |
| `htmx/k/partnerships/<id>/activity/` | Activity log section | After new entry save | `#k-partnership-activity-{id}` |
| `htmx/k/partnerships/kpi/` | KPI strip | After status change, 5-min refresh | `#k-partnerships-kpi` |

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  PARTNERSHIP TRACKER             [+ Add Partnership]        │
├──────────┬──────────┬──────────┬──────────────────────────┤
│ Active   │ MoUs     │ Expiring │ Institutions              │
│ Partners │ Signed   │ <30 Days │ Covered                   │
│ 12       │ 8        │ 2        │ 340                       │
├──────────┴──────────┴──────────┴──────────────────────────┤
│  [Status▼] [Type▼] [Territory▼] [Expiry▼]  🔍 Search...  │
├───────────────┬──────────────┬────────┬──────┬────┬───────┤
│ Partner Name  │ Type         │ Status │ Insts│ MoU│Actions│
│               │              │        │ Cvrd │Exp.│       │
├───────────────┼──────────────┼────────┼──────┼────┼───────┤
│ AP State Board│ STATE_BOARD  │ ACTIVE │ 180  │Mar'27│[···]│
│ FIITJEE Chain │ COACHING_CHN │ MOU_SGN│ 28   │Jun'26│[···]│
│ DM Govt Tender│ GOVT_CONTRACT│ NEGOT. │ 0    │ —  │ [···] │
├───────────────┴──────────────┴────────┴──────┴────┴───────┤
│  Showing 1–12 of 12 partnerships             ← 1 →        │
└───────────────────────────────────────────────────────────┘
```

Below main table: [View Renewal Calendar] toggle button switches layout to calendar view.

---

## Components

### 1. KPI Strip

```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ 12               │ │ 8                │ │ 2                │ │ 340              │
│ Active Partners  │ │ MoUs Signed      │ │ Expiring <30d    │ │ Institutions     │
│ (Active+MOU_SGN) │ │ (incl. Active)   │ │ ⚠ 2 contracts    │ │ Covered          │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

- **Active Partners:** COUNT WHERE `status IN ('ACTIVE', 'MOU_SIGNED')`
- **MoUs Signed:** COUNT WHERE `status IN ('MOU_SIGNED', 'ACTIVE')` — this tracks how many have reached formal agreement stage
- **Expiring <30 Days:** COUNT WHERE `mou_expires_at BETWEEN now() AND now()+30d`. Amber tile if > 0; red tile if any have already expired without renewal. Red badge "N overdue" if any contract has `mou_expires_at < now() AND status NOT IN ('EXPIRED', 'TERMINATED')`.
- **Institutions Covered:** SUM `institutions_covered` WHERE `status='ACTIVE'`. Nightly Celery task updates this field from actual onboarded institution counts.

---

### 2. Filter Bar

```
[Status ▼]  [Type ▼]  [Territory ▼]  [Expiry Within ▼]  [🔍 Search partner name...]  [Clear All]
```

- **Status:** Multi-select — PROSPECTING / NEGOTIATION / MOU_SIGNED / ACTIVE / EXPIRED / TERMINATED
- **Type:** Multi-select — STATE_BOARD / COACHING_CHAIN / GOVT_CONTRACT / NGO / UNIVERSITY_AFFILIATE / DISTRICT_AUTHORITY
- **Territory:** Multi-select — dynamically populated from distinct territory values in the table
- **Expiry Within:** Dropdown — 30 days / 60 days / 90 days / Any
- **Search:** ILIKE on `partner_name`; 300ms debounce
- **Clear All:** Visible when any filter is non-default

---

### 3. Partnership Table

Sortable by name, contract_value, mou_expires_at, institutions_covered. 25 rows per page.

| Column | Detail |
|---|---|
| Partner Name | Text; row click opens Partnership Detail Drawer |
| Type badge | STATE_BOARD=blue / COACHING_CHAIN=orange / GOVT_CONTRACT=indigo / NGO=teal / UNIVERSITY_AFFILIATE=violet / DISTRICT_AUTHORITY=slate |
| Status badge | ACTIVE=green / MOU_SIGNED=teal / NEGOTIATION=amber / PROSPECTING=grey / EXPIRED=red / TERMINATED=dark-red |
| Institutions Covered | Integer; "0" in grey if PROSPECTING/NEGOTIATION |
| MoU Expiry | Formatted "Mar '27" or "Jun '26"; amber if <60d, red if <30d; "No MoU" (grey) if status is PROSPECTING or NEGOTIATION |
| State | Short state name |
| Contract Value | ₹ formatted (₹X.XL / ₹X.XCr); "—" if not yet set |
| Actions | 3-dot: View / Edit / Upload MoU / Change Status / Add Activity |

Row background: amber tint if MoU expiring within 30 days; red tint if expired but not in terminal status.

---

### 4. Add / Edit Partnership Drawer

Slide-in from right. Title: "Add Partnership" (new) or "Edit — [Partner Name]" (edit).

```
┌──────────────────────────────────────────────────────────────────┐
│  Add Partnership                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Partner Name*        [____________________________________]      │
│  Partner Type*        [STATE_BOARD                       ▼]      │
│  State*               [Andhra Pradesh                    ▼]      │
│  Territory*           [AP — Central                      ▼]      │
│                       (auto-suggested by state; editable)        │
│  Status*              [PROSPECTING                       ▼]      │
│                       Flow: PROSPECTING→NEGOTIATION→MOU_SIGNED   │
│                       →ACTIVE. Terminal: EXPIRED / TERMINATED.   │
│  Contract Value ₹     [_________]  (optional for PROSPECTING)    │
│  Institutions Covered [___]  (number this partnership covers)    │
│                                                                  │
│  — MoU Details (shown when status = MOU_SIGNED or ACTIVE) —     │
│  MoU Signed Date      [YYYY-MM-DD  ]                            │
│  MoU Expiry Date*     [YYYY-MM-DD  ]  (required if signed)      │
│  Annual Review Date   [YYYY-MM-DD  ]  (optional)                │
│                                                                  │
│  Notes                [Textarea — context, negotiations, etc.  ] │
│                                                                  │
│  [Cancel]                           [Save Partnership]          │
└──────────────────────────────────────────────────────────────────┘
```

**Validation:**
- Partner Name: required; min 3 chars; unique within active records (warn if similar name exists)
- Partner Type: required
- State: required
- Status: required; allowed transitions enforced (cannot jump from PROSPECTING to ACTIVE)
- MoU Expiry Date: must be after MoU Signed Date
- Contract value: must be ≥ 0 if provided
- Moving to MOU_SIGNED or ACTIVE via this form triggers a Sales Manager approval request (not immediate); status stays at previous value with "Pending approval" indicator until #57 approves

**MoU date validation rules:**
- MoU Expiry Date must be at least 6 months after MoU Signed Date (minimum meaningful partnership duration). If < 6 months: warning "This MoU expires very quickly — please confirm dates are correct." (soft warning, not hard block).
- MoU Expiry Date cannot be in the past (hard block with error "Cannot create an already-expired MoU. Set status to EXPIRED instead.").
- Annual Review Date: auto-suggested as 1 year after MoU Signed Date. Overridable. Cannot be after MoU Expiry Date.

On save: POST (new) or PATCH (edit) → refresh table + KPI strip + toast.

---

### 5. Partnership Detail Drawer

Opens on row click. Full-width slide-in from right. Tabbed sections within drawer.

**Header:**
```
AP State Board — Andhra Pradesh                        [ACTIVE]
STATE_BOARD  ·  Territory: AP — Central  ·  Owner: Priya Rao
Contract Value: ₹18.4L  ·  Institutions Covered: 180
```

**Section a — Key Metrics:**
| Field | Value |
|---|---|
| Contract Value | ₹18,40,000 |
| Institutions Covered | 180 (updated nightly) |
| MoU Signed | 15 Sep 2024 |
| MoU Expiry | 14 Mar 2027 (24 months remaining) |
| Annual Review | 15 Sep 2025 |
| Status | ACTIVE |

**Section b — Document Vault:**

List of uploaded documents linked to this partnership via `mou_s3_path`.

```
┌──────────────────────────────────────────────────────────────────┐
│  Documents                              [Upload MoU Document]    │
├──────────────────────────────────────────────────────────────────┤
│  📄 AP_StateBoard_MoU_2024.pdf                                    │
│  Uploaded: 16 Sep 2024 by Priya Rao · 2.3 MB                    │
│  [View ↗]  [Replace]                                             │
│                                                                  │
│  📄 AP_StateBoard_MoU_2024_Amendment1.pdf                        │
│  Uploaded: 2 Jan 2025 by Vikram Singh · 1.1 MB                  │
│  [View ↗]  [Replace]                                             │
└──────────────────────────────────────────────────────────────────┘
```

- **Upload MoU Document:** POST multipart to `/group1/k/partnerships/<id>/documents/upload/`. Accepted formats: PDF, DOC, DOCX. Max 20 MB. On success: saves to S3, stores path in `mou_s3_path`, updates document list via HTMX swap.
- **View:** Generates pre-signed S3 URL with 15-minute expiry. Opens in new tab.
- **Replace:** Renames existing file with `_v1`, `_v2` suffix before overwriting. Keeps version history.
- Empty state: "No documents uploaded. Upload the signed MoU to keep records current."

**Document versioning:** When a document is replaced, the old version is renamed with a `_v[N]` suffix in S3 (e.g., `mou_ap_state_board_v1.pdf`) and retained for 7 years (legal compliance — partnership contracts). The `sales_partnership.mou_s3_path` is updated to point to the new version. A changelog entry is added to the Activity Log: "MoU document replaced by [user] on [date] — previous version archived as v[N]."

Maximum document size: 20MB. Allowed types: PDF, DOC, DOCX. If wrong type: "Only PDF, DOC, DOCX files are accepted." If too large: "File exceeds 20MB. Please compress before uploading."

**Section c — Activity Log:**

Chronological log of interactions specific to this partnership. Newest first.

```
┌──────────────────────────────────────────────────────────────────┐
│  ● NEGOTIATION_SESSION   18 Mar 2026 · 10:00 AM   Priya Rao      │
│  "Second round discussion on revenue share model. Board          │
│   requested 15% fee waiver for first 100 schools."               │
│  Next: Circulate revised term sheet by 25 Mar                    │
│                                                                  │
│  ● CALL   14 Mar 2026 · 3:15 PM   Priya Rao                      │
│  "Initial call post MoU renewal — positive direction."           │
└──────────────────────────────────────────────────────────────────┘
[+ Log Activity]
```

Activity types available: CALL / MEETING / EMAIL / NEGOTIATION_SESSION / MOU_REVIEW / DOCUMENT_RECEIVED.

Each entry: activity type icon + label, logged_by, occurred_at, notes text (truncated, expand). [Edit] visible to activity author and #57.

HTMX retargets activity log section on new entry save.

**Log Activity form (inline, collapses after save):**
```
Type*       [CALL                    ▼]
Date/Time*  [2026-03-21  ]  [14:00  ]
Notes       [What happened?          ]
Next Action [Next step               ]  Due: [date]
[Save Activity]
```

**Section d — Status Change Controls:**

```
Current Status: MOU_SIGNED                [Change Status ▼]
```

Status change flow:
- Partnership Manager (#61): can move PROSPECTING → NEGOTIATION without approval
- Partnership Manager (#61): moves to MOU_SIGNED or ACTIVE require Sales Manager approval
- Sales Manager (#57): sees "Pending Approval" badge; can [Approve] or [Reject with reason] inline
- All status changes require a mandatory reason note (textarea, min 20 chars)
- Terminal moves (EXPIRED, TERMINATED) require #57 approval; sends notification to division lead

**Status change modal:**
```
┌──────────────────────────────────────────────────────────────────┐
│  Change Status — AP State Board                                  │
├──────────────────────────────────────────────────────────────────┤
│  Current:  MOU_SIGNED                                            │
│  Move to:  [ACTIVE              ▼]                               │
│  Reason*   [Describe the basis for this status change       ]    │
│            (min 20 chars; required)                              │
│                                                                  │
│  ℹ This change requires Sales Manager approval.                  │
│    An approval request will be sent to the Sales Manager.        │
│                                                                  │
│  [Cancel]                      [Submit for Approval]            │
└──────────────────────────────────────────────────────────────────┘
```

**Section e — Linked Leads:**

Shows `sales_lead` records where `institution_type` and `territory` match this partnership and where `stage = CLOSED_WON`. Provides context on how many institutions from this partnership have already been onboarded.

```
Institutions Onboarded via This Partnership
Linked Won Deals: 22 institutions
[View all →]  (links to Pipeline filtered by partner_id if is_channel_deal / territory match)
```

---

### 6. Renewal Calendar

Toggles from list view. Title: "Renewal Calendar — MoU Expiry Dates".

**Monthly calendar grid:**
- Each day cell shows dots or compact cards for MoU expiry dates falling on that day
- Colour coding: red = expired (past) / amber = <30 days / yellow = 30–90 days / green = >90 days
- Click any day with data → opens a popover showing the partnership(s) expiring that day with [Open] link to drawer

**List/Calendar toggle:**
```
[≡ List View]  [📅 Calendar View]   Month: [March 2026 ◀ ▶]
```

**Export Renewal Schedule:**
[Export CSV] button at top right of calendar section. Generates CSV with columns:
- Partner Name, Partner Type, State, Territory, Contract Value, MoU Expiry Date, Days Until Expiry, Owner, Status

Download filename: `renewal-schedule-[YYYY-MM].csv`.

**Renewal Schedule CSV export columns:** Partner Name | Partner Type | Status | State | Territory | MoU Signed Date | MoU Expiry Date | Annual Review Date | Days Until Expiry | Contract Value ₹ | Institutions Covered | Owner (Partnership Manager name) | Notes (truncated to 100 chars).
Export is synchronous (max ~200 rows typical — no async needed for partnerships volume).

**Empty state:** "No MoU expiry dates scheduled. Add MoU details when creating or editing a partnership."

---

## Empty States

| Section | Condition | Message |
|---|---|---|
| Partnership table | No records match current filters | "No partnerships match the current filters. Try clearing some filters." |
| Partnership table (first use) | Table is empty | "Start building your partnership pipeline. Add the first government or chain partnership." |
| Document Vault | No documents uploaded | "No documents uploaded. Upload the signed MoU to keep records current." |
| Activity Log | No activities logged | "No activity logged for this partnership yet." |
| Linked Leads section | No matching won deals | "No institutions onboarded via this partnership yet." |
| Renewal Calendar | No expiry dates set | "No partnerships expiring in the selected period." |
| Expiring <30d KPI | Count is zero | "No partnerships expiring in the next 30 days." |

---

## Toast Messages

| Action | Toast |
|---|---|
| Partnership added | "Partnership added: AP State Board" (green) |
| Partnership updated | "Partnership updated: AP State Board" (green) |
| Status change submitted | "Status change to ACTIVE submitted for Sales Manager approval" (blue) |
| Status change approved | "AP State Board moved to ACTIVE — approved by Vikram Singh" (green) |
| Status change rejected | "Status change rejected: [rejection reason]" (red) |
| MoU document uploaded | "MoU document uploaded for AP State Board" (green) |
| Upload error (size) | "File too large. Maximum allowed size is 20 MB." (red) |
| Upload error (type) | "Invalid file type. Only PDF, DOC, and DOCX are accepted." (red) |
| Activity logged | "Activity logged for AP State Board" (green) |
| Renewal CSV exported | "Renewal schedule downloaded" (green) |

---

## Role-Based View Summary

| Feature | #61 Partner Mgr | #57 Sales Mgr | All other roles |
|---|---|---|---|
| View partnership table | Yes — all | Yes — all | No access |
| Add new partnership | Yes | No | No |
| Edit partnership details | Yes | No | No |
| Change status (PROSP→NEGOT) | Yes — immediate | Yes — immediate | No |
| Change status (→MOU_SIGNED or ACTIVE) | Submits for approval | Approves / rejects | No |
| Change status (→EXPIRED / TERMINATED) | Submits for approval | Approves / rejects | No |
| Upload MoU document | Yes | No | No |
| View MoU document | Yes | Yes | No |
| Log partnership activity | Yes | No | No |
| View activity log | Yes | Yes | No |
| View renewal calendar | Yes | Yes | No |
| Export renewal CSV | Yes | Yes | No |
| Linked Leads section | Yes | Yes | No |
