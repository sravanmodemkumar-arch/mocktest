# O-03 — Recruitment Pipeline

**Route:** `GET /hr/recruitment/`
**Method:** Django `TemplateView` + HTMX part-loads
**Primary roles:** Recruiter (#80), HR Manager (#79)
**Also sees:** Hiring managers in each division — read-only for positions in their division (interview feedback input only, via separate interview feedback form at `GET /hr/interview/{token}/`)

---

## Purpose

End-to-end applicant tracking for EduForge's internal recruitment across all 15 divisions and 106+ roles. At any growth phase, the Recruiter manages multiple concurrent open positions across technical (engineering, content, AI/ML) and non-technical (sales, support, HR) functions. This page provides pipeline visibility (kanban + table view), candidate management, interview coordination, offer lifecycle, and time-to-hire analytics — all without an external ATS subscription.

Avg hiring volumes (est.):
- Phase 2 → Phase 3 transition: ~20–30 new hires in 6 months
- Phase 3 → Phase 4: ~40–70 new hires over 12 months
- Ongoing steady state: ~2–5 hires/month (replacement + growth)

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| Pipeline KPI strip | `hr_position` + `hr_candidate` aggregated by stage | 5 min |
| Position list | `hr_position` WHERE current_status IN ('OPEN','ON_HOLD') | 5 min |
| Candidate pipeline | `hr_candidate` JOIN `hr_position` JOIN `hr_interview` | 2 min |
| Kanban board | `hr_candidate` GROUP BY current_stage for each open position | 2 min |
| Offer pipeline | `hr_offer` WHERE offer_status IN ('DRAFT','SENT','ACCEPTED') | 2 min |
| Time-to-hire chart | `hr_employee` WHERE join_date in last 12 months — days from `hr_position.opened_at` to join_date | 30 min |
| Source mix chart | `hr_candidate` GROUP BY source for last 6 months | 30 min |
| Interview schedule | `hr_interview` WHERE scheduled_at BETWEEN now() AND now()+7d | 5 min |

Cache keys scoped to `(user_id, filters)`.

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?view` | `pipeline`, `positions`, `offers`, `analytics` | `pipeline` | Active tab |
| `?position_id` | UUID | — | Focus pipeline on a specific position |
| `?stage` | `applied`, `screening`, `interview_1`, `interview_2`, `final_round`, `offer`, `joined`, `rejected` | `all` | Filter candidates by stage |
| `?division` | A–O | `all` | Filter positions by division |
| `?source` | `linkedin`, `naukri`, `referral`, `website`, `campus`, `agency`, `internal` | `all` | Filter candidates by source |
| `?q` | string | — | Search: candidate name, email, position title |
| `?sort` | `applied_date_desc`, `applied_date_asc`, `name_asc`, `stage` | `applied_date_desc` | Table sort |
| `?page` | integer | `1` | Pagination (25 per page in table view) |
| `?export` | `csv` | — | Export filtered candidate list (HR Manager only) |

---

## HTMX Part-Load Routes

| Part | Route | Trigger | Target ID |
|---|---|---|---|
| Pipeline KPI strip | `?part=kpi` | Page load | `#o3-kpi-strip` |
| Kanban board | `?part=kanban&position_id={id}` | Position select + page load | `#o3-kanban` |
| Positions list | `?part=positions` | Tab click + filter change | `#o3-positions` |
| Offers list | `?part=offers` | Tab click | `#o3-offers` |
| Analytics charts | `?part=analytics` | Tab click | `#o3-analytics` |
| Candidate drawer | `?part=candidate_drawer&id={id}` | Card click / row click | `#o3-candidate-drawer` |
| Interview schedule | `?part=interview_schedule` | Page load + 5 min poll | `#o3-interview-schedule` |
| Add position modal | `?part=add_position_modal` | [+ Add Position] click | `#modal-container` |
| Add candidate modal | `?part=add_candidate_modal&position_id={id}` | [+ Add Candidate] click | `#modal-container` |
| Schedule interview modal | `?part=schedule_modal&candidate_id={id}` | [Schedule Interview] click | `#modal-container` |
| Offer modal | `?part=offer_modal&candidate_id={id}` | [Create Offer] click | `#modal-container` |
| Move stage HTMX | `POST /hr/recruitment/candidates/{id}/move/` | Drag-and-drop / [Move to] button | Inline swap |

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Recruitment Pipeline  [🔍 Search candidates, positions...]  [+ Add] │
├──────────────────────────────────────────────────────────────────────┤
│  KPI STRIP (5 tiles)                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  [Pipeline ▼] [Positions] [Offers] [Analytics]                      │
│  Position: [All Positions ▼]   Division: [All ▼]   Source: [All ▼]  │
├──────────────────────────────────────────────────────────────────────┤
│  KANBAN PIPELINE (horizontal scroll if needed)                      │
│  Applied │ Screening │ Interview 1 │ Interview 2 │ Final │ Offer     │
│  (N)     │ (N)       │ (N)         │ (N)         │ (N)   │ (N)       │
├──────────────────────────────────────────────────────────────────────┤
│  UPCOMING INTERVIEWS (next 7 days)                                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## KPI Strip (5 tiles)

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 8            │ │ 34           │ │ 2            │ │ 18.4 days    │ │ 24%          │
│ Open         │ │ Active       │ │ Pending      │ │ Avg Time     │ │ Offer        │
│ Positions    │ │ Candidates   │ │ Offers       │ │ to Hire      │ │ Acceptance   │
│ 3 critical   │ │ 5 this week  │ │ 1 lapsing    │ │ ↓2.3d vs Q4  │ │ Rate (90-d)  │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

**Tile 1 — Open Positions:** `COUNT(hr_position WHERE current_status='OPEN')`. Sub-label: "N critical" = positions open > 30 days with no candidate in interview stage. Red if critical > 3.

**Tile 2 — Active Candidates:** Total candidates across all active stages (excludes Rejected/Withdrawn/Joined). Sub-label: "N this week" = applied in last 7 days.

**Tile 3 — Pending Offers:** Offers in DRAFT or SENT state. Sub-label: "N lapsing" = offers sent > 5 days ago with no response. Amber if any lapsing.

**Tile 4 — Avg Time to Hire:** Average calendar days from `hr_position.opened_at` to `hr_employee.join_date` for hires in last 90 days. Delta vs prior 90-day period. Green if ≤ 30 days, amber if 31–45 days, red if > 45 days.

**Tile 5 — Offer Acceptance Rate:** `COUNT(ACCEPTED offers) / COUNT(SENT offers) × 100` for last 90 days. Green if ≥ 80%, amber if 60–79%, red if < 60%.

---

## Kanban Board

One column per pipeline stage. Horizontally scrollable.

**Stages (left to right):**
1. APPLIED — received application, not yet screened
2. SCREENING — initial phone/video screen
3. INTERVIEW_1 — technical or domain round 1
4. INTERVIEW_2 — technical or domain round 2
5. FINAL_ROUND — culture fit / HR / leadership round
6. OFFER — offer created or sent

Terminal states (not shown as columns, accessible via filter):
- JOINED — converted to employee
- REJECTED — eliminated at any stage
- WITHDRAWN — candidate withdrew

**Candidate Card:**

```
┌─────────────────────────────────────┐
│  Priya Sharma                       │
│  Senior Backend Engineer · Div C    │
│  📍 LinkedIn · Applied: 3 days ago  │
│  ★★★☆☆  Last interview: 18 Mar     │
│  [View] [Move to ▼] [Reject]        │
└─────────────────────────────────────┘
```

- Avatar (initials), name, target position, source badge (LinkedIn/Naukri/Referral/etc.)
- Days since applied (red if > 14 days stale in same stage with no activity)
- Star rating: avg of all interview feedback scores (1–5)
- [View]: opens Candidate Drawer
- [Move to ▼]: dropdown of next/previous stages. Stage transitions recorded with timestamp in `hr_candidate.stage_history` (JSONB array: `[{stage, moved_at, moved_by}]`)
- [Reject]: opens rejection reason modal → records reason, sends automated rejection email if candidate email on file

**Drag-and-drop:** Cards are draggable between stage columns. On drop: `POST /hr/recruitment/candidates/{id}/move/` with `new_stage`. Optimistic UI update with server confirmation.

**Position selector:** Dropdown at top filters kanban to show only candidates for selected position. Default: "All Open Positions" (aggregate view).

---

## Candidate Profile Drawer

```
┌──────────────────────────────────────────────────────────────────┐
│  Priya Sharma · Backend Engineer (Div C)         [Edit] [Reject] [×] │
│  📧 priya.s@gmail.com · 📞 +91-98765-XXXXX                       │
│  Source: LinkedIn · Applied: 18 Mar 2026 (3 days ago)            │
│  Current Stage: INTERVIEW_1   ⭐ Avg Score: 4.2 / 5              │
├──────────────────────────────────────────────────────────────────┤
│  [Profile] [Interviews] [Offer] [Timeline]                       │
└──────────────────────────────────────────────────────────────────┘
```

**Tab 1 — Profile**

```
  Current Company:    Infosys · 4 years
  Current CTC:        ₹12,00,000 p.a.
  Expected CTC:       ₹16,00,000 p.a.
  Notice Period:      60 days
  Location:           Hyderabad (open to relocation: Yes)

  Resume:    [📄 priya_sharma_resume.pdf]  [Download]
  LinkedIn:  [linkedin.com/in/priya-s]

  Recruiter Notes:
  "Strong Django background. HTMX experience a bonus. Culture fit
   seemed good on screening call — direct communicator, asks good Qs."
  [Edit Notes]
```

[Edit Notes]: Recruiter (#80) and HR Manager (#79) only. Notes saved inline.

**Tab 2 — Interviews**

```
  Stage             Date          Interviewer          Score   Outcome
  ─────────────────────────────────────────────────────────────────────
  Screening         15 Mar 2026   Recruiter (self)     4/5     PROCEED
  Interview 1       18 Mar 2026   Arjun K. (CTO)       4.5/5   STRONG_YES
  Interview 2       —             [Schedule →]          —       —
```

[Schedule Interview] → opens schedule modal:
- Select interview stage
- Select interviewer (dropdown of all active employees)
- Date + time picker
- Mode: IN_PERSON / VIDEO / TELEPHONIC
- Optional: add agenda / JD link

On schedule: sends calendar invite email to interviewer and candidate. Creates `hr_interview` record.

**Interview Feedback Form** (separate route `GET /hr/interview/{token}/` — accessible by interviewer without requiring Division O access):
- Structured rating (1–5) across 3–5 criteria (defined per position)
- Open-text strengths + concerns
- Recommendation: STRONG_YES / YES / NEUTRAL / NO / STRONG_NO
- Feedback submission auto-updates Candidate Drawer in real-time via Django Channels or on next poll

**Tab 3 — Offer**

```
  No offer created yet.
  [Create Offer]   (HR Manager only)
```

After offer creation:
```
  Offer Status: SENT
  ─────────────────────────────
  CTC Offered:     ₹16,00,000 p.a.
  Designation:     Backend Engineer · Grade L4
  Join Date:       1 May 2026
  Validity:        Expires 31 Mar 2026 (in 10 days)
  Sent On:         21 Mar 2026
  Sent Via:        Email (offer_letter.pdf)
  [Download Offer Letter]  [Resend]  [Mark Accepted]  [Mark Declined]
```

[Mark Accepted] → `hr_offer.offer_status='ACCEPTED'`; triggers onboarding checklist creation in O-04; candidate added to "upcoming joiners" in O-01 dashboard.

[Mark Declined] → records decline reason; optionally reopens position to next candidate.

**Tab 4 — Timeline**

Immutable stage history + activity log.

```
  21 Mar 2026   HR Manager      Offer sent (₹16L CTC)
  18 Mar 2026   Arjun K.        Interview 1 feedback — STRONG_YES (4.5/5)
  15 Mar 2026   Recruiter       Screening call — PROCEED (4/5)
  13 Mar 2026   Recruiter       Moved: APPLIED → SCREENING
  10 Mar 2026   System          Application received (LinkedIn)
```

---

## Positions Tab

```
  Open Positions (8)   On Hold (2)   Closed (14)

  ☐ │ Title │ Division │ Opened │ Open Days │ Candidates │ Stage │ Priority │ ···
```

| Column | Description |
|---|---|
| Title | Position title (link → opens position detail + filtered kanban) |
| Division | Division badge |
| Opened | Date position was opened |
| Open Days | Days since opened. Red if > 45 days open. |
| Candidates | Count of active (non-rejected) candidates |
| Stage | Furthest stage reached by any candidate |
| Priority | P1 (red) / P2 (amber) / P3 (grey) |
| ··· | [Edit] [Put on Hold] [Close Position] |

**Add Position Modal:**

```
┌──────────────────────────────────────────────────────────────────┐
│  Create Position                                                 │
├──────────────────────────────────────────────────────────────────┤
│  Position Title*      [Backend Engineer                ]         │
│  Division*            [C — Engineering               ▼]          │
│  Hiring Manager*      [Arjun Kumar (CTO)             ▼]          │
│  Headcount Approved*  [1        ]   Grade: [L4      ▼]           │
│  Employment Type*     [Full-Time (Permanent)         ▼]          │
│  Target Join Date     [2026-05-01                    ]           │
│  Priority*            [P1 — Critical                 ▼]          │
│  JD (paste or upload) [                              ]           │
│  Required Skills      [Django · PostgreSQL · AWS     ]  [+ Add]  │
│  Budget (CTC range ₹) [Min: 12L  Max: 18L            ]           │
│                                                                  │
│  [Cancel]                            [Create Position]           │
└──────────────────────────────────────────────────────────────────┘
```

**HR Manager approval gate:** Positions budget > ₹20L CTC require HR Manager sign-off before opening. If Recruiter creates: status = `PENDING_APPROVAL`. HR Manager sees pending positions in O-01 dashboard under Pending Approvals.

---

## Offers Tab

Table of all active offers (DRAFT / SENT / ACCEPTED / DECLINED / LAPSED).

| Column | Description |
|---|---|
| Candidate | Name + target position |
| CTC Offered | Annual CTC in ₹ |
| Offer Status | DRAFT / SENT / ACCEPTED / DECLINED / LAPSED |
| Sent Date | Date offer was sent |
| Expiry | Offer expiry date. Red if within 3 days. |
| Expected Join | Expected join date (on acceptance) |
| Actions | [View] [Resend] [Revoke] [Mark Accepted/Declined] |

LAPSED: system auto-marks offers as LAPSED after expiry date passes with no response (Task background logic via O-8 equivalent — no Celery task defined in the page, the offer status check runs via O-15 filing task at daily 08:00 or at page load for < 24h precision).

---

## Analytics Tab

```
┌──────────────────────────────────────────────────────────────────┐
│  Time to Hire (last 12 months)   │  Source Mix (last 6 months)   │
│  (bar chart, avg days per month) │  (donut chart by source)      │
├──────────────────────────────────┴───────────────────────────────┤
│  Stage Conversion Funnel (last 90 days)                          │
│  Applied(34) → Screening(22) → Int1(14) → Int2(8) → Offer(4) → Joined(3) │
├──────────────────────────────────────────────────────────────────┤
│  Offer Acceptance Trend (last 12 months, line chart)             │
└──────────────────────────────────────────────────────────────────┘
```

**Time to Hire Chart:** Bar chart — avg days from `hr_position.opened_at` to `hr_employee.join_date`, grouped by hire month. Reference line at 30 days.

**Source Mix Donut:** LinkedIn / Naukri / Referral / Website / Campus / Agency / Internal. Hover tooltip: source · count · % · avg time to hire from this source.

**Stage Conversion Funnel:** Horizontal funnel showing candidate drop-off at each stage. Conversion rate shown between stages (e.g., "64% proceed from Screening to Interview 1"). Useful for diagnosing bottlenecks.

**Offer Acceptance Trend:** Line chart of monthly offer acceptance rate (%). Reference line at 80%.

**Visible to:** HR Manager (#79) full; Recruiter (#80) full.

---

## Upcoming Interviews Panel

```
  Interviews this week: 7
  ─────────────────────────────
  Today
    Priya S.  Interview 2  Arjun K.  3:00 PM  VIDEO    [View candidate]
  Tomorrow
    Rahul M.  Screening    Recruiter  11:00 AM  VIDEO    [View candidate]
  22 Mar
    Kavya R.  Final Round  HR Manager 2:00 PM  IN_PERSON [View candidate]
```

[View candidate]: opens Candidate Drawer.

Auto-refreshes every 5 minutes.

**Visible to:** HR Manager (#79) and Recruiter (#80).

---

## Empty States

| Condition | Message |
|---|---|
| No open positions | "No open positions. Ready to hire? [+ Create Position]" |
| No candidates for position | "No candidates yet for this position. [+ Add Candidate]" |
| No pending offers | "No pending offers." |
| No upcoming interviews | "No interviews scheduled this week." |
| Analytics — insufficient data | "Not enough hiring data yet. Analytics available after 5+ hires." |

---

## Toast Messages

| Action | Toast | Type |
|---|---|---|
| Candidate added | "[Name] added to [Position] pipeline." | Green |
| Stage moved | "[Name] moved to [Stage]." | Green |
| Candidate rejected | "[Name] rejected. Rejection email queued." | Amber |
| Interview scheduled | "Interview scheduled for [date] with [interviewer]." | Green |
| Offer created | "Offer created for [Name]. Review and send." | Blue |
| Offer sent | "Offer sent to [Name]. Expires [date]." | Green |
| Offer accepted | "[Name] accepted the offer. Joining: [date]. Onboarding checklist created." | Green |
| Offer declined | "[Name] declined the offer." | Amber |
| Position created | "Position '[title]' created." | Green |

---

## Authorization

**Route guard:** `@division_o_required(allowed_roles=[79, 80])` applied to `RecruitmentView`. Hiring managers access interview feedback only via tokenised one-time form at `/hr/interview/{token}/` — this route does not require Division O membership.

| Scenario | Behaviour |
|---|---|
| [Create Offer] | HR Manager (#79) only; Recruiter (#80) sees button as disabled with tooltip "Offer creation requires HR Manager" |
| [Edit Position] | HR Manager (#79) only for budget/grade fields; Recruiter (#80) can edit JD, skills, hiring manager |
| Analytics tab | Both HR Manager (#79) and Recruiter (#80) |
| Export CSV | HR Manager (#79) only |
