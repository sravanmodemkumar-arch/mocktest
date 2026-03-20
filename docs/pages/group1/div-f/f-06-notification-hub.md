# F-06 — Notification Hub

> **Route:** `/ops/exam/notifications/`
> **Division:** F — Exam Day Operations
> **Primary Role:** Notification Manager (37) — full control
> **Supporting Roles:** Results Coordinator (36) — send result-related broadcasts; Exam Operations Manager (34) — read + emergency broadcast approve; Platform Admin (10) — full
> **File:** `f-06-notification-hub.md`
> **Priority:** P1 — Manages communication to 74,000 students; quota mismanagement can silence result notifications

---

## 1. Page Name & Route

**Page Name:** Notification Hub
**Route:** `/ops/exam/notifications/`
**Part-load routes:**
- `/ops/exam/notifications/?part=kpi` — KPI strip
- `/ops/exam/notifications/?part=templates` — template management tab
- `/ops/exam/notifications/?part=broadcasts` — broadcasts tab
- `/ops/exam/notifications/?part=delivery-report&broadcast_id={id}` — delivery stats for a broadcast
- `/ops/exam/notifications/?part=quota-dashboard` — quota monitoring tab
- `/ops/exam/notifications/?part=template-drawer&id={id}` — template edit drawer
- `/ops/exam/notifications/?part=broadcast-wizard` — broadcast create wizard

---

## 2. Purpose

F-06 is the central hub for all platform communications from EduForge to institutions and students. It manages:

1. **Template library** — WhatsApp/SMS/Email templates with DLT approval tracking
2. **Broadcast sends** — bulk sends to segmented audiences (all coaching centres, all SSC institutions, etc.)
3. **Delivery reporting** — per-broadcast delivery success rates, failures, opt-outs
4. **Quota monitoring** — daily WhatsApp (150K) and SMS (200K) limits with live tracking

**Scale reality check:**
- Result announcement broadcast: 74,000 WhatsApp messages in one send
- At 5,000 messages/min (rate limiter): a 74K send takes ~15 minutes
- Quota: 150K WhatsApp/day — a single large broadcast uses 50% of daily quota
- DLT registration: all SMS templates must have TRAI DLT pre-approval before activation; this takes 3–7 days per template

---

## 3. Tabs

| Tab | Label |
|---|---|
| 1 | Templates |
| 2 | Broadcasts |
| 3 | Delivery Reports |
| 4 | Quota Dashboard |

---

## 4. Section-Wise Detailed Breakdown

---

### KPI Strip

| # | KPI | Alert |
|---|---|---|
| 1 | Active Templates | Count of ACTIVE templates across all channels |
| 2 | Broadcasts Today | Count of broadcasts in SENDING or SENT today |
| 3 | WhatsApp Sent Today | Count vs 150K daily limit |
| 4 | SMS Sent Today | Count vs 200K daily limit |
| 5 | WhatsApp Quota Used | Percentage of daily limit; amber > 70%, red > 90% |
| 6 | Pending Broadcasts | APPROVED broadcasts awaiting send; amber if > 0 |

**Quota gauge visual:**
- KPI tile 5 renders as a thin progress bar below the percentage: green → amber → red

---

### Tab 1 — Templates

#### Template Filter Bar

| Filter | Control |
|---|---|
| Channel | Multi-select: WhatsApp · SMS · Email |
| Category | Multi-select: Result Release · Exam Reminder · OTP · Schedule Change · Admit Card · General · Payment Confirmation |
| Language | Multi-select: EN · HI · TE · UR |
| Status | Multi-select: Draft · Pending Approval · Approved · Active · Archived |
| DLT Registered | Yes · No · N/A (for non-SMS) |

#### Templates Table

| Column | Sortable | Notes |
|---|---|---|
| Name | Yes | Template display name |
| Code | No | `template_code` — unique identifier used in broadcasts |
| Channel | No | WhatsApp · SMS · Email icon |
| Category | No | — |
| Language | No | — |
| Char Count | No | For SMS: 160 = 1 SMS; 320 = 2 SMS; shown in amber if > 160 |
| DLT Status | No | ✅ Registered · ⚠️ Pending · — N/A |
| WhatsApp ID | No | Meta template ID (short) · — if not approved |
| Status | No | Status pill |
| Actions | — | [Edit] · [Preview] · [Duplicate] · [Archive] · [Activate] |

**[+ New Template]** (header button): opens Template Edit Drawer (640px).

**[Activate]:** shown when status = APPROVED. Moves to ACTIVE. Template becomes available in Broadcast wizard.

---

### Template Edit Drawer (640px)

**Header:** Template name or "New Template" · [×]

#### Section A — Template Metadata

| Field | Required | Validation |
|---|---|---|
| Name | Yes | Unique; max 100 chars |
| Template Code | Yes | Unique; alphanumeric + underscore; max 50 chars; auto-suggested from name |
| Channel | Yes | Select: WhatsApp · SMS · Email |
| Category | Yes | Select from enum |
| Language | Yes | Select: EN · HI · TE · UR |

#### Section B — Template Body

**For WhatsApp / SMS:**
- Large text area for `body_text`
- Variable syntax: `{{variable_name}}` — highlighted as amber chips
- Character counter (live): SMS shows "160 chars = 1 SMS; 320 = 2 SMS" with colour coding
- Variable list (below text area): each `{{variable}}` detected → shown as a row with: Variable name · Description field · Example value field. All three required for each variable.

**For Email:**
- Subject line field (required)
- Body: rich text editor (plain HTML — no WYSIWYG) or text area
- Preview: "Send test email" to a specified address

**Sample variable block:**
```
Body: "Dear {{institution_name}}, your student {{student_ref}} has scored {{score}} marks in {{exam_name}}."

Variables detected:
- institution_name — Description: "Institution display name" — Example: "Sri Chaitanya Academy"
- student_ref — Description: "Anonymised student reference" — Example: "STU-0042"
- score — Description: "Student's total marks" — Example: "87"
- exam_name — Description: "Full exam title" — Example: "SSC CGL Mock Test 5"
```

**Character count (SMS only):**
- Live count badge: "140 / 160 chars (1 SMS)"
- When > 160: "320 chars = 2 SMS — double cost" (amber)
- When > 480: "480+ chars = 3 SMS" (red warning)

#### Section C — DLT Registration (SMS only)

| Field | Notes |
|---|---|
| DLT Template ID | Text input — enter TRAI DLT registration ID once approved |
| DLT Approved Date | Date picker |
| DLT Entity ID | Platform-level; pre-filled from config |
| Sender ID | `EDUFGE` (locked — platform DLT sender ID) |

**Status workflow for SMS:**
1. `DRAFT` → writer fills template
2. `PENDING_APPROVAL` → submitted for TRAI DLT (external process, 3–7 days)
3. `APPROVED` → DLT ID entered; internal Notification Manager activates
4. `ACTIVE` → available for broadcasts

**DLT note:** Templates not DLT-registered will be rejected by SMS gateway. F-06 enforces: SMS template with `dlt_template_id = NULL` cannot be activated.

#### Section D — WhatsApp Registration (WhatsApp only)

| Field | Notes |
|---|---|
| Meta Template Name | Name as submitted to Meta Business Manager |
| WhatsApp Template ID | From Meta — entered after approval |
| WhatsApp Approved Date | Date picker |
| Template Category (Meta) | Utility · Authentication · Marketing — affects deliverability and cost |

#### Footer

[Save Draft] · [Submit for Approval] `bg-[#6366F1]` · [Preview Template] · (if APPROVED) [Activate]

---

### Tab 2 — Broadcasts

#### Broadcast Filter Bar

| Filter | Control |
|---|---|
| Status | Multi-select: Draft · Pending Approval · Approved · Queued · Sending · Sent · Failed · Partial · Cancelled |
| Channel | WhatsApp · SMS · Email |
| Date Range | Created / Sent at |
| Created By | My broadcasts / All |

#### Broadcasts Table

| Column | Sortable | Notes |
|---|---|---|
| Name | Yes | Broadcast label |
| Channel | No | — |
| Template | No | Template code |
| Target | No | e.g. "All Coaching" · "SSC Institutions" · "{N} specific" |
| Recipients | No | Total recipients count |
| Sent | No | Sent count (progress if SENDING) |
| Failed | No | Failed count |
| Status | No | Status pill; SENDING has pulse animation |
| Scheduled At | Yes | — |
| Created By | No | Role label |
| Actions | — | [View Report] · [Cancel] · [Retry Failed] |

**[+ New Broadcast]** (header): opens Broadcast Create Wizard.

**Progress display during SENDING:**
- Row shows: `{sent_count} / {total_recipients} sent` with thin progress bar
- HTMX auto-updates while status = SENDING: `hx-trigger="every 10s"` on SENDING rows only

---

### Broadcast Create Wizard (760px drawer — 4 steps)

#### Step 1 — Select Template

- Searchable list of ACTIVE templates (filtered by channel type selector at top)
- Each template shows: name · category · language · char count · DLT status
- Preview panel on the right: renders template with sample variable values

#### Step 2 — Define Recipients

**Target Type selector:**

| Target Type | Description |
|---|---|
| All Institutions | All 2,050 institutions |
| By Institution Type | School / College / Coaching / Online Domain |
| By Exam Type | All institutions registered for a specific exam domain |
| By Exam Schedule | Specific exam schedule (e.g., "All institutions running SSC Mock 5 today") |
| Specific Institutions | Multi-select list — search by name |
| By Subscription Plan | Starter / Standard / Professional / Enterprise |

**Recipient count estimate:** "Estimated recipients: {N}" — updates live as target type changes. Click [Calculate Exact Count] for precise DB query.

**Opt-out count:** "~{N} opted out — will be excluded from send"

**Final recipient count:** "Sending to: {total - opt_outs} recipients"

#### Step 3 — Variable Values

For each `{{variable}}` in the template, define how the value is resolved:

| Variable | Resolution Type | Notes |
|---|---|---|
| `{{institution_name}}` | Auto-mapped | System fills from institution record |
| `{{exam_name}}` | Auto-mapped | System fills from linked exam_schedule |
| `{{score}}` | Per-recipient DB field | System fills from exam_result per student |
| `{{exam_date}}` | Manual entry | "Enter value: [2026-04-10]" |
| `{{custom_message}}` | Manual entry | Static text applied to all recipients |

**Preview (sample):** Shows a sample rendered message with dummy values. Notification Manager must verify before proceeding.

#### Step 4 — Schedule & Review

| Field | Notes |
|---|---|
| Send When | Radio: Send Now · Schedule for Later |
| Scheduled At | Datetime picker (shown if Schedule for Later) |
| Broadcast Name | Auto-generated from template + date; editable |
| Internal Notes | Optional context note |

**Send summary:**
```
Channel: WhatsApp
Template: result_announcement_en (EN)
Recipients: 68,420 (after 580 opt-outs)
Estimated send time: ~14 min at 5,000/min rate
Quota impact: 68,420 of 150,000 daily quota (45.6%)
Quota remaining after send: ~81,580
```

**Quota warning** (if send would exceed daily quota): `bg-[#451A03] border-[#F59E0B]` — "⚠️ This broadcast will consume {N}% of today's remaining WhatsApp quota. Remaining after send: {N} messages."

**Hard block** if quota exceeded: "❌ Cannot queue — insufficient daily quota. Current remaining: {N}. Required: {N}. Wait for quota reset at midnight IST or contact Engineering for quota increase."

**[Save as Draft]** · **[Submit for Approval]** (if approval required) · **[Send Now]** (Notification Manager + Ops Manager only)

**Approval gate:** Broadcasts to > 10,000 recipients require approval by Ops Manager (34) or Notification Manager (37). Broadcasts to > 50,000 require explicit re-confirmation after quota check.

---

### Tab 3 — Delivery Reports

Per-broadcast delivery analytics.

**Select broadcast:** Searchable dropdown at top.

#### Delivery Summary Cards

| Card | Value |
|---|---|
| Total Recipients | {N} |
| Successfully Delivered | {N} ({X}%) |
| Failed | {N} ({X}%) |
| Opted Out (skipped) | {N} |
| Pending (not yet delivered) | {N} — shown during SENDING |

**Delivery Rate Over Time Chart:**
`LineChart` — cumulative sent count vs time (in minutes). Shows S-curve typical of bulk sends.

#### Failure Analysis

| Failure Reason | Count | % |
|---|---|---|
| Invalid number | {N} | — |
| Opted out | {N} | — |
| Carrier rejection | {N} | — |
| Template not approved by Meta (WA) | {N} | — |
| Rate limit exceeded | {N} | — |
| Other | {N} | — |

**[Retry Failed]** (available for PARTIAL/FAILED broadcasts within 24h): re-queues only the failed recipients. Opens confirmation modal with count + quota impact.

**[Export Delivery Report]** → CSV download: columns = channel · recipient_ref (anonymised) · status · failure_reason · sent_at. DPDPA: no phone numbers in export — only anonymised refs.

---

### Tab 4 — Quota Dashboard

Real-time view of WhatsApp and SMS daily quota usage.

#### Quota Gauges

For each channel (WhatsApp, SMS):

```
WhatsApp Daily Quota
[████████████████░░░░░░░░░░░░░░] 54% used (81,200 / 150,000)
Remaining: 68,800 messages
Resets at: midnight IST (12:00 AM = 00:00 IST)

Today's breakdown:
  - Result announcement broadcast: 74,000 sent
  - Schedule reminder (automated): 7,200 sent
  - Pending broadcasts: 0 queued
  - Reserved for OTP: 5,000 (always reserved)
```

**OTP reservation:** 5,000 WhatsApp/day reserved for OTP sends (authentication). This reservation cannot be consumed by broadcast sends. F-06 enforces this in the quota check before any send.

#### Quota History Chart

`BarChart` — last 30 days, daily quota used per channel (WhatsApp + SMS stacked or side-by-side).

Useful for planning: identifies exam announcement days (quota spikes) vs normal days.

#### Quota Alerts Config

| Alert | Threshold | Notification |
|---|---|---|
| WhatsApp 70% | 105,000 sent | In-app notification to Notification Manager (37) |
| WhatsApp 90% | 135,000 sent | In-app + amber banner in F-06 |
| SMS 70% | 140,000 sent | In-app |
| SMS 90% | 180,000 sent | In-app + amber banner |
| Quota at 95%+ | Any channel | Red banner in F-06 header: "⚠️ {Channel} quota critically low — {N} messages remaining today." |

---

## 5. Modals

### Send Now Confirmation Modal (480px)

**Trigger:** [Send Now] in Broadcast Wizard Step 4

"Send this broadcast now?

- Channel: WhatsApp
- Recipients: {N}
- Template: {template_code}
- Quota impact: {X}% of today's remaining quota

This action cannot be undone once sending begins."

[Confirm Send] `bg-[#6366F1]` · [Cancel]

### Cancel Broadcast Modal (400px)

Available for QUEUED or SENDING broadcasts.

"Cancel this broadcast?

- If QUEUED: No messages will be sent.
- If SENDING: Messages already sent ({N}) cannot be recalled. Only pending sends ({N}) will be cancelled."

[Confirm Cancel] `bg-[#EF4444]` · [Cancel]

### Retry Failed Modal (400px)

"Retry {N} failed messages from broadcast '{name}'?

- Quota impact: {N} messages ({X}% of remaining daily quota)
- Opt-outs will still be excluded"

[Retry Now] `bg-[#6366F1]` · [Cancel]

---

## 6. Data Model Reference

Full models in `div-f-pages-list.md`:
- `exam_notification_template` — template with DLT/WA registration fields
- `exam_notification_broadcast` — broadcast with progress tracking

**`exam_notification_delivery_log`** (F-06 delivery reports):
| Field | Type | Notes |
|---|---|---|
| `id` | bigint | Auto-increment — potentially 150K rows per broadcast |
| `broadcast_id` | FK → `exam_notification_broadcast` | — |
| `recipient_ref` | varchar(50) | Anonymised — DPDPA: no phone numbers stored |
| `channel` | varchar | — |
| `status` | varchar | Enum: `SENT` · `FAILED` · `OPT_OUT_SKIP` |
| `failure_reason` | varchar(100) | Nullable |
| `sent_at` | timestamptz | Nullable |

**`exam_notification_quota_daily`**:
| Field | Type | Notes |
|---|---|---|
| `id` | int | Auto-increment |
| `date` | date | Unique per date |
| `whatsapp_sent` | int | Default 0 — incremented by Celery per message batch |
| `sms_sent` | int | Default 0 |
| `email_sent` | int | Default 0 |

---

## 7. Access Control

| Gate | Rule |
|---|---|
| Page access | Notification Manager (37), Results Coordinator (36), Ops Manager (34), Platform Admin (10) |
| Create / edit templates | Notification Manager (37) |
| Activate templates | Notification Manager (37) |
| Create broadcasts | Notification Manager (37), Results Coordinator (36) — for result-related broadcasts |
| Send broadcasts < 10K recipients | Notification Manager (37) |
| Send broadcasts > 10K recipients | Notification Manager (37) + Ops Manager (34) approval |
| Cancel broadcasts | Notification Manager (37), Ops Manager (34) |
| Quota dashboard | All Div F roles read |
| Delivery reports | Notification Manager (37), Ops Manager (34) |

---

## 8. Edge Cases & Error States

| Scenario | Behaviour |
|---|---|
| WhatsApp template not approved by Meta | Cannot be activated. Status stays APPROVED (internally ready) but not ACTIVE. Banner: "Template awaiting Meta approval — check WhatsApp Business Manager." |
| SMS template missing DLT ID | Cannot be activated. Banner: "DLT Template ID required for SMS templates. Enter your TRAI DLT registration ID." |
| Broadcast quota exceeds daily limit | Hard block at wizard Step 4. Message: "Cannot queue — insufficient daily quota. Required: {N}. Remaining: {N}." |
| Broadcast sends during exam (high load) | Rate limiter still applies (5,000/min). Celery distributes load. No broadcast is allowed to suppress OTP quota (5K reserved). |
| Celery task failure mid-broadcast | Partial status set. `failed_count` shows failed batches. [Retry Failed] button appears. Notification Manager notified in-app. |
| Duplicate broadcast accidentally triggered | Detection: if same template + same target_type sent within last 2 hours, warning modal: "A broadcast with this template to this audience was sent {N} min ago. Send again?" |
| Opt-out list not updated | Opt-outs are sourced from platform DNC (Do Not Contact) table maintained by Notification Manager. If DNC table is stale: no system-level detection — Notification Manager is responsible for keeping it current. |

---

## 9. UI Patterns

### Toasts

| Action | Toast |
|---|---|
| Template saved | ✅ "Template saved as draft" (4s) |
| Template activated | ✅ "Template activated — available for broadcasts" (4s) |
| Broadcast queued | ℹ️ "Broadcast queued — sending starts shortly" (6s) |
| Broadcast sent (complete) | ✅ "Broadcast complete — {N} sent, {N} failed" (4s) |
| Broadcast cancelled | ✅ "Broadcast cancelled — {N} pending sends stopped" (4s) |
| Quota alert | ⚠️ "{Channel} quota at {N}% — {N} messages remaining today" (8s) |

### Responsive

| Breakpoint | Behaviour |
|---|---|
| Desktop (≥1280px) | Full table; wizard as 760px drawer; quota gauges side-by-side |
| Tablet | Reduced table; wizard full-width; quota gauges stacked |
| Mobile | Card layout; wizard = step-by-step full screen; quota = single gauge at a time |

---

*Page spec complete.*
*F-06 covers: template management (WhatsApp/SMS/Email, DLT tracking) → broadcast wizard (target, variables, quota check) → delivery reports → daily quota monitoring.*
