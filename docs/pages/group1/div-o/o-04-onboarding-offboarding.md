# O-04 — Onboarding & Offboarding

**Route:** `GET /hr/onboarding/`
**Method:** Django `TemplateView` + HTMX part-loads
**Primary roles:** HR Manager (#79), Office Administrator (#81)
**Also involved (not direct page access):** Recruiter (#80) — triggers onboarding on offer acceptance; DevOps/SRE Engineer (#14) — receives IT access task notifications; BGV Manager (#39) — receives employee BGV initiation; Payroll & Compliance Executive (#105) — receives payroll setup task; L&D Coordinator (#107) — receives induction scheduling task

---

## Purpose

Every EduForge employee hire and exit involves coordinated actions across HR, IT (DevOps), Finance (payroll setup), Security (access provisioning/revocation), BGV (Division G for background verification), and L&D (induction). Without a structured checklist system, critical steps get missed: a new joiner starts without a laptop (Office Admin missed the asset prep), or an exiting employee retains GitHub access for weeks (DevOps not notified). This page coordinates the full joining and exit workflow through task-based checklists with assignees, deadlines, and completion tracking.

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| Tab counts | `hr_onboarding_checklist` + `hr_offboarding_checklist` aggregated by status | 5 min |
| Onboarding records | `hr_employee` WHERE join_date >= today-30d OR status='ACTIVE' and onboarding_complete=false | 5 min |
| Offboarding records | `hr_employee` WHERE status='ON_NOTICE' ORDER BY last_working_date ASC | 2 min |
| Checklist items | `hr_onboarding_checklist` or `hr_offboarding_checklist` for selected employee | No cache |
| Task detail | Single checklist task row + completion log | No cache |

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?tab` | `onboarding`, `offboarding` | `onboarding` | Active tab |
| `?employee_id` | UUID | — | Pre-open checklist for specific employee |
| `?status` | `in_progress`, `completed`, `overdue`, `all` | `in_progress` | Filter checklist status |
| `?assigned_to` | `hr`, `it`, `payroll`, `bgv`, `ld`, `admin` | `all` | Filter tasks by assignee team |

---

## HTMX Part-Load Routes

| Part | Route | Trigger | Target ID |
|---|---|---|---|
| Onboarding list | `?part=onboarding_list` | Page load + tab click + filter | `#o4-onboarding-list` |
| Offboarding list | `?part=offboarding_list` | Tab click + filter | `#o4-offboarding-list` |
| Checklist drawer | `?part=checklist&employee_id={id}&type={onboarding|offboarding}` | Row click / [Open Checklist] | `#o4-checklist-drawer` |
| Task complete toggle | `POST /hr/onboarding/tasks/{task_id}/complete/` | [Mark Done] click | Inline swap |
| Initiate exit modal | `?part=exit_modal&employee_id={id}` | [Initiate Exit] button | `#modal-container` |

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Onboarding & Offboarding                                            │
├──────────────────────────────────────────────────────────────────────┤
│  [Onboarding (4 active)] [Offboarding (7 on notice)]                │
├──────────────────────────────────────────────────────────────────────┤
│  SUMMARY STRIP (joining this month / tasks overdue / exits this month)│
├──────────────────────────────────────────────────────────────────────┤
│  Filter: Status [In Progress ▼]  Assigned to [All ▼]                │
│                                                                      │
│  EMPLOYEE LIST (left panel)  │  CHECKLIST (right panel)              │
│  ─────────────────────────── │  ──────────────────────────────────── │
│  [Employee card list]        │  [Task checklist for selected emp]    │
└──────────────────────────────┴───────────────────────────────────────┘
```

---

## Onboarding Tab

### Onboarding Summary Strip

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 4            │ │ 2            │ │ 3            │ │ 1            │
│ Joining      │ │ Joining      │ │ Overdue      │ │ Fully        │
│ This Month   │ │ This Week    │ │ Tasks        │ │ Completed    │
│              │ │              │ │ ⚠ action req │ │ this month   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### Onboarding Employee List (left panel)

```
  Meera G.        Backend Eng.     Join: 1 Apr 2026   9/18 tasks ✓   [Open Checklist]
  Suresh B.       SME Chemistry    Join: 7 Apr 2026   0/18 tasks ✓   ⚠ not started  [Open Checklist]
  Kavya R.        L2 Support Eng.  Join: 15 Apr 2026  0/18 tasks ✓   —              [Open Checklist]
  Rohit M.        Data Engineer    Joined: 14 Mar     18/18 tasks ✓  Completed ✓    [View]
```

Red row: join date within 3 days and < 50% tasks complete.
Amber row: join date within 7 days.

### Onboarding Checklist (right panel)

Structured checklist per new joiner. Tasks are generated from a master template at the time of offer acceptance, with `due_by_day` relative to `join_date`.

**Standard Onboarding Checklist (18 tasks):**

```
  ✓  Day -7:  HR            Send pre-joining welcome email with forms pack
  ✓  Day -7:  HR            Collect PAN card, Aadhaar, bank details
  ✓  Day -5:  Office Admin  Assign laptop (from hr_asset pool)
  ✓  Day -5:  Office Admin  Assign access card, desk allocation
  ○  Day -3:  DevOps (#14)  Create GitHub organisation access (team: <division>)
  ○  Day -3:  DevOps (#14)  Create AWS IAM role (if applicable by role)
  ○  Day -3:  HR            Create EduForge internal systems account (Jira/Confluence/Slack)
  ○  Day -1:  Payroll Exec  Add to payroll — PF registration (new UAN or link existing), CTC setup
  ○  Day 0:   HR            Issue appointment letter (signed copy)
  ○  Day 0:   HR            POSH policy briefing (signed acknowledgement)
  ○  Day 0:   HR            Data privacy policy briefing (signed acknowledgement)
  ○  Day 0:   Office Admin  Office tour, introductions, desk setup verification
  ○  Day 0:   L&D (#107)    Schedule induction sessions (product overview, culture, tools)
  ○  Day 1:   HR            Enrol in mandatory L&D: POSH Awareness, Data Privacy
  ○  Day 1:   BGV (via G)   Initiate background verification (via vendor/Division G workflow)
  ○  Day 7:   HR            1-week check-in call with HR Manager + HRBP
  ○  Day 30:  HRBP (#106)   30-day check-in + probation OKR setting
  ○  Day 90:  HRBP (#106)   90-day review (probation milestone 1)
```

**Task card (expanded):**

```
  ○  Day -3: DevOps — Create GitHub organisation access
  ─────────────────────────────────────────────────────
  Assigned to:    DevOps/SRE Engineer (#14)
  Due:            29 Mar 2026 (3 days before join: 1 Apr)
  Status:         PENDING
  Instructions:   "Add to github.com/eduforge-platform organisation.
                   Assign to team matching their division (e.g.,
                   team/engineering for Division C). Send invite link
                   to their work email."
  Notification:   Email sent to DevOps on 22 Mar 2026, 09:00 IST

  [Mark Done]   [Add Note]   [Reassign]   [Extend Deadline]
```

[Mark Done]: inline HTMX — task card ticks, progress counter updates. Completion recorded in `hr_onboarding_checklist` with `completed_at`, `completed_by`.

[Add Note]: free text note appended to task (useful for partial completions: "GitHub invite sent, awaiting acceptance from joiner").

[Reassign]: HR Manager only. Changes `assigned_to_role` and resends notification.

[Extend Deadline]: HR Manager only. Records new due date with reason. Overdue tasks shown with red left border.

**BGV Task special behaviour:** Clicking "Initiate BGV" on the BGV task opens a lightweight form:
- Employee name (pre-filled)
- Document checklist (Aadhaar, PAN, address proof on file: Yes/No)
- [Initiate BGV] → sends notification to BGV Manager (#39) / BGV Operations Supervisor (#92) with employee record link
- On BGV completion, BGV Manager updates the task status directly from Division G's system; O-04 polls `hr_onboarding_checklist` status

**External task completion flow:** DevOps, BGV Manager, and Payroll Exec do not have `/hr/onboarding/` access. They receive email notifications with a one-time task acknowledgement link (`/hr/tasks/{task_token}/complete/`) — clicking the link marks the task done and records `completed_by` with the external role. This avoids requiring non-Division-O roles to navigate the HR portal.

---

## Offboarding Tab

### Offboarding Summary Strip

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 7            │ │ 3            │ │ 2            │ │ 1            │
│ On Notice    │ │ Exiting      │ │ F&F Not      │ │ Overdue      │
│              │ │ This Month   │ │ Triggered    │ │ Tasks        │
│              │ │              │ │ ⚠ action req │ │ ⚠            │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### Initiate Exit Modal

HR Manager only. Triggered via O-02 Employee Directory [Initiate Exit] or from this page.

```
┌──────────────────────────────────────────────────────────────────┐
│  Initiate Exit — Ravi Kumar (EF-0031, DevOps Engineer)           │
├──────────────────────────────────────────────────────────────────┤
│  Exit Type*          [Resignation                   ▼]           │
│  Resignation Date*   [21 Mar 2026                   ]            │
│  Notice Period       60 days (per contract)                      │
│  Last Working Date*  [19 May 2026                   ] (computed) │
│  Override LWD?       [☐] Reason: [                  ]            │
│  Exit Interview?     [☑] Schedule: [28 Mar 2026     ]            │
│                                                                  │
│  [Cancel]                               [Initiate Exit Process]  │
└──────────────────────────────────────────────────────────────────┘
```

Exit types: RESIGNATION / TERMINATION / END_OF_CONTRACT / MUTUAL_SEPARATION / RETIREMENT / ABANDONMENT

On submit: updates `hr_employee.status='ON_NOTICE'`, sets `last_working_date`, generates offboarding checklist from template, sends notifications to all task assignees.

### Offboarding Checklist (17 standard tasks)

```
  ○  Day 0 from notice:   HR            Exit interview scheduled (if applicable)
  ○  Day 0:               HR            Acknowledge resignation formally (email + letter)
  ○  Day 0:               HRBP (#106)   PIP closure (if any active PIP — formal close-out)
  ○  Day -14 before LWD:  HR            Knowledge transfer plan initiated (role-specific)
  ○  Day -7:              HR            F&F (Full & Final) settlement computation initiated
  ○  Day -5:              DevOps (#14)  Revoke GitHub access (note: retain read-only for 14d for KT)
  ○  Day -5:              DevOps (#14)  Revoke AWS IAM role
  ○  Day -5:              DevOps (#14)  Deactivate SSO / internal Slack account (defer to LWD)
  ○  Day -3:              Payroll Exec  Stop recurring payroll; compute final payslip (proration)
  ○  Day -3:              Payroll Exec  PF withdrawal/transfer form (Form 19 + 10C or Form 13 for transfer)
  ○  Day -1:              Office Admin  Collect laptop + accessories (log in hr_asset as RETURNED)
  ○  Day -1:              Office Admin  Collect access card + deactivate building access
  ○  Day LWD:             HR            Issue experience letter (signed PDF)
  ○  Day LWD:             HR            Issue relieving letter
  ○  Day LWD + 7:         Payroll Exec  F&F settlement disbursed (payable within 30 days of LWD per Payment of Wages Act)
  ○  Day LWD + 7:         HR            Final Form 16 (prorated year)
  ○  Day LWD + 30:        HR            Archive employee record (status → EXITED)
```

**F&F Computation task** (Payroll Exec owned): Clicking opens F&F calculation drawer:
```
  Basic (proration):     ₹42,000   (21/31 days of March)
  HRA:                   ₹21,000
  Earned Leave Encashment: ₹12,400 (18 EL × ₹689/day)
  Gratuity:              ₹29,200   (if >5 years) / — (< 5 years, not applicable)
  Recovery — Notice shortfall: — (if serving full notice)
  TDS (advance):         ₹8,200
  ───────────────────────────────
  Net F&F Payable:       ₹88,000
  [Lock F&F Computation]  [Export for Approval]
```

F&F must be approved by HR Manager before disbursement. After HR Manager approval, Payroll Exec executes payment and marks the F&F task complete.

---

## Knowledge Transfer Protocol

For technical roles (Division C, D, E, F, H) with notice > 14 days, a knowledge transfer checklist is generated:

```
  [Role-specific KT checklist — auto-populated based on division]

  Division C — Engineering:
  ○ Document all active microservices / Lambda functions owned
  ○ Update Confluence runbooks for owned services
  ○ Hand over API keys / rotation schedule to DevOps
  ○ Code review pending PRs + merge before LWD
  ○ Introduce replacement/buddy to external vendors

  Division D — Content:
  ○ Hand over all unpublished question drafts to Question Approver
  ○ Document current curriculum mapping for owned subjects
  ○ Complete in-progress reviews
```

KT tasks assigned to the exiting employee (self-marked) + verified by their manager (separate confirmation step).

---

## Empty States

| Condition | Message |
|---|---|
| No active onboardings | "No active joiners right now." with [+ Create Onboarding] button |
| No employees on notice | "No employees currently on notice. All clear." with green checkmark |
| All tasks complete | "All onboarding tasks completed for [name]." with green shield icon |
| F&F not yet triggered | "F&F settlement not yet initiated. Due within 30 days of last working date." with amber warning |

---

## Toast Messages

| Action | Toast | Type |
|---|---|---|
| Task marked done | "[Task name] completed by [user]." | Green |
| Exit initiated | "Offboarding process initiated for [Name]. Last working date: [date]." | Amber |
| BGV initiated | "BGV request sent to BGV team for [Name]." | Blue |
| F&F computation locked | "F&F computation locked for [Name]. Awaiting HR Manager approval." | Blue |
| F&F approved | "F&F settlement approved for [Name]. Disbursement queued." | Green |
| Experience letter issued | "Experience letter issued for [Name]." | Green |
| Overdue task alert | "[N] onboarding tasks are overdue. [View →]" | Red |

---

## Authorization

**Route guard:** `@division_o_required(allowed_roles=[79, 81, 106])` applied to `OnboardingView`. Payroll Exec (#105) and DevOps (#14) access tasks via tokenised one-time acknowledgement links only.

| Scenario | Behaviour |
|---|---|
| DevOps clicking task link | Resolves via `/hr/tasks/{token}/complete/` — marks task, shows thank-you page, no portal access |
| [Initiate Exit] | HR Manager (#79) only |
| [Mark Done] for IT tasks | HR Manager (#79) or task owner via token link |
| F&F lock and approval | Lock: Payroll Exec (#105) via token; Approve: HR Manager (#79) |
| BGV initiation | HR Manager (#79) only |
