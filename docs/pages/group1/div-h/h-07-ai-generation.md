# H-07 — AI MCQ Generation Manager

> **Route:** `/analytics/ai-generation/`
> **Division:** H — Data & Analytics
> **Primary Role:** AI Generation Manager (45) — full pipeline ownership
> **Supporting Roles:** Data Engineer (43) — read + pipeline troubleshooting; Platform Admin (10) — full
> **File:** `h-07-ai-generation.md`
> **Priority:** P1 — AI pipeline feeds the 2M+ question bank; quality gate before Division D

---

## 1. Page Name & Route

**Page Name:** AI MCQ Generation Manager
**Route:** `/analytics/ai-generation/`
**Part-load routes:**
- `/analytics/ai-generation/?part=pipeline-kpi` — KPI bar
- `/analytics/ai-generation/?part=batch-list` — batch management table
- `/analytics/ai-generation/?part=review-queue` — MCQ review queue
- `/analytics/ai-generation/?part=quality-metrics` — quality dashboard
- `/analytics/ai-generation/?part=cost-tracker` — cost tracking panel
- `/analytics/ai-generation/{batch_id}/?part=batch-detail` — batch detail drawer
- `/analytics/ai-generation/{mcq_id}/?part=mcq-review` — individual MCQ review panel

---

## 2. Purpose

H-07 is the **AI MCQ Generation Manager's primary workspace**. It manages the entire AI pipeline from batch creation through quality review and handoff to Division D.

**The two-level quality gate:**
1. **AI Generation Manager (45)** — reviews AI output for: hallucinations, wrong correct answers, factually incorrect explanations, poor distractors, topic drift. This is H-07's scope.
2. **Division D SME (roles 19–27) + Approver (29)** — reviews for: pedagogical quality, curriculum alignment, language polish, final publish decision. This is Division D's scope.

The AI Gen Manager is a subject-matter-aware filter who removes obviously bad MCQs so Division D SMEs don't waste time on rejects. They are NOT the final quality authority — that is always Division D.

**Who needs this page:**
- AI Generation Manager (45) — daily: creates batches, reviews output, tracks quality trends
- Data Engineer (43) — pipeline troubleshooting if AI API calls fail

---

## 3. Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  Page header: "AI MCQ Generation Manager"  [+ Create Batch]       │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────────────────┤
│Total │Genrtd│Pendng│Apprvd│Rejtd │Div D │MTD   │ MTD Acceptance  │
│Batches│(MTD)│Review│(MTD) │(MTD) │Queue │Cost  │ Rate            │
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────────────────┤
│  Batch Management Table (server-side paginated, 25 rows)          │
├───────────────────────────────────────────────────────────────────┤
│  MCQ Review Queue  (REVIEW_PENDING items — across all batches)    │
├─────────────────────────────────┬─────────────────────────────────┤
│  Quality Metrics Dashboard      │  Cost Tracker                   │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

## 4. Section-Wise Detailed Breakdown

---

### Section A — KPI Bar

Eight tiles. Source: `analytics_ai_batch` + `analytics_ai_generated_mcq`.

| Tile | Description | Colour Rule |
|---|---|---|
| Total Batches | All time batch count | Neutral |
| Generated (MTD) | MCQs generated this month | Neutral |
| Pending Review | `analytics_ai_generated_mcq` where `review_status = PENDING` across all batches | Amber if > 100; Red if > 500 (backlog) |
| Approved (MTD) | MCQs AI Gen Manager approved this month | Neutral |
| Rejected (MTD) | MCQs rejected this month | Amber if rejection rate > 30% |
| Division D Queue | MCQs approved by AI Gen Manager and currently in Division D review queue | Neutral |
| MTD Cost (₹) | Sum of `analytics_ai_batch.api_cost_inr` for current month | Amber if > monthly budget (configurable in model config) |
| MTD Acceptance Rate | `approved_count ÷ generated_count` for current month | Green ≥ 70%; Amber 50–70%; Red < 50% (AI quality is poor) |

---

### Section B — Batch Management Table

Server-side paginated, 25 rows per page. Source: `analytics_ai_batch`.

| Column | Sortable | Notes |
|---|---|---|
| Batch Ref | No | `AIB-YYYYMM-{seq}` |
| Domain | Yes | Badge |
| Subject | Yes | — |
| Topic | Yes | — |
| Difficulty | No | EASY / MEDIUM / HARD / MIXED badge |
| Requested | No | Count |
| Generated | No | Actual generated count |
| Status | Yes | QUEUED · GENERATING · REVIEW_PENDING · REVIEW_IN_PROGRESS · APPROVED · PARTIALLY_APPROVED · REJECTED · CANCELLED badge |
| Accepted | No | Approved ÷ generated — e.g., "42/50 (84%)" |
| Cost (₹) | Yes | `api_cost_inr` |
| Created | Yes (default: DESC) | Datetime |
| Actions | — | [Review] (if REVIEW_PENDING) · [View →] opens detail drawer |

**[Review]** on REVIEW_PENDING batch: opens the MCQ Review Panel in the MCQ Review Queue section (auto-scrolls to it and pre-filters to this batch).

**Bulk actions (rows selected):**
- [Cancel Selected] — only rows with status QUEUED can be cancelled. Confirmation: "Cancel {N} queued batches? Generated MCQs are discarded."
- [Export Batch Summary CSV] — batch-level stats for selected rows

**Row click** → opens Batch Detail Drawer.

---

### Section C — MCQ Review Queue

The single most important section for the AI Generation Manager's daily work. Shows all individual MCQs with `review_status = PENDING`, across all batches, sorted by batch creation date (oldest first — process FIFO to avoid stale batches).

**Queue stats strip:** "Showing {N} pending MCQs from {M} batches. Oldest pending: {batch_ref} — {X} days."

**Quick review mode — card view:**

Each card shows one MCQ for rapid review:

```
┌─────────────────────────────────────────────────────────────────┐
│  Batch: AIB-202409-0042 · Domain: SSC · Subject: Mathematics    │
│  Topic: Data Interpretation  · Confidence: 0.87  [2 of 50]     │
├─────────────────────────────────────────────────────────────────┤
│  Q: The ratio of income to expenditure of person A is 5:3 and  │
│  person B is 4:3. If their combined income is ₹18,000, what is │
│  person A's expenditure?                                        │
│                                                                 │
│  A. ₹4,500    B. ₹5,400    C. ₹6,000   ● D. ₹7,500             │
│                                                                 │
│  Explanation: Person A's income : expenditure = 5:3 = 5x : 3x  │
│  Person B = 4y : 3y. Total income = 5x + 4y = 18,000 ...       │
├─────────────────────────────────────────────────────────────────┤
│  [✅ Approve] [✏ Request Revision] [❌ Reject]  [Skip →]         │
│  Review note (required if Request Revision or Reject):          │
│  ┌──────────────────────────────────────────┐                   │
│  │ Wrong correct answer — option C is right │                   │
│  └──────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

**Three review actions:**

| Action | Behaviour | Note Required? |
|---|---|---|
| ✅ Approve | Sets `review_status = APPROVED`. MCQ enters Division D queue. | Optional (can add notes for SMEs) |
| ✏ Request Revision | Sets `review_status = FLAGGED_FOR_REVISION`. Does NOT send to Division D. Remains in queue for AI Manager to edit and re-review. | Required — min 10 chars |
| ❌ Reject | Sets `review_status = REJECTED`. MCQ discarded. | Required — min 10 chars |
| Skip → | Moves to next card, comes back to this one later. | — |

**[Skip →]** button: temporarily defers an MCQ (it drops to the bottom of the queue for this session). Useful when the AI Gen Manager is unsure and wants to consult an SME before deciding.

**Keyboard shortcuts** (desktop):
- `A` → Approve
- `R` → Reject (opens note field)
- `V` → Request Revision (opens note field)
- `Space` or `→` → Skip

**Batch review mode toggle:** [Review by Batch] / [Review All] — "Review by Batch" shows a batch selector at top, then only shows MCQs from that batch. Useful for large batches where the AI Gen Manager wants to review one batch completely before moving to the next.

**[Review All] button** at batch level (in Batch Management Table when status = REVIEW_PENDING): Approve or Reject all MCQs in a batch with a single action. Use case: batch for a simple topic where all generated MCQs are clearly correct or clearly wrong.
- [Approve All in Batch] — confirmation: "Approve all {N} MCQs in batch {ref}? They will all enter Division D review queue."
- [Reject All in Batch] — requires reason (batch-level reject note applied to all).

**Progress indicator:** "Reviewed {N} of {total} in current session." Visual progress bar.

**Filter for queue:**
- Domain / Subject / Topic / Batch Ref
- Confidence score range (review high-confidence first: `ai_confidence_score > 0.8`)
- [Show Flagged for Revision] — shows MCQs previously flagged that need re-review

---

### Section D — Quality Metrics Dashboard

**Purpose:** Longitudinal tracking of AI generation quality. Shows whether AI quality is improving or degrading over time. Used by AI Gen Manager to decide when to adjust model prompts.

**Charts:**
1. **Acceptance rate by month** (bar chart): `approved ÷ generated` per month. Target ≥ 70%. A declining trend signals prompt degradation or model version change.

2. **Rejection reason breakdown** (pie chart, MTD): Distribution of rejection notes (auto-categorised by keyword matching):
   - Wrong correct answer
   - Factually incorrect
   - Poor distractors
   - Topic drift
   - Ambiguous question
   - Duplicate of existing
   - Other

3. **Confidence score vs. acceptance rate** (scatter plot): X = `ai_confidence_score`, Y = accepted (1) or rejected (0). Shows whether the model's self-reported confidence correlates with actual quality. A well-calibrated model should have higher acceptance at high confidence scores.

4. **Domain quality comparison** (bar chart): Acceptance rate per exam domain. Identifies which domains produce better AI output (some domains have better training data).

---

### Section E — Cost Tracker

**Purpose:** Budget oversight for AI API costs. Different models have very different costs.

**Monthly cost breakdown:**
| Month | Batches | MCQs Generated | Avg Cost/MCQ (₹) | Total (₹) | Budget (₹) | Status |
|---|---|---|---|---|---|---|
| Sep 2024 | 28 | 1,400 | 2.40 | 3,360 | 5,000 | ✅ Under budget |
| Oct 2024 (MTD) | 12 | 600 | 2.80 | 1,680 | 5,000 | ✅ On track |

**Model cost comparison:** Side-by-side cost per MCQ for each model config used in batches. Helps the AI Gen Manager decide which model gives the best cost/quality tradeoff.

**Cost alert threshold:** Configurable in model config. If MTD cost exceeds 80% of monthly budget: amber warning. If 100%: red alert + in-app notification to Analytics Manager (42).

---

### Section F — Batch Detail Drawer

460px right drawer. Tabs: **Summary | MCQ List | Config Used**

#### Summary Tab

**Batch header:** Batch Ref · Domain · Subject · Topic · Difficulty · Created by · Created at

**Stats panel:**
| Metric | Value |
|---|---|
| Requested / Generated | 50 / 47 (API returned fewer than requested) |
| Approved / Rejected / Pending | 42 / 3 / 2 |
| Acceptance Rate | 89.4% |
| API Cost | ₹131.60 |
| Generation Time | 3 min 42s |
| Model Used | GPT-4o (config: "SSC Standard") |

**Notes:** If AI Gen Manager added batch-level notes for Division D SMEs, shown here.

**Status history:** Timeline of status changes (QUEUED → GENERATING → REVIEW_PENDING → REVIEW_IN_PROGRESS → APPROVED).

#### MCQ List Tab

Table of all MCQs in this batch with their individual review status.

| Column | Notes |
|---|---|
| # | Sequence number |
| Status | PENDING / APPROVED / REJECTED / FLAGGED_FOR_REVISION |
| Confidence | AI confidence score (0.0–1.0) |
| Review Note | If rejected/flagged — truncated, hover for full |
| Reviewed At | Datetime |
| Actions | [Review →] opens individual MCQ review panel |

Clicking [Review →] scrolls to the MCQ review queue section and auto-loads that specific MCQ.

#### Config Used Tab

Shows the full model configuration that was used for this batch (read-only snapshot, even if the config has since been updated):
- Model provider + model ID
- System prompt (full text)
- User prompt template (with the substituted values highlighted: {domain} = SSC, {topic} = Data Interpretation, etc.)
- Temperature, max_tokens settings

**[Use This Config for New Batch]** — pre-fills the Create Batch modal with this config selected.

---

### Section G — Create Batch Modal

Triggered by [+ Create Batch] button.

**Step 1 — Generation Parameters:**
| Field | Control | Notes |
|---|---|---|
| Domain | Select (required) | SSC / RRB / NEET / JEE / AP Board / TS Board |
| Subject | Select (required, cascades from domain) | — |
| Topic | Text input (required) | Free text — specific topic within subject |
| Difficulty Target | Select: EASY / MEDIUM / HARD / MIXED | MIXED generates proportional blend |
| Count | Number input (required) | 5–100 MCQs per batch. Above 100: warning "Very large batches have higher rejection rates. Consider splitting." |
| Model Config | Select | Only ACTIVE configs shown. [View Config] shows prompt details. |
| Notes for Division D | Textarea (optional) | Max 500 chars — guidance for SMEs reviewing these AI MCQs |

**Step 2 — Preview Prompt:**
- Shows the rendered prompt that will be sent to the AI API (system prompt + filled user prompt)
- AI Gen Manager can verify the topic and parameters before committing API cost
- Estimated cost (based on avg tokens for this config): "Est. ₹{N} for {count} MCQs"

**[Generate Now]:**
- Creates `analytics_ai_batch` record with status = QUEUED
- Triggers `run_ai_generation_batch` Celery task
- Modal closes with toast: "Batch {ref} queued — you'll be notified when generation is complete (~{est_min} min)"
- Batch card appears in Batch Management Table with ⏳ GENERATING status

---

### Section H — Model Configuration Manager

Accessible via [⚙ Manage Model Configs] button. Opens a full-page modal.

**Config list:** All `analytics_ai_model_config` records.

**Per-config card:**
- Name, model provider, model ID, temperature
- Active/Inactive status toggle (AI Gen Manager only)
- Average acceptance rate (computed from historical batches using this config)
- Average cost per MCQ
- [Edit] opens edit form (below)
- [Test Config] — generates 3 sample MCQs with the current config (costs ~₹5–10) to validate a new or changed prompt before using it for a full batch

**Edit/Create config form:**
| Field | Control |
|---|---|
| Name | Text |
| Model Provider | Select: OPENAI / ANTHROPIC / CUSTOM |
| Model ID | Text (e.g., `gpt-4o`, `claude-sonnet-4-6`) |
| System Prompt | Textarea (large) |
| User Prompt Template | Textarea — must include `{domain}`, `{subject}`, `{topic}`, `{difficulty}`, `{count}` placeholders |
| Temperature | Range slider 0.0–1.0 |
| Max Tokens | Number input |
| API Key Source | Select: use platform AI API key (from config) or [Custom Key] |
| Monthly Budget (₹) | Number input — threshold for cost alerts |

**[Save Config]:** Saved. AI Gen Manager can immediately use it in batch creation.
**[Test Config]:** Generates 3 test MCQs. Results shown in a preview modal. Test MCQs NOT added to any batch or stored permanently.

---

## 5. Access Control

| Gate | Rule |
|---|---|
| Page access | AI Generation Manager (45), Data Engineer (43) read-only, Platform Admin (10) |
| [+ Create Batch] | AI Generation Manager (45), Platform Admin (10) |
| Review MCQs (Approve/Reject) | AI Generation Manager (45), Platform Admin (10) |
| [Review All in Batch] bulk approval | AI Generation Manager (45), Platform Admin (10) — bulk approval requires confirmation |
| [Cancel Batch] | AI Generation Manager (45) — own batches only; Platform Admin (10) — any batch |
| Model Config create/edit | AI Generation Manager (45), Platform Admin (10) |
| Model Config active toggle | Platform Admin (10) only — to prevent AI Gen Manager from accidentally disabling the only active config |
| Cost Tracker visibility | AI Generation Manager (45), Analytics Manager (42), Platform Admin (10) |
| Data Engineer (43) | Read-only: batch list, quality metrics, cost tracker. Cannot create batches or review MCQs. |

---

## 6. Edge Cases & Error States

| Scenario | Behaviour |
|---|---|
| AI API call fails during generation | Batch status → FAILED. AI Gen Manager and Data Engineer notified: "Batch {ref} failed — API error: {message}. [Retry →]". [Retry] re-queues the Celery task. 3 total attempts before permanent failure. |
| AI returns fewer MCQs than requested | Common (API may return 47 of 50). `generated_count` = actual. No error — expected behaviour documented in batch summary. |
| AI generates a question identical to an existing question in the bank | Detected post-generation by `analytics_ai_generated_mcq` dedup check (hash of `question_text`). Auto-set to `review_status = FLAGGED_FOR_REVISION` with note: "Possible duplicate of question {id} in bank. Verify before approving." |
| No active model configs | [+ Create Batch] disabled: "No active model configurations. [Configure a model →]" linking to Model Config Manager. |
| Monthly budget exceeded (100%) | New batch creation blocked: "Monthly AI budget (₹{N}) is exhausted. Contact Analytics Manager to increase budget or wait until next month." Platform Admin can override. |
| Review queue > 1,000 pending MCQs | Warning banner: "Review backlog is high ({N} MCQs). Consider using [Approve All in Batch] for trusted batches to clear the queue faster." |
| AI Gen Manager approves MCQ → Division D rejects it | Division D rejection creates a task notification back to AI Gen Manager: "Division D rejected AI MCQ {id}: '{reason}'. This MCQ was from batch {ref}. Consider updating the model prompt for this topic." Tracked in quality metrics as "Division D rejection rate" (separate from AI Gen Manager rejection rate). |

---

## 7. UI Patterns

### Loading States
- KPI bar: 8-tile shimmer
- Batch table: 10-row shimmer
- MCQ review queue: 3-card shimmer
- Quality metrics charts: chart skeleton per panel
- Cost tracker: table skeleton

### Toasts
| Action | Toast |
|---|---|
| Batch created | ✅ "Batch {ref} queued — generation starts shortly" (4s) |
| MCQ approved | ✅ "MCQ approved — added to Division D queue" (2s, auto-dismiss) |
| MCQ rejected | ✅ "MCQ rejected" (2s, auto-dismiss) |
| Batch bulk approved | ✅ "{N} MCQs approved and sent to Division D queue" (4s) |
| Batch cancelled | ✅ "Batch {ref} cancelled" (3s) |
| Config test complete | ✅ "Test complete — 3 sample MCQs generated. Review below." (4s) |

### Responsive
| Breakpoint | Behaviour |
|---|---|
| Desktop (≥1280px) | Full layout — MCQ review cards full-width, charts side by side |
| Tablet | MCQ review cards full-width. Charts stacked. Keyboard shortcuts disabled. |
| Mobile | MCQ review card simplified (question + options + 3 buttons). Batch management table hidden (too wide). Note: "Full batch management requires desktop." |

---

*Page spec complete.*
*H-07 covers: AI pipeline KPI bar → batch management table (QUEUED/GENERATING/REVIEW_PENDING/APPROVED/REJECTED) → MCQ review queue (card-by-card with keyboard shortcuts and batch-level bulk approve/reject) → rejection reason analytics → confidence score calibration scatter → domain quality comparison → cost tracker with budget alerts → batch detail drawer (stats / MCQ list / config snapshot) → create batch 2-step wizard (params + prompt preview) → model configuration manager with live test.*
