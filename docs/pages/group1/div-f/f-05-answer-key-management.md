# F-05 — Answer Key & Objections Management

> **Route:** `/ops/exam/answer-key/`
> **Division:** F — Exam Day Operations
> **Primary Role:** Results Coordinator (36) — full control over publication and objection decisions
> **Supporting Roles:** Exam Config Specialist (90) — read (for paper reference); Exam Integrity Officer (91) — read (review integrity-flagged objections); Exam Ops Manager (34) — read + approve
> **File:** `f-05-answer-key-management.md`
> **Priority:** P1 — Post-exam workflow; critical for result accuracy after objection review

---

## 1. Page Name & Route

**Page Name:** Answer Key & Objections Management
**Route:** `/ops/exam/answer-key/`
**Part-load routes:**
- `/ops/exam/answer-key/?part=kpi` — KPI strip
- `/ops/exam/answer-key/?part=pending-keys` — pending publication tab
- `/ops/exam/answer-key/?part=published-keys` — published answer keys
- `/ops/exam/answer-key/?part=objections` — objections queue tab
- `/ops/exam/answer-key/?part=closed-objections` — closed objections
- `/ops/exam/answer-key/?part=key-drawer&id={id}` — answer key detail drawer
- `/ops/exam/answer-key/?part=objection-drawer&id={id}` — objection review drawer

---

## 2. Purpose

After an exam ends, the Results Coordinator publishes the answer key so institutions and students can verify which answers were marked correct. Institutions (and sometimes students via institution admins) can then file objections against specific questions — claiming the marked answer is wrong, multiple answers are valid, or a question has an error.

F-05 manages:
1. Answer key entry and publication (PROVISIONAL first, then FINAL)
2. Objection window management (default 72 hours from `exam_operational_config`)
3. Per-objection review workflow (Accept/Reject with reasoning)
4. When a CRITICAL objection is ACCEPTED: the system re-scores the affected exam → F-04 gets a recompute trigger

**Why PROVISIONAL → FINAL matters:**
Publishing PROVISIONAL first signals "students can check, but we're still reviewing objections." Publishing FINAL means scoring is locked and results are now authoritative. If an objection is accepted after FINAL, a revised answer key is published (REVISED status) and results are recomputed.

---

## 3. Tabs

| Tab | Label |
|---|---|
| 1 | Pending Answer Keys |
| 2 | Published Answer Keys |
| 3 | Open Objections |
| 4 | Closed Objections |

---

## 4. Section-Wise Detailed Breakdown

---

### KPI Strip

| # | KPI | Alert |
|---|---|---|
| 1 | Awaiting Answer Key | Exams completed but no answer key published; amber if > 0 |
| 2 | Objection Window Open | Active publications still accepting objections |
| 3 | Open Objections | Count unresolved; amber if > 0 |
| 4 | Accepted Objections (this month) | Count for awareness |
| 5 | Objection Window Closing Soon | Publications with window closing in < 6h; amber |
| 6 | Pending Rescoring | Count where accepted objection triggered rescoring but not yet done |

---

### Tab 1 — Pending Answer Keys

Exams completed (or ACTIVE with answer key ready for pre-staging) that do not have an PROVISIONAL or FINAL answer key published.

#### Pending Table

| Column | Sortable | Notes |
|---|---|---|
| Exam | Yes | Exam name |
| Institution | Yes | — |
| Exam Type | No | — |
| Paper Code | No | `exam_question_paper.paper_code` |
| Completed At | Yes (default: ASC) | — |
| Questions | No | Total question count from paper |
| Key Status | No | `DRAFT` · `PENDING_REVIEW` · No key yet |
| Actions | — | [Create/Edit Key] · [Publish Provisional] |

**[Create/Edit Key]:** opens Answer Key Editor Drawer (760px).

**[Publish Provisional]:** only shown when key status = `PENDING_REVIEW` and all questions have answers entered. Opens Publish Confirmation Modal.

---

### Answer Key Editor Drawer (760px)

**Header:** Exam name + Paper code + Status pill + [×]

#### Section A — Answer Key Grid

One row per question in the paper.

| Column | Notes |
|---|---|
| Q# | Question number |
| Correct Option | Select: A · B · C · D · E (or custom options) — editable |
| Marks Awarded | Number (default from paper config; editable per question) |
| Marks for Wrong | Number (negative marking — default from exam schedule config) |
| Marks if No Attempt | Number (default 0) |
| Status | `DRAFT` · `CONFIRMED` |
| Objection Count | Count of objections for this question (shown when published) |
| Actions | [Mark Confirmed] · [Flag for Review] |

**Bulk actions:** Select all → [Set All Marks to {X}] · [Set All Negative to {Y}]

**Import Answer Key (CSV):** [Import CSV] button. Format: `question_number,correct_option,marks_awarded,marks_for_wrong`. Validates on upload; preview before import.

**[Save Draft]** → saves without publishing. ✅ "Answer key saved as draft" toast 4s.

#### Section B — Key Summary

- Total questions: {N}
- Answered (confirmed): {N} of {N}
- Unanswered: {N} — highlighted red if any exist before publish

#### Section C — Publish Controls

**Pre-publish validation:**
- All questions must have correct_option set
- All marks_awarded must be ≥ 0
- Total marks must equal `exam_question_paper.total_marks`

**[Publish Provisional Answer Key]:** enables when all validation passes. Opens confirmation modal.

**Provisional banner message** (shown to institutions after publish): "This is a provisional answer key. Objections can be filed until {objection_window_close_at}. Final answer key will be published after objection review."

**[Mark as Final]:** available when `status = PROVISIONAL` and objection window closed. Opens confirmation modal. After marking FINAL, no new objections accepted.

**[Publish Revised Key]:** available when `status = FINAL` and a new draft was prepared (due to accepted objection). Reopens objection window for {N} hours (configurable). Triggers rescoring task.

---

### Tab 2 — Published Answer Keys

All published answer keys (PROVISIONAL, FINAL, REVISED).

#### Published Keys Table

| Column | Sortable | Notes |
|---|---|---|
| Exam | Yes | — |
| Institution | Yes | — |
| Status | No | PROVISIONAL · FINAL · REVISED |
| Published At | Yes (default: DESC) | — |
| Objection Window | No | Open / Closed + datetime |
| Total Objections | No | Count |
| Accepted | No | Count |
| Rejected | No | Count |
| Actions | — | [View Key] · [View Objections] · [Extend Window] · [Mark Final] |

**[Extend Window]:** extends `objection_window_close_at` by N hours (input). Requires reason. Logs action.

---

### Tab 3 — Open Objections

All unresolved objections across all published answer keys.

#### Filter Bar

| Filter | Control |
|---|---|
| Exam | Searchable select |
| Institution | Searchable select |
| Objection Type | Multi-select |
| Priority | Auto-sorted by: WRONG_ANSWER (highest) → MULTIPLE_CORRECT → QUESTION_ERROR → OTHER |
| Date Filed | Date range |

#### Objections Table

| Column | Sortable | Notes |
|---|---|---|
| ID | No | Auto-ref |
| Exam | Yes | — |
| Institution | Yes | — |
| Q# | No | Question number |
| Objection Type | No | — |
| Description (excerpt) | No | First 80 chars |
| Supporting Doc | No | 📎 if attached |
| Filed At | Yes | — |
| Window Closes | Yes | Countdown if < 12h |
| Status | No | OPEN · UNDER_REVIEW |
| Actions | — | [Review] · [Quick Accept] · [Quick Reject] |

**[Quick Accept] / [Quick Reject]:** one-click with mandatory reason input inline. No drawer needed for simple cases.

**[Review]:** opens Objection Review Drawer (640px).

---

### Objection Review Drawer (640px)

**Header:** Exam + Q# + Objection Type + Status pill + [×]

#### Section A — Objection Details

| Field | Notes |
|---|---|
| Institution | — |
| Question Number | With link to question in paper (read-only view) |
| Objection Type | — |
| Description | Full text |
| Supporting Document | Download link (presigned S3 URL, 15 min expiry) — if attached |
| Filed At | — |

#### Section B — Current Answer Key Entry

| Field | Value |
|---|---|
| Correct Option (current) | A / B / C / D |
| Marks Awarded | {X} |
| Marks for Wrong | {Y} |
| Published Status | PROVISIONAL / FINAL |

#### Section C — Review Decision

| Field | Required | Notes |
|---|---|---|
| Decision | Yes | Radio: ACCEPT · REJECT |
| Corrected Option (if ACCEPT) | Conditional | Required if ACCEPT + objection type = WRONG_ANSWER / MULTIPLE_CORRECT |
| Review Notes | Yes | Min 20 chars — rationale required |

**When ACCEPT selected:**
- If `objection_type = WRONG_ANSWER`: shows "New correct answer" field (select corrected option)
- If `objection_type = MULTIPLE_CORRECT`: shows "Award marks to:" radio — "Both A and B correct" or "Question cancelled (full marks to all)"
- If `objection_type = QUESTION_ERROR`: shows "Mark as cancelled?" toggle — cancelled questions award full marks to all students

**[Submit Decision]** → sets `exam_answer_key_objection.status = ACCEPTED / REJECTED`. Triggers rescoring workflow if ACCEPTED. ✅ "Objection {accepted/rejected}" toast 4s.

**Rescoring workflow on ACCEPT:**
1. Updates `exam_answer_key` for the affected question
2. Queues `compute_exam_results` recompute task (Celery) — recomputes scores for all students
3. Notification sent to Results Coordinator (36) in F-04 that rescoring is ready for review
4. Result publication status → DRAFT (forces re-review before republishing)

---

### Tab 4 — Closed Objections

Read-only archive of all resolved objections with decision and reasoning.

**Filters:** Date resolved · Decision (Accepted/Rejected) · Exam · Objection Type

**Export:** [Download Objections Report CSV] — useful for SME team (Div D) to review question quality.

---

## 5. Modals

### Publish Answer Key Confirmation Modal (480px)

"Publish provisional answer key for **{Exam Name}** at **{Institution}**?

- {N} questions with answers
- Objection window: {N} hours (closes at {datetime})
- Institutions will be notified and can see the answer key immediately"

[Confirm Publish] `bg-[#6366F1]` · [Cancel]

**On confirm:** creates `exam_answer_key_publication` with status = PROVISIONAL. Sends in-app notification to institution admins. Celery task `close_answer_key_objection_window` scheduled for `objection_window_close_at`.

### Mark Final Confirmation Modal (400px)

"Mark answer key as FINAL for **{Exam Name}**?

- Objection window: **Closed** ({N} objections filed, {N} accepted, {N} rejected)
- After marking FINAL, no new objections will be accepted
- Results using this answer key are now authoritative"

[Confirm Mark Final] `bg-[#6366F1]` · [Cancel]

---

## 6. Data Model Reference

Full models in `div-f-pages-list.md`:
- `exam_answer_key_publication` — publication state
- `exam_answer_key_objection` — objection lifecycle

**`exam_answer_key_entry`** (per question):
| Field | Type | Notes |
|---|---|---|
| `id` | UUID | — |
| `publication_id` | FK → `exam_answer_key_publication` | — |
| `question_number` | int | — |
| `correct_option` | varchar(10) | `A` · `B` · `C` · `D` · `CANCELLED` |
| `marks_awarded` | decimal | — |
| `marks_for_wrong` | decimal | Default: from exam_schedule.negative_marking_factor × marks_awarded |
| `marks_if_no_attempt` | decimal | Default 0 |
| `is_cancelled` | boolean | Default False — when question cancelled, all students get marks_awarded |
| `status` | varchar | Enum: `DRAFT` · `CONFIRMED` |
| `objection_accepted` | boolean | Default False — set when an objection modifies this entry |
| `revision_note` | text | Nullable — if revised due to accepted objection |

---

## 7. Access Control

| Gate | Rule |
|---|---|
| Page access | Results Coordinator (36), Config Specialist (90), Integrity Officer (91), Ops Manager (34), Platform Admin (10) |
| Create / edit answer key | Results Coordinator (36), Platform Admin (10) |
| Publish (provisional or final) | Results Coordinator (36), Platform Admin (10) |
| Review objections | Results Coordinator (36) |
| Accept/Reject objections | Results Coordinator (36), Platform Admin (10) |
| Extend objection window | Results Coordinator (36), Ops Manager (34) |
| Read-only | Config Specialist (90), Integrity Officer (91), Ops Manager (34) |

---

## 8. Edge Cases & Error States

| Scenario | Behaviour |
|---|---|
| Objection filed after window closed | Institution portal blocks submission. F-05 confirms: "Objection window is closed — this objection was not filed." |
| Max objections per institution reached | New objection submission blocked in institution portal. F-05 shows: "Institution X has reached the objection limit ({N}). No further objections accepted." |
| Accepted objection triggers rescore but computation fails | ❌ "Rescoring failed: {error}. Results remain at previous published state. Retry from F-04." Notification sent to Results Coordinator. |
| Two coordinators review same objection | Optimistic concurrency: first to submit wins. Second sees: "This objection was already resolved by another session." |
| Answer key published for exam with integrity hold | Publication is allowed (students need to see the key). Result publication (F-04) remains blocked by integrity hold separately. |
| Revised key published after FINAL marked | `exam_answer_key_publication.status → REVISED`. Previous FINAL key retained in history. Objection window reopened. Results Coordinator notified that rescoring is needed. |

---

## 9. UI Patterns

### Toasts

| Action | Toast |
|---|---|
| Key saved as draft | ✅ "Answer key saved as draft" (4s) |
| Provisional key published | ✅ "Provisional answer key published — objection window open until {time}" (4s) |
| Final key marked | ✅ "Answer key marked as FINAL" (4s) |
| Objection accepted | ✅ "Objection accepted — rescoring triggered" (4s) |
| Objection rejected | ✅ "Objection rejected" (4s) |
| Window extended | ✅ "Objection window extended to {time}" (4s) |

### Responsive

| Breakpoint | Behaviour |
|---|---|
| Desktop (≥1280px) | Full table; drawer 760px; answer key grid scrollable |
| Tablet | Reduced table columns; drawer full-width |
| Mobile | Card layout; answer key grid → scrollable table with sticky Q# column |

---

*Page spec complete.*
*F-05 covers: answer key creation (grid edit + CSV import) → provisional publish → objection window management → per-objection review → accept/reject → rescoring trigger → final publication.*
