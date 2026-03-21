# J-07 — NPS & Voice of Customer

**Route:** `GET /csm/feedback/`
**Method:** Django `TemplateView` + HTMX part-loads
**Primary roles:** CSM (#53), CS Analyst (#93)
**Also sees:** Account Manager (#54) — own accounts + send for own; ISM (#94) — own accounts + send for own; Escalation Manager (#55) — read-only; Renewal Executive (#56) — read-only

---

## Purpose

Systematic voice-of-customer programme for 2,050 institutions. At scale, individual relationship memory fails — this page turns feedback into structured data. The CSM uses it to run quarterly NPS campaigns, triage detractors before they churn, identify promoters for case studies, and track CSAT trends over time. The CS Analyst uses it to model correlation between NPS and churn probability.

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| NPS KPI strip | `csm_nps_survey` aggregated (promoters/passives/detractors) for last complete quarter | 60 min |
| NPS trend chart | `csm_nps_survey` grouped by month for last 12 months | 60 min |
| CSAT trend chart | `csm_nps_survey` WHERE survey_type='RENEWAL_CSAT' grouped by month | 60 min |
| Score distribution chart | `csm_nps_survey.nps_score` histogram for current period | 60 min |
| NPS by segment chart | `csm_nps_survey` grouped by institution type for current period | 60 min |
| Survey table | `csm_nps_survey` JOIN `institution` JOIN `user` (sent_by) | 5 min |
| Verbatim panel | `csm_nps_survey.verbatim_feedback` WHERE verbatim_feedback IS NOT NULL | 5 min |
| Pending surveys | `csm_nps_survey` WHERE responded_at IS NULL AND link_expires_at > now() | 5 min |
| Follow-up required | `csm_nps_survey` WHERE follow_up_required=true | 5 min |

Cache key includes all filter params. `?nocache=true` for CSM (#53) and CS Analyst (#93).

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?period` | `this_quarter`, `last_quarter`, `last_6m`, `last_12m`, `custom` | `last_quarter` | Reporting window |
| `?from` | `YYYY-MM-DD` | — | Custom period start |
| `?to` | `YYYY-MM-DD` | — | Custom period end |
| `?survey_type` | `QUARTERLY_NPS`, `POST_ONBOARDING_NPS`, `RENEWAL_CSAT`, `EBR_FEEDBACK`, `AD_HOC` (comma-sep; case-insensitive — view normalises to uppercase before querying) | `all` | Filter survey type |
| `?category` | `promoter`, `passive`, `detractor` | `all` | Filter by promoter category |
| `?type` | `school`, `college`, `coaching`, `group` | `all` | Filter by institution type |
| `?follow_up` | `1` | — | Show only follow_up_required=true |
| `?pending` | `1` | — | Show only unanswered surveys |
| `?sent_by` | user_id | `all` | Filter by who sent the survey |
| `?sort` | `sent_at_desc`, `score_asc`, `score_desc`, `institution_name` | `sent_at_desc` | Survey table sort |
| `?page` | integer | `1` | Survey table page |
| `?export` | `csv` | — | Export filtered survey data (CSM + Analyst) |
| `?nocache` | `true` | — | Bypass Memcached (CSM + CS Analyst only) |

---

## HTMX Part-Load Routes

| Part | Route | Trigger |
|---|---|---|
| NPS KPI strip | `?part=nps_kpi` | Page load + period change |
| NPS trend chart | `?part=nps_trend` | Page load + period change |
| CSAT trend chart | `?part=csat_trend` | Page load + period change |
| Score distribution | `?part=score_dist` | Page load + filter change |
| NPS by segment | `?part=nps_by_segment` | Page load + period change |
| Survey table | `?part=survey_table` | Page load + filter change + sort + page |
| Verbatim panel | `?part=verbatim` | Page load + filter change + text search (300ms debounce, min 3 chars) |
| Pending surveys | `?part=pending` | Page load + auto-refresh every 10 min |
| Follow-up panel | `?part=followups` | Page load |

---

## Page Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  NPS & Voice of Customer   Period: [Last Quarter ▼]  [Send Survey] │
├────────────────────────────────────────────────────────────────────┤
│  NPS KPI STRIP (5 tiles)                                           │
├─────────────────────────┬──────────────────────────────────────────┤
│  NPS TREND CHART        │  CSAT TREND CHART                       │
│  (12 months, line)      │  (12 months, line)                      │
├─────────────────────────┴──────────────────────────────────────────┤
│  SCORE DISTRIBUTION     │  NPS BY INSTITUTION TYPE (grouped bar)   │
├─────────────────────────┴──────────────────────────────────────────┤
│  FILTER ROW                                                        │
│  SURVEY TABLE + PAGINATION                                         │
├────────────────────────────────────────────────────────────────────┤
│  VERBATIM FEEDBACK PANEL   │   PENDING & FOLLOW-UP PANEL           │
└────────────────────────────┴───────────────────────────────────────┘
```

---

## NPS KPI Strip (5 tiles)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ +38          │ │ 54           │ │ 18%          │ │ 62%          │ │ 43%          │
│ NPS Score    │ │ Responses    │ │ Detractor %  │ │ Promoter %   │ │ Response     │
│ (last qtr)   │ │              │ │              │ │              │ │ Rate         │
│ ↑+8 vs Q3   │ │ of 127 sent  │ │ (10 insts)   │ │ (35 insts)   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

- **NPS Score:** `(Promoters/Total × 100) - (Detractors/Total × 100)`. Scale: -100 to +100. Delta vs previous period. Green if ≥ 40, amber if 20–39, red if < 20.
- **Responses:** Count where `responded_at IS NOT NULL` in period. Sub-label: "of N sent".
- **Detractor %:** Count(DETRACTOR) / Count(responded) × 100. Red if > 20%.
- **Promoter %:** Count(PROMOTER) / Count(responded) × 100. Green if > 50%.
- **Response Rate:** Count(responded) / Count(sent) × 100. Target ≥ 30%.

Tiles shown in selected period. "last_quarter" = Q4 2025 (Oct–Dec 2025) if today is Q1 2026.

Note: NPS formula counts only `QUARTERLY_NPS` surveys by default; includes all NPS-type surveys if `?survey_type=all`. The NPS Score tile shows "— (no data)" if fewer than `csm_config['nps_min_kpi_responses']` (default: 10) responses exist for the period — this threshold is intentionally higher than the per-month trend chart threshold (5) because portfolio-wide KPIs require statistical credibility.

---

## NPS Trend Chart

Line chart (Chart.js) — 12 months of monthly NPS scores.

- X-axis: month labels (MMM YY)
- Y-axis: -100 to +100
- Dotted reference line at 0 (neutral)
- Solid reference line at +40 (good) and +70 (excellent)
- Data points: NPS score per month. Null (shown as gap with tooltip "Not enough responses — need ≥5 for trend") if < 5 responses for that month — per-month samples are naturally smaller; the ≥5 threshold is intentionally lower than the ≥10 threshold used for KPI tiles (which represent portfolio-wide quarterly aggregates requiring higher statistical confidence). A "low sample" indicator icon (⚠) shown on data points with 5–9 responses.
- Secondary bars (right Y-axis, 0–100): response count per month as grey bars

Hover tooltip: NPS score · Promoters% · Detractors% · Response count.

---

## CSAT Trend Chart

Line chart — 12 months of average `csat_score` (1–5 scale) from RENEWAL_CSAT and EBR_FEEDBACK surveys.

- X-axis: month labels
- Y-axis: 1.0 to 5.0
- Reference line at 4.0 (target)
- Data points: monthly avg CSAT. Null if 0 responses.

Hover tooltip: avg CSAT · response count · date range.

---

## Score Distribution Chart

Bar chart — distribution of NPS scores 0–10 for selected period.

```
Count
 12 │  ┌───┐       ┌───┐ ┌───┐
 10 │  │   │       │   │ │   │
  8 │  │   │   ┌───┤   │ │   │ ┌───┐
  6 │  │   │   │   │   │ │   │ │   │
  4 │  │   │   │   │   │ │   │ │   │ ┌───┐ ┌───┐
  2 │  │   │ ┌─┤   │   │ │   │ │   │ │   │ │   │
  0 └──┴───┴─┴─┴───┴───┴─┴───┴─┴───┴─┴───┴─┴───┴
       0   1  2   3   4   5   6   7   8   9  10
   [■ Detractor (0–6)]  [■ Passive (7–8)]  [■ Promoter (9–10)]
```

Bars coloured by range: red=0–6, amber=7–8, green=9–10.

---

## NPS by Institution Type

Grouped bar chart showing NPS score per institution type for selected period.

```
Coaching  [███████████████░░░░░]  +52
Colleges  [████████████░░░░░░░░]  +38
Schools   [█████████░░░░░░░░░░░]  +28
Groups    [██████░░░░░░░░░░░░░░]  +14
```

Horizontal bars sorted by NPS score descending. Shows N responses below each bar label on hover.

---

## Survey Table Filter Row

```
Type: [All ▼]  Category: [All ▼]  Institution type: [All ▼]  Sent by: [All ▼]
[Follow-up required □]  [Pending response □]
Period: [Last Quarter ▼]   [Apply]   [Clear]
Sort: [Sent date ▼]   Showing 127 surveys
```

---

## Survey Table

| Column | Description |
|---|---|
| Institution | Name (link → J-03 Feedback tab) + type badge |
| Survey Type | Badge: QUARTERLY_NPS / POST_ONBOARDING_NPS / RENEWAL_CSAT / EBR_FEEDBACK / AD_HOC |
| Sent To | Name + email (truncated) |
| Sent Date | Date (relative if < 7 days) |
| Score | NPS 0–10 or CSAT 1–5 with star icons. "Pending" if no response |
| Category | PROMOTER (green) / PASSIVE (amber) / DETRACTOR (red) / — if CSAT |
| Responded | Relative time or "Pending" |
| Follow-up | Yellow flag icon if `follow_up_required=true`; tick if resolved |
| Verbatim | First 80 chars of `verbatim_feedback` + [↓ expand] link. "—" if no text |
| Sent By | Sender avatar + name |
| Actions | [Mark Follow-up] [Resend] [View] |

**Pending survey row:** Score + Category columns show "—" in grey italic. Responded column shows "Pending (N days)" — red if > 7 days since sent.

**Expired survey row:** Shows "Expired" badge in Score column. [Resend] action available.

**[Mark Follow-up]:** Toggle `follow_up_required`. Inline PATCH. Changes icon from outline to solid yellow flag. Second click opens follow-up notes input: "Add a note about the required follow-up action:" → saves to `csm_nps_survey.follow_up_notes`.

**[Resend]:** Available for expired or pending surveys. Opens resend modal (same as Send Survey modal, pre-filled). Creates a new `csm_nps_survey` row with a fresh `survey_link_token` (`secrets.token_urlsafe(48)`). Old row updated: `superseded_by_id = new_row.id` (column defined in data model). Old token immediately invalidated — public survey endpoint rejects submissions to superseded tokens.

**[View]:** Opens Survey Detail Drawer.

---

## Survey Detail Drawer

```
┌──────────────────────────────────────────────────────────────────┐
│  QUARTERLY_NPS  ·  Delhi Public School               [Close ×]   │
├──────────────────────────────────────────────────────────────────┤
│  Sent to: Dr. Ramesh Kumar (principal@dps.edu)                   │
│  Sent by: Ananya K. (CSM)   ·   Sent: 2 Jan 2026                 │
│  Responded: 5 Jan 2026 (3 days later)                            │
│  Expires: 16 Jan 2026                                            │
├──────────────────────────────────────────────────────────────────┤
│  NPS Score: 9 / 10  ·  PROMOTER  ●●●●●●●●●○  (9/10)            │
├──────────────────────────────────────────────────────────────────┤
│  Verbatim feedback:                                              │
│  "EduForge has transformed how we run exams. The real-time       │
│   reports after each test help teachers adjust their teaching.   │
│   We'd love to see more question variety in the regional         │
│   language section."                                             │
├──────────────────────────────────────────────────────────────────┤
│  Follow-up required: No                                          │
│  [Mark follow-up required]                                       │
│                                                                  │
│  Follow-up notes: —                                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Send Survey Modal

```
┌──────────────────────────────────────────────────────────────────┐
│  Send Survey                                                     │
├──────────────────────────────────────────────────────────────────┤
│  Institution*   [Search institution...                    ]      │
│  Survey type*   [QUARTERLY_NPS                          ▼]       │
│  Send to (email)* [principal@dps.edu                    ]        │
│  Recipient name* [Dr. Ramesh Kumar                       ]       │
│  Custom message  [Optional personalised intro text       ]       │
│                                                                  │
│  Survey link expires 14 days after sending.                      │
│                                                                  │
│  ⚠  This institution has an active pending survey of the same    │
│     type (sent 2 Jan, not yet responded). Sending a new one will │
│     supersede the old link.  [Proceed ▼]                         │
│                                                                  │
│  [Cancel]                          [Send Survey]                 │
└──────────────────────────────────────────────────────────────────┘
```

**Validation:**
- Institution: required
- Survey type: required
- Email: required; valid format
- Recipient name: required; min 2 chars
- Guard: warns but does not block if existing pending survey for same institution + type

POST to `/csm/feedback/surveys/send/`. Triggers dispatch via **F-06 Notification Manager** — email for all institution types; additionally sends WhatsApp via F-06 if `survey_type = QUARTERLY_NPS` and institution_type = `COACHING` (coaching centres have significantly higher WhatsApp open rates than email).

---

## Verbatim Feedback Panel

Below the survey table. Shows all verbatim responses for the selected period with filter controls.

```
┌──────────────────────────────────────────────────────────────────┐
│  Verbatim Feedback (38 responses)                                │
│  Category: [All ▼]  Type: [All ▼]  Sort: [Newest ▼]             │
│                                                                  │
│  PROMOTER · Delhi Public School · 9/10 · 5 Jan 2026             │
│  "EduForge has transformed how we run exams. The real-time..."   │
│  [Read more ↓]   [Flag follow-up]                               │
│  ─────────────────────────────────────────────────────           │
│  DETRACTOR · Excel Coaching Hub · 3/10 · 12 Jan 2026            │
│  "The platform lags during peak exam hours. We lost 15           │
│   minutes in our last mock test. Students were upset."           │
│  [Read more ↓]   [Flag follow-up]   [Create Escalation ↗]       │
│  ─────────────────────────────────────────────────────           │
│  ...                                                             │
└──────────────────────────────────────────────────────────────────┘
```

DETRACTOR verbatim: highlighted with red-50 background. [Create Escalation ↗] button visible to CSM and Escalation Manager — pre-fills escalation drawer with institution and summary from verbatim.

[Read more ↓]: expands full verbatim text inline.

Sorted newest first by default. Filter by category (PROMOTER/PASSIVE/DETRACTOR), survey type, institution type.

**Text search:** `[🔍 Search verbatim feedback...]` — searches `verbatim_feedback` using PostgreSQL full-text search (`to_tsvector('english', verbatim_feedback) @@ plainto_tsquery('english', ?)`) with 300ms debounce. Min 3 chars. Highlights matching terms in results using `<mark>` tags. Useful for surfacing themes (e.g., searching "pricing" to find all price-related detractor feedback before a renewal negotiation).

**Empty state:** "No verbatim feedback received for the selected period."

---

## Pending & Follow-up Panel

Two-column panel at bottom right.

**Left: Pending Surveys**

```
  Pending (no response):    42 of 127 sent
  ─────────────────────────────────────
  Delhi Coaching Hub   Sent 10 Jan (11d ago)  [Resend]
  Victory College      Sent 12 Jan (9d ago)   [Resend]
  Excel Institute      Sent 15 Jan (6d ago)   —
  [View all pending →]
```

[Resend] available after 7 days of no response.

**Right: Follow-up Required**

```
  Follow-ups pending:   5
  ─────────────────────────────────────
  Sunrise Academy    DETRACTOR 2/10  "Platform unstable"  [View]
  Hyderabad Hub      DETRACTOR 4/10  "Missing features"   [View]
  [View all follow-ups →]
```

[View] opens the Survey Detail Drawer.

---

## Bulk NPS Dispatch (Celery Task J-3 control)

Available to CSM (#53) only. Shows current quarter's dispatch schedule:

```
┌──────────────────────────────────────────────────────────────────┐
│  Quarterly NPS Dispatch — Q1 2026 (Jan–Mar)                      │
│                                                                  │
│  Status: Completed on 1 Jan 2026, 10:00 IST                      │
│  Sent: 127 surveys · Skipped: 18 (surveyed < 60 days ago)        │
│  Next dispatch: 1 Apr 2026, 10:00 IST (in 11 days)               │
│                                                                  │
│  [Preview Next Batch]  (shows which institutions will be included)│
│  [Skip Next Dispatch]  (requires confirmation + reason note)     │
└──────────────────────────────────────────────────────────────────┘
```

[Preview Next Batch] → modal listing institutions that Task J-3 will survey on next run: HEALTHY + ENGAGED institutions not surveyed in last 60 days.

[Skip Next Dispatch] → confirmation dialog: "Skip the Q2 2026 NPS dispatch? This cannot be undone." POST to `/csm/feedback/dispatch/skip/`.

---

## Export CSV

Filename: `eduforge_nps_feedback_YYYY-MM-DD.csv`

Columns: survey_id, institution_id, institution_name, institution_type, survey_type, sent_to_email, sent_to_name, sent_by, sent_at, responded_at, nps_score, csat_score, promoter_category, verbatim_feedback, follow_up_required, follow_up_notes

Available to CSM (#53) and CS Analyst (#93).

---

## Empty States

| Condition | Message |
|---|---|
| No surveys in period | "No surveys sent in this period." with [Send Survey] button |
| No verbatim responses | "No verbatim feedback received for the selected period." |
| No follow-ups pending | "No follow-ups required." with green checkmark |
| No pending surveys | "All surveys have been responded to." |

---

## Role-Based UI Visibility Summary

| Element | 53 CSM | 54 AM | 55 Escalation | 56 Renewal | 93 Analyst | 94 ISM |
|---|---|---|---|---|---|---|
| Full NPS charts + KPIs | Yes | Yes | Read | Read | Full + export | Read |
| Survey table | All surveys | Own sent | All (read) | All (read) | All | Own sent |
| Send survey | All institutions | Own accounts | No | No | No | Own accounts |
| Resend survey | Yes | Own | No | No | No | Own |
| Mark follow-up | Yes | Own | No | No | No | Own |
| Create escalation from verbatim | Yes | No | Yes | No | No | No |
| Bulk dispatch control (Task J-3) | Yes | No | No | No | No | No |
| Export CSV | Yes | No | No | No | Yes | No |
| [?nocache=true] | Yes | No | No | No | Yes | No |
