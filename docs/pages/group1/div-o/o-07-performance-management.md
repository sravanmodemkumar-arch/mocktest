# O-07 — Performance Management

**Route:** `GET /hr/performance/`
**Method:** Django `TemplateView` + HTMX part-loads
**Primary role:** HR Business Partner (#106)
**Also sees:** HR Manager (#79) — full access + calibration authority + PIP approval; Division managers — read-only for their own team's reviews, OKR input, and PIP involvement (via separate limited access, not Division O membership)

---

## Purpose

Structured performance management for all EduForge employees across OKR cycles, formal review cadences, calibration sessions, and Performance Improvement Plans. At 100–150 employees, informal feedback is unreliable — this page ensures every employee has documented OKRs, receives a formal mid-year and annual review, and that calibration decisions (ratings, increments, promotions) are consistent across divisions. The HRBP uses it daily during active review cycles; the HR Manager uses it for final calibration, increment approvals, and PIP oversight.

**Review cycle structure:**
- **Annual:** 1 April – 31 March (FY-aligned)
- **Mid-year checkpoint:** 1 October – 31 October (6-month progress review, no rating change)
- **Probation review:** At 3-month and 6-month marks from join date
- **Confirmation review:** At end of probation (typically 6 months) — outcome: CONFIRMED / EXTENDED / SEPARATED

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| Cycle status strip | `hr_performance_cycle` WHERE status NOT IN ('ARCHIVED') | 5 min |
| OKR overview | `hr_okr_objective` JOIN `hr_okr_key_result` for active cycle | 5 min |
| Review completion progress | `hr_performance_review` GROUP BY status for active cycle | 5 min |
| PIP list | `hr_pip` WHERE status NOT IN ('CLOSED') | 2 min |
| Employee reviews | `hr_performance_review` JOIN `hr_employee` for selected cycle | 5 min |
| Calibration grid | `hr_performance_review` WHERE cycle_id=active AND calibration_rating IS NOT NULL | 5 min |
| OKR detail | `hr_okr_objective` + `hr_okr_key_result` for selected employee+cycle | No cache |
| Review detail | `hr_performance_review` single row + `hr_okr_objective` for employee + cycle | No cache |

Cache keys scoped to `(user_id, cycle_id)`.

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?tab` | `overview`, `okrs`, `reviews`, `calibration`, `pips` | `overview` | Active section |
| `?cycle_id` | UUID | latest active | Select review cycle |
| `?division` | A–O | `all` | Filter employees by division |
| `?employee_id` | UUID | — | Jump to specific employee's review/OKR |
| `?review_status` | `not_started`, `self_assessment`, `manager_review`, `calibration`, `completed` | `all` | Filter reviews by status |
| `?pip_status` | `active`, `closed`, `all` | `active` | Filter PIPs by status |
| `?export` | `ratings_csv`, `okr_summary_csv` | — | Export (HR Manager only) |

---

## HTMX Part-Load Routes

| Part | Route | Trigger | Target ID |
|---|---|---|---|
| Overview strip | `?part=overview` | Page load | `#o7-overview` |
| OKR table | `?part=okrs&cycle_id={id}` | Tab click + filter | `#o7-okr-table` |
| Reviews table | `?part=reviews&cycle_id={id}` | Tab click + filter | `#o7-reviews-table` |
| Calibration grid | `?part=calibration&cycle_id={id}` | Tab click | `#o7-calibration` |
| PIP list | `?part=pips` | Tab click | `#o7-pip-list` |
| OKR drawer | `?part=okr_drawer&employee_id={id}&cycle_id={id}` | Row click | `#o7-okr-drawer` |
| Review drawer | `?part=review_drawer&review_id={id}` | Row click | `#o7-review-drawer` |
| PIP drawer | `?part=pip_drawer&pip_id={id}` | Row click | `#o7-pip-drawer` |
| Create cycle modal | `?part=create_cycle_modal` | [+ New Cycle] click | `#modal-container` |
| Create PIP modal | `?part=create_pip_modal&employee_id={id}` | [Initiate PIP] click | `#modal-container` |
| OKR check-in modal | `?part=checkin_modal&kr_id={id}` | [Check In] button | `#modal-container` |

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Performance Management   Cycle: [FY 2025-26 Annual ▼]  [+ Cycle]   │
├──────────────────────────────────────────────────────────────────────┤
│  CYCLE STATUS STRIP (cycle phase, deadlines, completion progress)    │
├──────────────────────────────────────────────────────────────────────┤
│  [Overview] [OKRs] [Reviews] [Calibration] [PIPs]                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Cycle Status Strip

```
┌──────────────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ FY 2025-26 Annual Review │ │ 64%            │ │ 82%            │ │ 2              │
│ Phase: Self-Assessment   │ │ OKRs with      │ │ Self-Assess    │ │ Active PIPs    │
│ Deadline: 31 Mar 2026    │ │ last check-in  │ │ Submitted      │ │                │
│ (in 10 days)             │ │ < 14 days      │ │ 92/112 emp.    │ │                │
└──────────────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘
```

**Phase badge (cycle phases in order):**
1. OKR_SETTING (green) — start of cycle: employees set objectives
2. OKR_ACTIVE (blue) — cycle in progress: regular check-ins expected
3. SELF_ASSESSMENT (amber) — self-assessment window open
4. MANAGER_REVIEW (purple) — managers complete their assessments
5. CALIBRATION (red) — HRBP + HR Manager calibration sessions
6. RESULTS_COMMUNICATED (teal) — ratings communicated to employees
7. CLOSED (grey) — cycle archived

Deadline countdown: red if ≤ 3 days to current phase deadline.

---

## Overview Tab

```
┌──────────────────────────────────────────────────────────────────────┐
│  FY 2025-26 Annual Review — Progress Summary                         │
├──────────────────────────────────────────────────────────────────────┤
│  REVIEW COMPLETION by Division                                       │
│  A Executive     4/4   ████████████████ 100%                        │
│  C Engineering   18/22 ████████████░░░░  82%   [View incomplete →]  │
│  D Content       10/13 ████████████░░░░  77%   [View incomplete →]  │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  SELF-ASSESSMENT: 92 submitted / 20 pending                          │
│  MANAGER REVIEW:  61 submitted / 51 pending                          │
│  CALIBRATION:     0 completed  / 112 pending                         │
├──────────────────────────────────────────────────────────────────────┤
│  [Send Reminder to Pending Employees]  [Send Reminder to Managers]   │
└──────────────────────────────────────────────────────────────────────┘
```

[Send Reminder to Pending Employees]: HTMX POST → sends email to all employees who haven't submitted self-assessment. Toast: "Reminder sent to [N] employees." HRBP (#106) can send; HR Manager (#79) can send.

---

## OKRs Tab

### OKR Table

| Column | Description |
|---|---|
| Employee | Name + division |
| Objectives | Count of objectives set for this cycle |
| Avg Confidence | Average KR confidence across all KRs: ON_TRACK / AT_RISK / OFF_TRACK |
| Last Check-in | Days since last check-in. Red if > 14 days |
| Overall Progress | Estimated % completion (avg of all KR current/target ratios) |
| Actions | [View OKRs] [Nudge] |

Sorted by Last Check-in descending (most overdue first) by default.

[Nudge]: sends a nudge notification to the employee to perform a check-in. Throttled: max once per 7 days per employee.

### OKR Detail Drawer

```
┌──────────────────────────────────────────────────────────────────┐
│  Rohan Verma — OKRs — FY 2025-26 Annual                [×]      │
│  Last check-in: 8 Mar 2026 (13 days ago)   Overall: ~72%        │
├──────────────────────────────────────────────────────────────────┤
│  Objective 1 (weight: 50%): Improve backend API response time    │
│  Status: ON_TRACK                                                │
│  ─────────────────────────────────────────────────────────────  │
│  KR 1.1: Reduce P95 API latency from 450ms to < 200ms           │
│          Current: 280ms | Target: 200ms | Confidence: AT_RISK ⚠  │
│          [Check In]                                              │
│                                                                  │
│  KR 1.2: Achieve 99.9% uptime for exam day APIs                 │
│          Current: 99.95% | Target: 99.9% | Confidence: ON_TRACK ✓│
│          [Check In]                                              │
│  ─────────────────────────────────────────────────────────────  │
│  Objective 2 (weight: 30%): Launch exam result microservice     │
│  Status: ON_TRACK                                                │
│  ...                                                             │
│  ─────────────────────────────────────────────────────────────  │
│  Objective 3 (weight: 20%): Mentor 2 junior engineers           │
│  Status: OFF_TRACK ⚠                                            │
│  ...                                                             │
└──────────────────────────────────────────────────────────────────┘
```

[Check In] modal (HRBP or employee via self-serve at `/hr/my-performance/`):
```
  KR: Reduce P95 API latency < 200ms
  Current value*:  [280   ] ms   (was 310ms at last check-in)
  Confidence*:     [AT_RISK ▼]
  Notes:           [Working on query optimisation — should hit target by end of March]
  [Save Check-in]
```

Check-in stored in `hr_okr_key_result.current_value` + appended to check-in history (JSONB array).

### Create OKR (for employees via self-serve, HRBP during OKR_SETTING phase)

New objectives created only during OKR_SETTING phase or within first 2 weeks of a new joiner's start (even if mid-cycle). After OKR_SETTING phase closes, objectives are locked — only check-ins allowed.

OKR weights must sum to 100% (validation enforced on save). Minimum 2, maximum 5 objectives per employee per cycle.

---

## Reviews Tab

### Reviews Table

| Column | Description |
|---|---|
| Employee | Name + division + grade |
| Self-Assessment | Submitted / Not Started / In Progress |
| Manager Review | Submitted / Not Started / In Progress |
| Manager | Reporting manager name |
| Calibration Rating | EXCEPTIONAL / EXCEEDS / MEETS / BELOW / UNSATISFACTORY / — |
| Promoted | ✓ / — |
| Increment | % / — |
| Status | NOT_STARTED / SELF_ASSESSMENT / MANAGER_REVIEW / CALIBRATION / COMPLETED |
| Actions | [View Review] [Edit Calibration] (HRBP) [View OKRs] |

### Performance Review Drawer

```
┌──────────────────────────────────────────────────────────────────┐
│  Rohan Verma — Annual Review FY 2025-26              [Close ×]  │
│  Backend Engineer · Division C · Grade L3 · 9 months at grade   │
├──────────────────────────────────────────────────────────────────┤
│  [Self Assessment] [Manager Review] [Calibration] [OKR Summary] │
└──────────────────────────────────────────────────────────────────┘
```

**Self Assessment tab:**

```
  What did you achieve this year? (OKR summary auto-populated):
  "Achieved 99.95% exam day uptime across 12 exam events..."

  Strength demonstrated:
  "Strong ownership of the exam day operations — proactively..."

  Development area:
  "Would benefit from more exposure to system design..."

  Support needed from manager:
  "Access to AWS certification training"

  Self-rating: MEETS_EXPECTATIONS
  Submitted: 20 Mar 2026
```

**Manager Review tab:**

```
  Manager: Arjun Kumar (CTO)
  ─────────────────────────────────────────────────────────
  Performance summary:
  "Rohan delivered consistently this year. The exam day work..."

  Strength demonstrated:
  "Exceptional reliability under pressure. Zero escalations..."

  Development area:
  "Should take more initiative on architecture decisions..."

  Manager rating: EXCEEDS_EXPECTATIONS
  Promotion recommended: Yes (to L4)
  Increment recommended: 15%
  Submitted: 25 Mar 2026
```

**Calibration tab (HRBP + HR Manager only):**

```
  Calibration Rating: [EXCEEDS_EXPECTATIONS ▼]
  Promotion approved: [☑ Yes]   New Designation: [Backend Eng. Sr. ▼]   New Grade: [L4 ▼]
  Increment approved: [15%  ]   Effective: [1 Apr 2026]
  Calibration Note:   "Peer comparison with Division C: consistent top performer."

  [Save Calibration]
```

Calibration changes trigger salary revision task in O-05 (Payroll Exec receives notification to update CTC in next payroll run).

**OKR Summary tab:** read-only pull from OKRs tab — objectives, KR completion, confidence at end of cycle.

---

## Calibration Tab

### 9-Box Calibration Grid

HRBP uses this to run calibration sessions. Plots all employees on a 3×3 grid:

```
  Performance →  BELOW   MEETS   EXCEEDS
  Potential
  HIGH     │  ◉ (2) │  ◉ (8) │  ⭐ (5) │  ← "Stars" — promote + stretch
           │        │        │        │
  MEDIUM   │  ◉ (4) │  ◉(32) │  ◉(18) │  ← Core performers
           │        │        │        │
  LOW      │  ⚠ (2) │  ◉(14) │  ◉ (4) │  ← ⚠ = PIP candidates
```

- Each dot represents an employee. Hover: name, designation, division, grade
- Click dot → opens Review Drawer for that employee
- ⚠ (red): employees in BELOW performance + LOW potential → strong PIP signal, displayed with amber/red marker
- Star (⭐): EXCEEDS + HIGH potential → key talent, retention watch
- Numbers in brackets = count per quadrant
- [Initiate PIP] button appears on hover over ⚠ employees
- [Export 9-Box PNG] → HR Manager only

Potential rating is set by the HRBP based on manager input + HRBP assessment. Stored in `hr_performance_review.potential_rating` (LOW/MEDIUM/HIGH).

### Distribution Summary

Below the grid, a summary bar:

```
  Rating Distribution — FY 2025-26 (112 employees)
  EXCEPTIONAL:      5 (4.5%)   ██
  EXCEEDS:         27 (24.1%)  ████████████
  MEETS:           64 (57.1%)  ████████████████████████████████
  BELOW:            9 (8.0%)   ████
  UNSATISFACTORY:   3 (2.7%)   █
  Not yet calibrated: 4
```

Normal distribution check: amber warning if EXCEPTIONAL > 10% (over-awarding risk) or BELOW + UNSATISFACTORY > 20% (systemic issue signal).

---

## PIPs Tab

### PIP List

| Column | Description |
|---|---|
| Employee | Name + designation |
| Division | Badge |
| Initiated By | HRBP name |
| Start Date | PIP start date |
| End Date | PIP end date (typically 60–90 days) |
| Duration | Days in PIP |
| Status | ACTIVE / CHECKPOINT_DUE / EXTENDED / IMPROVED / SEPARATED / CLOSED |
| Outcome | — or IMPROVED / SEPARATED |
| Actions | [View] [Add Checkpoint] [Close PIP] |

### Initiate PIP Modal (HRBP + HR Manager only — HR Manager must approve before sending)

```
┌──────────────────────────────────────────────────────────────────┐
│  Initiate Performance Improvement Plan                           │
├──────────────────────────────────────────────────────────────────┤
│  Employee*             [Search employee...              ▼]       │
│  Initiated By*         [HR Business Partner (auto)      ]        │
│  Reason for PIP*       [                                ]        │
│  (min 100 chars — must reference specific performance data)      │
│  PIP Start Date*       [2026-04-01                      ]        │
│  PIP Duration*         [90 days (ends: 30 Jun 2026)     ▼]       │
│  Improvement Goals*                                              │
│    Goal 1: [                                            ]        │
│    Goal 2: [                                            ] [+ Add] │
│  Checkpoint Schedule*  [Bi-weekly                       ▼]       │
│  Checkpoint 1 date:    [15 Apr 2026]  (auto-computed)            │
│  Checkpoint 2 date:    [29 Apr 2026]  ...                        │
│                                                                  │
│  ⚠ PIP initiation requires Legal Officer (#75) legal review for  │
│    TERMINATION-risk cases. Flag for legal review: [☐]            │
│                                                                  │
│  [Cancel]              [Save Draft]  [Submit for HR Manager Approval] │
└──────────────────────────────────────────────────────────────────┘
```

**HR Manager approval gate:** HRBP creates PIP draft → HR Manager reviews and approves. Only after approval does the employee's manager get notified to initiate the formal PIP conversation. This two-step prevents premature disclosure.

**Legal flag:** For cases where separation may be the outcome, the Legal Officer (#75) receives a notification to review the PIP documentation for legal compliance (wrongful termination risk).

### PIP Detail Drawer

```
┌──────────────────────────────────────────────────────────────────┐
│  PIP — [Employee Name] (EF-XXXX)                      [Close ×]  │
│  Backend Engineer · Division C · Started: 1 Apr 2026            │
│  Duration: 90 days · Ends: 30 Jun 2026 · Status: ACTIVE         │
├──────────────────────────────────────────────────────────────────┤
│  Reason: "Consistent below-target delivery on API performance    │
│  objectives over Q3-Q4 FY2025-26. P95 latency target of 200ms   │
│  not met despite 2 prior coaching conversations."               │
├──────────────────────────────────────────────────────────────────┤
│  Goals:
│  1. Reduce P95 API latency to < 250ms by 30 Apr 2026
│  2. Complete AWS Advanced certification by 15 May 2026
│  3. Zero production incidents caused by own code in PIP period
│
│  Checkpoints:
│  ✓ 15 Apr 2026   CHECKPOINT_1   Met Goal 1 partially (280ms). Goals 2 in progress.
│  ○ 29 Apr 2026   CHECKPOINT_2   [Add Checkpoint]
│  ○ 13 May 2026   CHECKPOINT_3   Pending
│  ○ 30 Jun 2026   FINAL REVIEW   Pending
│
│  [Add Checkpoint]  [Extend PIP] (HR Manager only)  [Close PIP]
└──────────────────────────────────────────────────────────────────┘
```

[Add Checkpoint]: opens checkpoint modal:
```
  Checkpoint date: [29 Apr 2026]
  Goal 1 status:   [MET / PARTIALLY MET / NOT MET ▼]
  Goal 2 status:   [IN_PROGRESS ▼]
  Goal 3 status:   [MET ▼]
  Summary notes:   [                                     ]
  Recommendation:  [Continue PIP ▼]   (Continue PIP / Extend / Improve / Separate)
```

[Close PIP] → requires outcome selection: IMPROVED / SEPARATED / MUTUAL_SEPARATION. On SEPARATED: HR Manager and Legal Officer notified. Employee status updated to `ON_NOTICE` in O-02.

---

## Probation & Confirmation Reviews

Separate from annual cycle. Managed under the same page but with `cycle_type='PROBATION'` or `cycle_type='CONFIRMATION'`.

Triggered automatically by Task O-8 (14 days before 3-month and 6-month marks):

```
  Upcoming Probation Reviews
  ─────────────────────────────────────────────────────────
  Meera G.    Backend Eng.    3-month review due: 1 Jul 2026   [Create Review]
  Suresh B.   SME Chem.       3-month review due: 7 Jul 2026   [Create Review]
```

[Create Review]: opens simplified review form (no OKR scoring — just: Performance rating 1–5, Behaviour rating 1–5, Recommendation: CONFIRM / EXTEND_PROBATION / SEPARATE).

Outcome stored in `hr_performance_review.probation_outcome`. On CONFIRM: `hr_employee.probation_status='CONFIRMED'`. On EXTEND: new probation milestone created. On SEPARATE: exit initiated in O-04.

---

## Empty States

| Condition | Message |
|---|---|
| No active review cycle | "No active performance review cycle. [+ Create Cycle]" |
| No OKRs set for cycle | "No OKRs configured for this cycle. OKR setting window opens [date]." |
| No PIPs | "No active PIPs." with green checkmark |
| Calibration not started | "Calibration has not started for this cycle. Available from [manager review deadline + 1]." |
| No probation reviews due | "No probation reviews due in the next 30 days." |

---

## Toast Messages

| Action | Toast | Type |
|---|---|---|
| OKR check-in saved | "Check-in recorded for [KR title]." | Green |
| Reminder sent | "Reminder sent to [N] employees for self-assessment." | Blue |
| PIP created | "PIP initiated for [Name]. Awaiting HR Manager approval." | Amber |
| PIP approved | "PIP for [Name] approved. Manager notified." | Green |
| Checkpoint added | "Checkpoint recorded for [Name]'s PIP." | Green |
| Calibration saved | "Calibration rating saved for [Name]." | Green |
| Promotion approved | "[Name] approved for promotion to [Grade]. Payroll notified." | Green |

---

## Authorization

**Route guard:** `@division_o_required(allowed_roles=[79, 106])` applied to `PerformanceView`.

| Scenario | Behaviour |
|---|---|
| [Initiate PIP] | HRBP (#106) creates draft; HR Manager (#79) approves — two-step gate |
| Calibration edit | HRBP (#106) enters initial calibration; HR Manager (#79) finalises and locks |
| [Export ratings CSV] | HR Manager (#79) only |
| [Close PIP with SEPARATED outcome] | HR Manager (#79) only |
| 9-Box export | HR Manager (#79) only |
| Division managers | View-only their team's reviews via separate route `/hr/performance/team/` (requires login, not Division O membership) |
