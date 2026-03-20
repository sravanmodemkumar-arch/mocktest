# C-15 — AI Pipeline Dashboard

> **Route:** `/engineering/ai-pipeline/`
> **Division:** C — Engineering
> **Primary Role:** Platform Admin (Role 10) · AI/ML Engineer (Role 17)
> **Read Access:** Backend Engineer (Role 11) · DevOps/SRE (Role 14)
> **File:** `c-15-ai-pipeline.md`
> **Priority:** P2
> **Status:** ✅ Spec done

---

## 1. Page Name & Route

**Page Name:** AI Pipeline Dashboard
**Route:** `/engineering/ai-pipeline/`
**Part-load routes:**
- `/engineering/ai-pipeline/?part=kpi` — pipeline health KPI
- `/engineering/ai-pipeline/?part=jobs` — batch job status table
- `/engineering/ai-pipeline/?part=drawer&job_id={id}` — job detail drawer (ai-job-drawer)
- `/engineering/ai-pipeline/?part=funnel` — auto-rejection funnel
- `/engineering/ai-pipeline/?part=prompt-ab` — prompt version A/B comparison
- `/engineering/ai-pipeline/?part=model-tracking` — LLM model tracking panel
- `/engineering/ai-pipeline/?part=review-queue` — human review queue depth

---

## 2. Purpose (Business Objective)

The AI Pipeline Dashboard tracks the platform's MCQ (Multiple Choice Question) generation pipeline — the core AI capability that uses LLMs (Claude, GPT-4o, Gemini) to generate exam questions at scale. With 2M+ questions already in the bank and continuous generation for new domains, this pipeline processes thousands of questions per day.

The pipeline is expensive (₹8L–₹15L/month in LLM API costs) and generates questions that must meet strict quality gates before being added to the question bank. This page gives AI/ML Engineers visibility into pipeline health, rejection rates, prompt performance, and the human review queue.

The most important metric is the **approval rate** — the percentage of AI-generated questions that pass all quality gates and reach the question bank. A low approval rate means expensive LLM calls are being wasted on low-quality output, pointing to prompt engineering problems.

**Business goals:**
- Monitor MCQ generation throughput and quality in real-time
- Diagnose why questions are being rejected (hallucination vs format vs duplicate)
- Compare prompt versions A/B to continuously improve approval rates
- Track LLM model performance and cost per approved question
- Manage human review queue depth to ensure reviewers aren't overloaded

---

## 3. User Roles

| Role | Access Level | Permissions |
|---|---|---|
| Platform Admin (10) | Level 5 | Full view + write: cancel jobs · change model config · manage prompt versions |
| AI/ML Engineer (17) | Level 4 | Full view + write: cancel jobs · change model config · manage prompt versions · create prompt versions |
| Backend Engineer (11) | Level 4 — Read | View pipeline status + job logs |
| DevOps / SRE (14) | Level 4 — Read | View infrastructure impact (concurrency, cost) of pipeline |

---

## 4. Section-Wise Detailed Breakdown

---

### Section 1 — Page Header & Pipeline Status

**Purpose:** Instant pipeline health and throughput at page load.

**Header elements:**
- H1 "AI Pipeline Dashboard"
- Pipeline status badge: ✅ Running · ⚠ Degraded · ❌ Stopped · 🔄 Processing
- Today's generation counter: "1,842 questions generated today"
- Approval rate today: "68% approved — 1,248 reached question bank"
- Active jobs count: "3 jobs running"
- "Trigger New Job" button (AI/ML Engineer · Admin)
- Hard stop toggle: "Emergency halt all AI generation" (Admin only · 2FA required · kills all active Celery AI jobs)

**Quality alert banner:**
- If approval rate drops below 50%: amber banner "⚠ Approval rate low (42%). High rejection rate detected. Review rejection funnel."
- If approval rate drops below 30%: red banner "🚨 Critical quality degradation. Consider pausing pipeline until prompts reviewed."

---

### Section 2 — KPI Strip

**KPI Cards:**

| Card | Metric | Alert |
|---|---|---|
| Questions Generated Today | Count from all jobs | — |
| Approval Rate | Approved / Generated % | < 50% amber · < 30% red |
| Rejected Today | Count by all rejection types | — |
| Human Review Queue | Questions awaiting manual review | > 500 amber · > 2,000 red |
| Active Jobs | Currently running Celery AI jobs | — |
| LLM Cost Today (est.) | API token spend today | > 80% daily budget = amber |

---

### Section 3 — Batch Job Status Table

**Purpose:** All MCQ generation batch jobs with status and throughput metrics.

**Table Columns:**

| Column | Description | Sortable |
|---|---|---|
| Job ID | Short ID | — |
| Status | ✅ Completed · ❌ Failed · 🔄 Running · ⏸ Queued · 🚫 Cancelled | ✅ |
| Domain | Exam domain (JEE · NEET · UPSC · Class 10 · etc.) | ✅ |
| Target Questions | How many questions the job was asked to generate | ✅ |
| Generated | Count actually generated so far | ✅ |
| Approved | Count passing all quality gates | ✅ |
| Rejected | Count rejected (breakdown in drawer) | ✅ |
| In Review | Count awaiting human review | — |
| Model | LLM used (Claude · GPT-4o · Gemini) | ✅ |
| Prompt Version | Which prompt template was used | ✅ |
| Cost (est.) | Token cost for this job | ✅ |
| Started | Timestamp | ✅ |
| Duration | Elapsed time | — |
| Triggered By | Engineer or automated schedule | — |

**Row colour rules:**
- Approval rate < 50%: amber row
- Approval rate < 30%: red row
- Job failed: red left border

**Filter bar:**
- Domain · Status · Model · Prompt version · Date range

**Data Flow:**
- Job data from `platform_ai_jobs` table (updated by Celery worker on each question processed)
- 60s HTMX poll; guard: no drawer open

---

### Section 4 — Job Detail Drawer (ai-job-drawer)

**Purpose:** Deep dive into a specific job — config, sample output, errors, and cost.

**Drawer Width:** 640px
**Tabs:**

---

#### Tab 1 — Job Config

**Fields:**

| Field | Value |
|---|---|
| Job ID | `job-2026-03-15-jee-001` |
| Domain | JEE Advanced |
| Subject | Physics — Mechanics |
| Topic | Rotational Motion |
| Difficulty | Hard |
| Target Questions | 500 |
| Question Types | MCQ-single, MCQ-multiple, Integer answer |
| LLM Model | Claude Sonnet 4.6 |
| Prompt Version | v4.2 (current stable) |
| Temperature | 0.7 |
| Max Tokens | 1,200 per question |
| Batch Size | 10 questions per API call |
| Parallel Workers | 4 |
| Quality Checks | Hallucination detection · Duplicate detection · Format validation · Copyright scan |
| Triggered By | AI/ML Engineer: Rohan |
| Started At | 2h ago |
| Status | ✅ Completed |

**Actions:**
- "Cancel job" (if running) → stops Celery workers for this job
- "Re-run with same config" → creates identical job
- "Re-run failed questions only" → creates job targeting only questions that were rejected

---

#### Tab 2 — Sample Questions

**Purpose:** View sample approved and rejected questions from this job for quality assessment.

**Tabs within this tab:**
- Approved samples (10 random)
- Rejected samples (10 random, with rejection reason)

**Sample question card:**
- Question text (full)
- Options A/B/C/D
- Correct answer
- Explanation
- Metadata: topic · difficulty · LLM model · prompt version · generation time
- Quality check results: Hallucination: Pass ✅ · Duplicate: Pass ✅ · Format: Pass ✅
- For rejected: Rejection reason highlighted in red

**Quality reviewer actions (AI/ML Engineer):**
- "Approve this question" → moves rejected question to review queue (overrides auto-rejection)
- "Confirm rejection" → marks as permanently rejected with reason
- "Flag for review" → escalates to human review queue

---

#### Tab 3 — Errors

**Purpose:** Technical error log for this job.

**Error Table:**

| Timestamp | Error Type | Message | Question Index | Retried |
|---|---|---|---|---|
| 2h ago | API rate limit | Claude API: 429 Too Many Requests | 142 | ✅ (succeeded on retry 2) |
| 2h ago | Format validation | Response missing OPTIONS section | 158 | ✅ (succeeded on retry 1) |
| 1h ago | API timeout | Request timed out after 30s | 341 | ❌ (3 retries, all failed) |

**Error categories:**
- LLM API errors: rate limits, timeouts, model errors
- Format errors: LLM response doesn't match expected JSON schema
- Content errors: flagged by quality checks

**Retry logic:** Up to 3 automatic retries with exponential backoff; after 3 failures: question skipped + logged

---

#### Tab 4 — Cost

**Purpose:** Detailed cost breakdown for this specific job.

| Metric | Value |
|---|---|
| Input tokens | 1,284,000 |
| Output tokens | 428,000 |
| Total tokens | 1,712,000 |
| Model rate | Claude Sonnet: $3/$15 per M in/out |
| LLM API cost | ₹892 |
| Questions generated | 487 |
| Questions approved | 332 |
| Cost per generated question | ₹1.83 |
| Cost per approved question | ₹2.69 |
| Wasted spend (rejected questions) | ₹270 (30% of cost) |

**Cost efficiency indicator:**
- If cost per approved question > ₹5: amber warning "High cost per approved question. Review rejection rate and prompt quality."
- Historical comparison: "vs last 7-day avg: ₹2.41 (+12%)"

---

### Section 5 — Auto-Rejection Funnel

**Purpose:** Visualise where questions drop out of the pipeline and why — the key quality diagnostic.

**Funnel Visualization (last 7 days):**

```
Questions Requested:      10,000 (100%)
        ↓
Generated by LLM:          9,842 (98.4%) — 158 failed (API errors, timeouts)
        ↓
Format Validation Pass:    9,410 (94.1%) — 432 failed (JSON schema violations, incomplete responses)
        ↓
Hallucination Check Pass:  8,840 (88.4%) — 570 failed (factual errors detected)
        ↓
Duplicate Check Pass:      8,200 (82.0%) — 640 failed (similar to existing question bank)
        ↓
Copyright Scan Pass:       8,150 (81.5%) — 50 failed (potential copyright match)
        ↓
Human Review:              8,150 → 7,200 approved by reviewers (88.3% of reviewed)
        ↓
Added to Question Bank:    7,200 (72.0% overall approval rate)
```

**Each funnel stage is clickable:**
- Click "Format Validation: 432 failed" → drawer showing sample failed questions + error details + most common failure patterns

**Rejection reason breakdown (pie chart):**
- Hallucination: 41%
- Duplicate: 46%
- Format error: 12%
- Copyright: 1%

**Trend charts:**
- Approval rate by day (last 30 days)
- Rejection by reason by day (stacked bar)
- Helps identify: did a prompt change improve hallucination rates?

**Domain comparison:**
- Approval rate by exam domain (JEE vs NEET vs UPSC vs Class 10 etc.)
- Some domains have naturally higher rejection rates (e.g., UPSC current affairs: higher hallucination risk)

---

### Section 6 — Prompt Version A/B Comparison

**Purpose:** Compare performance of different prompt template versions to drive data-based prompt improvements.

**Prompt Versions Table:**

| Version | Status | Created | Created By | Domain | Total Generated | Approval Rate | Avg Cost/Q | Avg Quality Score |
|---|---|---|---|---|---|---|---|---|
| v4.2 | ✅ Active (primary) | Mar 2026 | Rohan (AI/ML) | All domains | 28,400 | 72.1% | ₹2.69 | 4.2/5 |
| v4.3 | 🔵 A/B Test (10%) | Mar 2026 | Rohan (AI/ML) | All domains | 2,840 | 78.4% | ₹2.82 | 4.5/5 |
| v4.1 | ⬜ Archived | Feb 2026 | Priya (Admin) | All domains | 45,200 | 68.2% | ₹2.55 | 4.0/5 |

**Active A/B test:**
- Traffic split: v4.2 (90%) / v4.3 (10%)
- Statistical significance: "80% confidence — needs more data (currently 2,840 samples, need ~5,000)"
- Projected winner: v4.3 (higher approval rate + quality score; slight cost increase)

**Side-by-side comparison (click "Compare" on any two versions):**
- Approval rate: 72.1% vs 78.4% (+8.7% relative improvement)
- Hallucination rate: 11.6% vs 7.2% (-38% improvement)
- Duplicate rate: 7.8% vs 7.4% (-5%)
- Avg quality score (human reviewer rating): 4.2 vs 4.5
- Cost per approved question: ₹2.69 vs ₹2.82 (+5% cost)

**Promote prompt version:**
- "Promote v4.3 to Primary" button (AI/ML Engineer · Admin)
- Confirmation modal: "This will make v4.3 the primary prompt for 100% of traffic. v4.2 will be archived."
- 2FA: not required (prompt change is reversible)

**Create new prompt version:**
- Opens prompt editor (large textarea with syntax highlighting for Jinja2 template syntax)
- Template variables documented inline: `{{subject}}`, `{{topic}}`, `{{difficulty}}`, `{{num_questions}}`, `{{examples}}`
- "Test prompt" button → runs 10 questions as a test batch · shows sample output before saving
- Version naming: auto-incremented (v4.4, v4.5, etc.)
- "Save as Draft" → not used in production yet; "Deploy as A/B Test (X%)" → routes X% of traffic to new version

---

### Section 7 — LLM Model Tracking Panel

**Purpose:** Track performance and cost across all three LLM providers used in the pipeline.

**Model Performance Table (last 30 days):**

| Model | Provider | Questions Generated | Approval Rate | Avg Latency | Cost (30d) | Cost per Approved Q | Status |
|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | Anthropic | 84,200 | 74.2% | 8.4s | ₹2,84,000 | ₹4.54 | ✅ Primary |
| GPT-4o | OpenAI | 12,400 | 71.8% | 6.2s | ₹48,000 | ₹5.38 | 🔵 Secondary |
| Gemini 1.5 Pro | Google | 8,200 | 68.4% | 7.1s | ₹28,000 | ₹4.98 | 🔵 Secondary |

**Model configuration (per model):**
- Primary/Secondary/Inactive toggle
- Traffic allocation % (must sum to 100%)
- Per-domain model routing: "Use Gemini for UPSC domains · Claude for Science domains"
- API key status: links to C-14 Secrets Manager
- API rate limit current usage vs limit

**Model health indicators:**
- API error rate per model (last 1h)
- Latency trend
- "Model unavailable" alert if API error rate > 5%

**Model routing rules:**
- Fallback chain: if Claude API returns 5xx → fall back to GPT-4o → if GPT-4o fails → fall back to Gemini
- Fallback events logged and shown in Model Health history

---

### Section 8 — Human Review Queue

**Purpose:** Monitor the depth of the queue of AI-generated questions awaiting human expert review.

**Queue Overview:**

| Domain | Questions in Queue | Avg Wait Time | Reviewers Assigned | Review Rate (q/day) | Estimated Clearance |
|---|---|---|---|---|---|
| JEE / Engineering | 420 | 2.4 days | 3 | 84/day | 5 days |
| NEET / Medical | 280 | 1.8 days | 2 | 72/day | 4 days |
| UPSC | 84 | 1.2 days | 1 | 42/day | 2 days |
| Class 10 | 142 | 0.9 days | 2 | 48/day | 3 days |
| **Total** | **926** | **1.7 days avg** | | | |

**Alert thresholds:**
- Queue > 500: amber banner
- Queue > 2,000: red banner + notify Content team (Div H)
- Any domain estimated clearance > 14 days: amber flag

**Review rate trend:**
- Chart: review rate (questions approved/day by reviewers) over last 30 days
- Identifies bottlenecks: if generation rate > review rate → queue growing → pipeline should throttle

**Pipeline throttle recommendation:**
- If total queue > 1,500: "Consider reducing pipeline throughput. Queue growing faster than review capacity."
- AI/ML Engineer can set "max queue depth" — pipeline automatically pauses when queue exceeds this threshold

**Actions:**
- "Set max queue depth" → number input → Celery job throttles pipeline output when threshold hit
- "Notify reviewer team" → sends email to Content team (Div H) showing queue status

---

## 5. User Flow

### Flow A — Weekly Pipeline Quality Review

1. AI/ML Engineer opens `/engineering/ai-pipeline/` on Monday
2. KPI: approval rate for last 7 days = 68% (below amber threshold of 70%)
3. Opens rejection funnel: Hallucination check: 18% rejection rate (was 12% last week)
4. Identifies: hallucination rate increased after Claude model was updated (GPT-4o version change)
5. Opens Prompt A/B panel: v4.2 vs v4.3
6. v4.3 shows better hallucination resistance (7.2% vs 11.6%)
7. Statistical significance: 85% confidence
8. Promotes v4.3 to primary
9. Approval rate recovers to 74% in next 2 days

### Flow B — New Domain Onboarding (UPSC Current Affairs)

1. Content team requests AI generation for UPSC Current Affairs (new domain)
2. AI/ML Engineer creates new batch job: domain = UPSC · subject = Current Affairs · target = 1,000
3. Chooses GPT-4o (better for current affairs, lower hallucination)
4. Creates new prompt version v4.4 with specific UPSC formatting rules
5. Deploys v4.4 as A/B test at 50% for UPSC domain only
6. After 100 questions: approval rate for v4.4 = 52% (worse than v4.3 at 65%)
7. Reverts UPSC to v4.3; v4.4 archived with notes

### Flow C — Human Review Queue Overflow

1. KPI: review queue = 2,200 (red alert)
2. AI/ML Engineer opens Review Queue panel
3. JEE domain: 1,400 in queue · estimated clearance 17 days
4. Sets max queue depth: 1,500
5. Pipeline auto-pauses JEE generation until queue drops below 1,500
6. Notifies Content team (Div H) to increase reviewer allocation
7. After 5 days: queue drops to 800 → pipeline resumes

---

## 6. Component Structure (Logical)

```
AIPipelineDashboardPage
├── PageHeader
│   ├── PipelineStatusBadge
│   ├── PageTitle
│   ├── DailyGenerationCounter
│   ├── ApprovalRateToday
│   ├── TriggerJobButton
│   └── EmergencyHaltToggle (Admin)
├── QualityAlertBanner (conditional)
├── KPIStrip × 6
├── BatchJobTable
│   ├── FilterBar
│   └── JobRow × N
├── AIJobDrawer (640px)
│   └── DrawerTabs
│       ├── JobConfigTab
│       ├── SampleQuestionsTab
│       ├── ErrorsTab
│       └── CostTab
├── AutoRejectionFunnel
│   ├── FunnelVisualization
│   ├── RejectionPieChart
│   ├── TrendCharts
│   └── DomainComparisonTable
├── PromptVersionABPanel
│   ├── VersionsTable
│   ├── ActiveABTestCard
│   ├── SideBySideComparison
│   └── PromptEditor (create/edit)
├── LLMModelTrackingPanel
│   ├── ModelPerformanceTable
│   └── ModelConfigSection
└── HumanReviewQueuePanel
    ├── QueueOverviewTable
    ├── ReviewRateTrendChart
    └── ThrottleConfig
```

---

## 7. Data Model (High-Level)

### platform_ai_jobs

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| domain | VARCHAR(100) | |
| subject | VARCHAR(100) | |
| topic | VARCHAR(200) | |
| difficulty | ENUM | easy/medium/hard/mixed |
| target_questions | INTEGER | |
| questions_generated | INTEGER | running count |
| questions_approved | INTEGER | running count |
| questions_rejected | INTEGER | running count |
| questions_in_review | INTEGER | running count |
| llm_model | ENUM | claude_sonnet/gpt4o/gemini_pro |
| prompt_version_id | UUID FK → platform_ai_prompt_versions | |
| temperature | DECIMAL(3,2) | |
| status | ENUM | queued/running/completed/failed/cancelled |
| total_input_tokens | INTEGER | |
| total_output_tokens | INTEGER | |
| estimated_cost_inr | DECIMAL(10,2) | |
| celery_task_id | VARCHAR(255) | |
| triggered_by | UUID FK → platform_staff | nullable |
| started_at | TIMESTAMPTZ | nullable |
| completed_at | TIMESTAMPTZ | nullable |

### platform_ai_prompt_versions

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| version | VARCHAR(20) | e.g., "v4.2" |
| status | ENUM | draft/ab_test/active/archived |
| template | TEXT | Jinja2 template with {{variables}} |
| traffic_allocation_pct | SMALLINT | 0–100 |
| domains | JSONB | array of domains this version applies to (null = all) |
| total_generated | INTEGER | cumulative |
| total_approved | INTEGER | cumulative |
| approval_rate | DECIMAL(5,2) | computed |
| avg_quality_score | DECIMAL(3,2) | from human reviewer ratings |
| cost_per_approved_q_inr | DECIMAL(6,2) | |
| created_by | UUID FK → platform_staff | |
| created_at | TIMESTAMPTZ | |
| promoted_at | TIMESTAMPTZ | nullable |
| archived_at | TIMESTAMPTZ | nullable |

---

## 8. Validation Rules

| Rule | Detail |
|---|---|
| Traffic allocation total | Must sum to exactly 100% across all active prompt versions |
| New prompt test | Must run "Test prompt" (10-question test batch) before deploying as A/B test |
| Max queue depth | Minimum 100 · Maximum 10,000; if set to 0, pipeline generation is paused entirely |
| Emergency halt | Admin only · 2FA required · creates automatic C-18 incident with reason |
| Model routing | Fallback chain must have at least 1 fallback (cannot have zero fallback models) |
| A/B test minimum | A/B test must run for minimum 1,000 questions before statistical significance is claimed |
| Prompt archived | Cannot archive the currently active (primary) prompt version — must first promote another version |

---

## 9. Security Considerations

| Control | Detail |
|---|---|
| LLM API keys | Stored in C-14 Secrets Manager; injected into Celery workers at runtime; never in environment variables |
| Generated question content | Before human review, questions stored in internal S3 bucket (not question bank) — not accessible to institution users |
| Prompt template access | Prompt templates are internal IP; access restricted to AI/ML Engineer + Admin; not visible to institution-facing roles |
| Cost overage protection | Hard stop at 95% monthly budget (configured in C-16); this page shows the soft alert at 80% |
| API rate limit protection | Celery worker implements per-model rate limit compliance; does not expose rate limit details in UI (could be used to time attacks) |

---

## 10. Edge Cases (System-Level)

| Scenario | Handling |
|---|---|
| LLM API returns empty response | Retry × 3 with different temperature setting; if all fail: question skipped, logged as "API empty response" |
| All three LLM providers unavailable simultaneously | Pipeline halts automatically; C-18 incident created; AI/ML Engineer alerted; jobs marked as "pending restart" |
| Prompt template syntax error | Pre-validated on save using Jinja2 parser; deployment blocked if template fails to parse |
| Duplicate question detection against 2M+ question bank | Uses vector similarity search (FAISS or pgvector index); threshold: cosine similarity > 0.92 → rejected as duplicate |
| Job generates correct count but quality catastrophically low | If approval rate < 10% after first 100 questions: job auto-pauses; AI/ML Engineer alerted; "Continue" or "Cancel" decision required |
| Human review queue cleared faster than expected | Pipeline resumes automatically (queue < max_depth threshold) |
| Cost spike mid-job (model pricing change) | Cost calculated at job completion; in-job estimate may differ; significant variance (> 20%) flagged in cost tab |

---

## 11. Performance & Scaling Strategy

| Concern | Strategy |
|---|---|
| Job status polling | Jobs update `platform_ai_jobs` row every 100 questions; HTMX polls every 60s; acceptable latency for dashboard display |
| Funnel calculation | Pre-computed by Celery beat every 30 min from `platform_ai_generated_questions` aggregate table; page reads from pre-computed result |
| A/B statistical significance | Calculated server-side with Python `scipy.stats` on prompt version comparison request; < 500ms for 10,000 samples |
| Sample question display | 10 random samples fetched per tab open; no full dataset loaded; drawer-only load |
| LLM API throughput | Each Celery worker: 4 parallel API calls × 10 questions/call = 40 questions/batch/worker; with 4 workers: 160 questions/batch; ~2,400 questions/hour throughput at current parallelism |
| Review queue calculation | Counts from `platform_ai_generated_questions WHERE status = pending_review GROUP BY domain`; index on status + domain; < 50ms |
