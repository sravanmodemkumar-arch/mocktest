# Group 1 — Division H: Data & Analytics — Pages Reference

> **Division:** H — Data & Analytics
> **Roles:** Analytics Manager (42) · Data Engineer (43) · Data Analyst (44) · AI Generation Manager (45) · Report Designer (46)
> **Base URL prefix:** `/analytics/`
> **Theme:** Dark (`portal_base_dark.html`)
> **Status key:** ✅ Spec done · 🔨 In progress · ⬜ Not started

---

## Scale Context (always keep in mind)

| Dimension | Value |
|---|---|
| Total institutions | **2,050** (1,000 schools + 800 colleges + 100 coaching + 150 groups) |
| Total students | **2.4M–7.6M** depending on active enrollment period |
| Peak concurrent exam load | **74,000 simultaneous submissions** |
| Questions in bank | **2M+** across 6 exam domains |
| Active test series | **800+** |
| Exam domains | SSC · RRB · NEET · JEE · AP Board · TS Board |
| AI-generated MCQs in pipeline | Variable — ~5,000–50,000/month target |
| Analytics schema lag | Nightly batch — data is max 24h old (intra-day for P0 metrics) |
| Celery aggregation schemas | One query spans 2,050 tenant schemas — ALWAYS via pre-aggregated tables, never live cross-tenant scan |

---

## Division H — Role Summary

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 42 | Analytics Manager | 1 | Platform-wide MIS; usage, revenue, exam performance trends; anomaly alerts; stakeholder reporting | No data edits; cannot trigger pipeline runs or AI batches |
| 43 | Data Engineer | 4 | EventBridge pipelines; aggregation Celery jobs; analytics schema DDL; data warehouse management; pipeline monitoring | Cannot approve AI MCQs; no business configuration |
| 44 | Data Analyst | 1 | Institution-level reports; cohort analysis; dropout signals; rank analytics; self-serve data exploration | No data edits; no pipeline management; no AI pipeline |
| 45 | AI Generation Manager | 3 | Commission AI MCQ batch jobs; review AI-generated MCQ quality before Division D queue; prompt/model configuration; cost monitoring | Cannot approve MCQs for publish (Division D Approver only); cannot modify existing question bank |
| 46 | Report Designer | 1 | Design institution-facing MIS report templates; schedule automated delivery; preview with sample data | No data edits; cannot trigger pipeline runs |

---

## Page Inventory

| # | Page Name | URL | File | Priority | Status | Primary Roles |
|---|---|---|---|---|---|---|
| H-01 | Analytics Dashboard | `/analytics/` | `h-01-analytics-dashboard.md` | **P0** | ✅ | 42, 44, 43, 45, 46, 10 |
| H-02 | Student Performance Analytics | `/analytics/students/` | `h-02-student-performance.md` | P1 | ✅ | 42, 44, 10 |
| H-03 | Institution Analytics | `/analytics/institutions/` | `h-03-institution-analytics.md` | P1 | ✅ | 42, 44, 10 |
| H-04 | Question Intelligence | `/analytics/questions/` | `h-04-question-intelligence.md` | P1 | ✅ | 42, 44, 43, 10 |
| H-05 | Exam & Domain Analytics | `/analytics/exams/` | `h-05-exam-analytics.md` | P1 | ✅ | 42, 44, 10 |
| H-06 | Data Pipeline Monitor | `/analytics/pipelines/` | `h-06-pipeline-monitor.md` | **P0** | ✅ | 43, 10 |
| H-07 | AI MCQ Generation | `/analytics/ai-generation/` | `h-07-ai-generation.md` | P1 | ✅ | 45, 43, 10 |
| H-08 | Report Studio | `/analytics/report-studio/` | `h-08-report-studio.md` | P2 | ✅ | 46, 42, 44, 10 |

---

## Role-to-Page Access Matrix

| Page | Analytics Manager (42) | Data Engineer (43) | Data Analyst (44) | AI Gen Manager (45) | Report Designer (46) | Platform Admin (10) |
|---|---|---|---|---|---|---|
| H-01 Analytics Dashboard | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| H-02 Student Performance | ✅ Full | Read | ✅ Full | — | Read | ✅ Full |
| H-03 Institution Analytics | ✅ Full | Read | ✅ Full | — | Read | ✅ Full |
| H-04 Question Intelligence | ✅ Full | ✅ Full | ✅ Full | Read | — | ✅ Full |
| H-05 Exam Analytics | ✅ Full | Read | ✅ Full | — | Read | ✅ Full |
| H-06 Pipeline Monitor | Read | ✅ Full | — | Read | — | ✅ Full |
| H-07 AI Generation | — | Read | — | ✅ Full | — | ✅ Full |
| H-08 Report Studio | ✅ Approve | — | Read | — | ✅ Full | ✅ Full |

> **Read** = view data, no create/edit/delete. **—** = no access.

---

## Critical Action Ownership

| Action | Role |
|---|---|
| Trigger manual pipeline re-run | Data Engineer (43), Platform Admin (10) |
| Archive dead questions (bulk) | Data Analyst (44) — flags for review; Data Engineer (43) — executes |
| Create AI generation batch | AI Generation Manager (45) |
| Approve/reject AI-generated MCQs | AI Generation Manager (45) |
| Publish AI MCQs to Division D queue | AI Generation Manager (45) |
| Publish institution report template | Analytics Manager (42) |
| Schedule institution report delivery | Report Designer (46), Analytics Manager (42) |
| Override data freshness warning | Data Engineer (43) — via pipeline re-run |
| Configure AI model / prompt templates | AI Generation Manager (45), Platform Admin (10) |

---

## Analytics Architecture

### Cross-Tenant Aggregation Strategy

The platform has 2,050 tenant PostgreSQL schemas. A naive cross-tenant query (e.g., `SELECT COUNT(*) FROM tenant_*.exam_attempts`) at 2.4M–7.6M students is catastrophically slow — and at 74K peak concurrent, impossible in real-time.

**Solution: Pre-Aggregated Analytics Schema**

A dedicated `analytics` schema (separate from all 2,050 tenant schemas) stores pre-computed aggregate data only. No analytics page ever queries tenant schemas directly in real-time.

```
Tenant schemas (2,050)          Analytics schema (1)
    └── exam_attempts     ─────▶  analytics_daily_snapshot
    └── exam_questions    ─────▶  analytics_question_stats
    └── institutions      ─────▶  analytics_institution_engagement
    └── students          ─────▶  analytics_cohort_snapshot
         (nightly Celery batch — never real-time)
```

**Data freshness guarantees:**
- Most metrics: updated nightly at 01:00–04:00 IST (max 24h lag)
- Institution engagement scores: updated weekly (Sunday 03:00 IST)
- Cohort snapshots: updated monthly (1st of month 04:00 IST)
- All pages show "Data as of: {last_computed_at}" timestamp
- Data Engineer can force a manual re-run of any pipeline job from H-06

**Caching layer:** Memcached (15-min TTL for most pages, 60-min for heavy computations like cohort analysis). `?nocache=true` param available to Data Engineer for fresh reads.

---

## Complete Data Model

### Table: `analytics_daily_snapshot`

Pre-computed daily metric aggregates. The backbone of all time-series charts in Division H.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `snapshot_date` | date | The date this metric represents |
| `metric_key` | varchar(100) | e.g., `active_institutions`, `exam_attempts_total`, `avg_score_pct`, `new_students` |
| `dimension_type` | varchar(50) | `exam_domain` · `institution_type` · `subscription_tier` · `region_state` · `none` |
| `dimension_value` | varchar(100) | e.g., `SSC`, `SCHOOL`, `Enterprise`, `Telangana` — or `_all_` for undimensioned |
| `metric_value` | decimal(20,4) | Numeric value |
| `metric_metadata` | jsonb | Optional extra context (e.g., `{"sample_size": 14200}`) |
| `computed_at` | timestamptz | When Celery job wrote this row |

Unique constraint: `(snapshot_date, metric_key, dimension_type, dimension_value)`.

Retention: 3 years of daily snapshots per metric.

---

### Table: `analytics_question_stats`

Classical Test Theory (CTT) metrics per question. Computed nightly from cross-tenant attempt data.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `question_id` | bigint | References the global question registry (not tenant-specific) |
| `domain` | varchar(50) | SSC · RRB · NEET · JEE · AP_BOARD · TS_BOARD |
| `subject` | varchar(100) | e.g., Mathematics, Physics |
| `attempt_count` | int | Total attempts across all tenants |
| `correct_count` | int | Correct answer count |
| `difficulty_index` | decimal(5,4) | `p = correct_count / attempt_count`. 0.0–1.0. Easy >0.7, Medium 0.4–0.7, Hard <0.4 |
| `discrimination_index` | decimal(5,4) | Point-biserial correlation between item score and total score. Good >0.3, Poor <0.2 |
| `omission_rate` | decimal(5,4) | Proportion of students who skipped this question |
| `distractor_stats` | jsonb | `{"A": 0.42, "B": 0.22, "C": 0.28, "D": 0.08}` — proportion choosing each option |
| `first_used_at` | date | First exam this question appeared in |
| `last_used_at` | date | Last exam this question appeared in |
| `last_computed_at` | timestamptz | When Celery job last updated this row |
| `quality_flag` | varchar(20) | `OK` · `POOR_DISCRIMINATION` · `ALL_CORRECT` · `ALL_WRONG` · `NEGATIVE_D` · `NEVER_USED` · `STALE` |

---

### Table: `analytics_institution_engagement`

Weekly engagement health score per institution. Used by H-03 and Division J (Customer Success, cross-reference only).

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `institution_id` | bigint | Platform institution ID |
| `institution_name` | varchar(300) | Denormalized for analytics queries |
| `institution_type` | varchar(20) | SCHOOL · COLLEGE · COACHING · GROUP |
| `subscription_tier` | varchar(20) | Starter · Standard · Professional · Enterprise |
| `region_state` | varchar(100) | — |
| `engagement_score` | smallint | 0–100 composite score (see formula below) |
| `churn_risk` | varchar(10) | LOW · MEDIUM · HIGH · CRITICAL |
| `exam_frequency_per_month` | decimal(6,2) | Average exams conducted per month (last 90 days) |
| `student_active_rate` | decimal(5,4) | Active students ÷ enrolled students in last 30 days |
| `question_bank_usage_pct` | decimal(5,4) | Unique questions used ÷ total available for this tier |
| `login_days_last_30` | smallint | Days with at least one admin login in last 30 days |
| `support_ticket_count_30d` | smallint | L1/L2/L3 tickets raised in last 30 days |
| `last_exam_at` | date | Date of most recent exam |
| `week_start` | date | Start of the week this snapshot covers |
| `computed_at` | timestamptz | — |

**Engagement score formula:**
- `exam_frequency_per_month`: weight 30%
- `student_active_rate`: weight 30%
- `question_bank_usage_pct`: weight 20%
- `login_days_last_30 / 30`: weight 20%
- **Churn risk thresholds:** CRITICAL <30, HIGH 30–49, MEDIUM 50–69, LOW ≥70

---

### Table: `analytics_cohort_snapshot`

Monthly student cohort retention data. Privacy-safe (no individual student IDs — aggregate by cohort).

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `cohort_month` | date | First day of month when cohort enrolled (e.g., 2024-09-01) |
| `dimension_type` | varchar(50) | `exam_domain` · `institution_type` · `region_state` · `none` |
| `dimension_value` | varchar(100) | — |
| `cohort_size` | int | Students who first appeared in this month |
| `retained_month_1` | int | Students still active in month+1 |
| `retained_month_2` | int | Students still active in month+2 |
| `retained_month_3` | int | — |
| `retained_month_6` | int | — |
| `retained_month_12` | int | — |
| `computed_at` | timestamptz | — |

---

### Table: `analytics_ai_batch`

AI MCQ generation batch jobs managed by AI Generation Manager (45).

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `batch_ref` | varchar(20) | Auto-generated: `AIB-{YYYY}{MM}-{seq}` e.g. `AIB-202409-0042` |
| `domain` | varchar(50) | Target exam domain |
| `subject` | varchar(100) | Target subject |
| `topic` | varchar(200) | Specific topic within subject |
| `difficulty_target` | varchar(10) | EASY · MEDIUM · HARD · MIXED |
| `requested_count` | smallint | How many MCQs requested |
| `model_config_id` | FK → analytics_ai_model_config | Which model + prompt template was used |
| `status` | varchar(20) | `QUEUED` · `GENERATING` · `REVIEW_PENDING` · `REVIEW_IN_PROGRESS` · `APPROVED` · `PARTIALLY_APPROVED` · `REJECTED` · `CANCELLED` |
| `generated_count` | smallint | How many MCQs the AI actually returned |
| `approved_count` | smallint | How many the AI Gen Manager approved for Division D queue |
| `rejected_count` | smallint | How many were rejected |
| `api_cost_inr` | decimal(10,2) | Cost of this batch (converted to INR at time of generation) |
| `generation_started_at` | timestamptz | — |
| `generation_completed_at` | timestamptz | — |
| `review_started_at` | timestamptz | When AI Gen Manager started reviewing |
| `review_completed_at` | timestamptz | — |
| `created_by_id` | FK → auth.User | AI Generation Manager |
| `reviewed_by_id` | FK → auth.User | — |
| `notes` | text | Generation notes passed to Division D SMEs |
| `celery_task_id` | varchar(36) | Celery task UUID for status polling |

---

### Table: `analytics_ai_generated_mcq`

Individual MCQs produced by an AI batch. Pending review by AI Gen Manager before queuing for Division D.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `batch_id` | FK → analytics_ai_batch | — |
| `sequence_no` | smallint | Order within batch (1-based) |
| `question_text` | text | AI-generated question (not encrypted — not student PII) |
| `option_a` | text | — |
| `option_b` | text | — |
| `option_c` | text | — |
| `option_d` | text | — |
| `correct_option` | char(1) | A / B / C / D |
| `explanation` | text | AI-generated explanation |
| `ai_confidence_score` | decimal(4,3) | Model's self-reported confidence 0.0–1.0 |
| `review_status` | varchar(20) | `PENDING` · `APPROVED` · `REJECTED` · `FLAGGED_FOR_REVISION` |
| `review_note` | text | AI Gen Manager's note (required if REJECTED or FLAGGED) |
| `division_d_queue_id` | bigint | Once approved, the Division D content queue ID |
| `reviewed_at` | timestamptz | — |
| `reviewed_by_id` | FK → auth.User | — |

---

### Table: `analytics_ai_model_config`

Stores AI model configurations and prompt templates for MCQ generation.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `name` | varchar(100) | e.g., "GPT-4o SSC Standard", "Claude 3.5 NEET" |
| `model_provider` | varchar(50) | `OPENAI` · `ANTHROPIC` · `CUSTOM` |
| `model_id` | varchar(100) | e.g., `gpt-4o`, `claude-sonnet-4-6` |
| `system_prompt` | text | System-level instructions for MCQ generation |
| `user_prompt_template` | text | Template with `{domain}`, `{subject}`, `{topic}`, `{difficulty}`, `{count}` placeholders |
| `temperature` | decimal(3,2) | 0.0–1.0 |
| `max_tokens` | int | — |
| `is_active` | boolean | Only active configs shown in batch creation |
| `created_by_id` | FK → auth.User | — |
| `updated_at` | timestamptz | — |

---

### Table: `analytics_report_template`

Institution-facing MIS report templates created by Report Designer (46).

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `name` | varchar(200) | e.g., "Monthly Performance Summary — Coaching" |
| `target_audience` | varchar(30) | `INSTITUTION_ADMIN` · `INTERNAL_EXEC` · `DIVISION_H_ONLY` |
| `institution_types` | varchar[] | Which institution types this template applies to (SCHOOL/COLLEGE/COACHING/ALL) |
| `subscription_tiers` | varchar[] | Which tiers receive this report |
| `sections` | jsonb | Ordered list of section configs: `[{"type": "kpi_bar", "metrics": [...]}, {"type": "chart", ...}]` |
| `output_formats` | varchar[] | `PDF` · `CSV` · `XLSX` |
| `schedule_type` | varchar(20) | `MANUAL` · `MONTHLY` · `QUARTERLY` · `ANNUAL` |
| `schedule_day` | smallint | Day of month to deliver (1–28) |
| `is_published` | boolean | Draft vs published — only published templates used for auto-delivery |
| `published_at` | timestamptz | — |
| `published_by_id` | FK → auth.User | Analytics Manager (42) must approve publish |
| `created_by_id` | FK → auth.User | Report Designer (46) |
| `updated_at` | timestamptz | — |

---

### Table: `analytics_report_delivery`

Log of every report delivery (auto-scheduled or manual).

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `template_id` | FK → analytics_report_template | — |
| `institution_id` | bigint | Which institution received this report |
| `delivery_type` | varchar(20) | `SCHEDULED` · `MANUAL` · `TEST` |
| `period_start` | date | Report covers data from this date |
| `period_end` | date | — |
| `output_format` | varchar(10) | PDF · CSV · XLSX |
| `file_path` | varchar(500) | R2 path (private, signed URL for download) |
| `status` | varchar(20) | `PENDING` · `GENERATING` · `DELIVERED` · `FAILED` |
| `delivered_at` | timestamptz | — |
| `error_message` | text | If FAILED |
| `triggered_by_id` | FK → auth.User | Null for scheduled deliveries |

---

### Table: `analytics_pipeline_run`

Execution history of every Celery analytics aggregation job. Monitored in H-06.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `job_name` | varchar(100) | e.g., `aggregate_daily_platform_metrics`, `compute_question_analytics` |
| `run_type` | varchar(20) | `SCHEDULED` · `MANUAL` |
| `triggered_by_id` | FK → auth.User | Null for scheduled runs |
| `status` | varchar(20) | `RUNNING` · `SUCCESS` · `FAILED` · `PARTIAL_SUCCESS` · `SKIPPED` |
| `started_at` | timestamptz | — |
| `completed_at` | timestamptz | — |
| `duration_ms` | int | — |
| `rows_processed` | bigint | Total rows read across all tenant schemas |
| `rows_written` | bigint | Rows written to analytics schema |
| `tenants_processed` | smallint | Number of tenant schemas queried |
| `tenants_failed` | smallint | Tenants where query failed (partial success) |
| `error_message` | text | Full traceback if FAILED |
| `celery_task_id` | varchar(36) | — |

---

### Table: `analytics_export_request`

Self-serve data export queue for Data Analysts who need raw aggregated data.

| Field | Type | Notes |
|---|---|---|
| `id` | bigint PK | — |
| `requested_by_id` | FK → auth.User | — |
| `export_type` | varchar(50) | `QUESTION_STATS` · `INSTITUTION_ENGAGEMENT` · `STUDENT_COHORT` · `EXAM_PERFORMANCE` · `AI_BATCH_SUMMARY` |
| `filters` | jsonb | Applied filter state at time of export request |
| `output_format` | varchar(10) | CSV · XLSX |
| `status` | varchar(20) | `QUEUED` · `PROCESSING` · `READY` · `EXPIRED` · `FAILED` |
| `file_path` | varchar(500) | R2 path when READY |
| `row_count` | bigint | Rows in exported file |
| `expires_at` | timestamptz | Download link expires 48h after generation |
| `created_at` | timestamptz | — |
| `completed_at` | timestamptz | — |

---

## Celery Tasks

### 1. `aggregate_daily_platform_metrics`

**Schedule:** Daily at 01:00 IST
**Queue:** `analytics`
**Duration target:** < 15 min

Scans all 2,050 tenant schemas using Django's `connection.set_schema()` pattern. For each metric key, executes a SQL aggregate query per tenant schema, accumulates results, and writes to `analytics_daily_snapshot` for `snapshot_date = yesterday`.

**Metrics computed:**
- `active_institutions` — distinct institutions with ≥1 exam attempt that day
- `exam_attempts_total` — sum of exam attempt records
- `exam_completions_total` — completed (submitted) attempt records
- `new_students` — students whose first attempt was yesterday
- `avg_score_pct` — mean score across all attempts
- `avg_completion_rate` — completions ÷ attempts
- `notification_sent_total` — notifications dispatched
- `content_published_total` — MCQs published to live bank

Each metric computed with dimensions: overall + per exam_domain + per institution_type + per subscription_tier + per region_state.

**On failure:** Logs to `analytics_pipeline_run`. Sends in-app notification to Data Engineer (43) and Analytics Manager (42). Does not retry automatically — manual re-run required from H-06.

---

### 2. `compute_question_analytics`

**Schedule:** Daily at 02:00 IST (after #1 completes)
**Queue:** `analytics`
**Duration target:** < 45 min (2M questions × CTT computation)

For each question in the global question registry:
- Queries attempt data from all tenant schemas (only schemas where this question was used — skips schemas with no record)
- Computes: `difficulty_index`, `discrimination_index`, `omission_rate`, `distractor_stats`
- Sets `quality_flag` based on thresholds
- Updates `analytics_question_stats` (upsert on `question_id`)

**Discrimination index computation:** Point-biserial correlation between item score (0/1) and total exam score, computed from attempt data. Requires minimum 30 attempts for a valid D value (questions with fewer attempts marked `quality_flag = INSUFFICIENT_ATTEMPTS`).

**Partial success handling:** If a tenant schema query fails (e.g., schema locked), logs the failure but continues with remaining schemas. Final row reflects data from successful schemas only. `tenants_failed` count written to `analytics_pipeline_run`.

---

### 3. `compute_institution_engagement`

**Schedule:** Weekly, Sunday at 03:00 IST
**Queue:** `analytics`

For each institution:
- Reads last 90 days of activity from that institution's tenant schema
- Computes engagement score (weighted formula documented in data model)
- Sets `churn_risk` classification
- Writes to `analytics_institution_engagement`

On CRITICAL churn risk (score < 30) for Enterprise/Professional tier institutions: triggers in-app notification to Customer Success Manager (53, Division J) with link to H-03 institution detail.

---

### 4. `compute_cohort_snapshots`

**Schedule:** Monthly, 1st of month at 04:00 IST
**Queue:** `analytics`

Reads student first-appearance dates from all tenant schemas. Groups by cohort month. Computes retention rates at 1/2/3/6/12 months. Writes to `analytics_cohort_snapshot`.

Privacy: no individual student IDs stored — only aggregate cohort counts.

---

### 5. `run_ai_generation_batch`

**Schedule:** On-demand (triggered by AI Generation Manager in H-07)
**Queue:** `ai_generation`

Picks up `analytics_ai_batch` records with `status = QUEUED`. Calls configured AI API with system prompt + user prompt template filled with batch parameters. Parses response into individual `analytics_ai_generated_mcq` records. Updates batch status to `REVIEW_PENDING` on completion. Notifies AI Gen Manager (45) in-app: "Batch {batch_ref} — {N} MCQs ready for review."

**Error handling:** If AI API call fails: exponential backoff (3 attempts, 60s/120s/300s delays). After 3 failures: status = `FAILED`, Data Engineer (43) and AI Gen Manager (45) notified.

---

### 6. `generate_scheduled_reports`

**Schedule:** 1st of each month at 06:00 IST; also 1st of each quarter
**Queue:** `reports`

For each published `analytics_report_template` with `schedule_type IN (MONTHLY, QUARTERLY, ANNUAL)` and `delivery_day` matching today:
- Fetches pre-aggregated data for the reporting period
- Renders report in requested output formats
- Stores in R2 private bucket
- Creates `analytics_report_delivery` records
- Sends in-app + email notification to institution admins with signed download URL (72h expiry)

---

### 7. `process_export_request`

**Schedule:** Triggered immediately when `analytics_export_request` is created
**Queue:** `exports`

Reads pre-aggregated analytics data matching the export filters. Generates CSV/XLSX file. Stores in R2. Updates `analytics_export_request` status to `READY`. Sends in-app notification to requester: "Export ready — download within 48h."

---

## Cross-Page Workflows

### Workflow 1: Question Quality Degradation Response

```
H-04 daily view → Data Analyst identifies questions with D < 0.2 (poor discrimination)
  → Flags batch for review → Analytics Manager notified
  → Decision: commission AI replacements OR archive
  → If AI replacements: H-07 AI Gen Manager creates batch for same domain/topic
  → Batch generates → AI Manager reviews → Approved MCQs → Division D queue
  → Division D SME reviews → approved → H-04 shows improved bank quality next cycle
```

### Workflow 2: Institution Churn Risk Intervention

```
H-03 Celery task computes CRITICAL churn risk (engagement score < 30)
  → In-app alert to CSM (Division J, role 53)
  → Data Analyst (H-03) drills into institution detail drawer
  → Generates ad-hoc report via H-08 Report Studio
  → CSM + Analyst discuss intervention with Account Manager (Division J, role 54)
  → H-08 monthly report scheduled for at-risk institution (more frequent delivery)
```

### Workflow 3: AI MCQ Pipeline to Division D

```
AI Gen Manager (H-07) creates batch: domain=SSC, topic=Data Interpretation, count=50
  → Celery `run_ai_generation_batch` triggers
  → 50 MCQs generated → status = REVIEW_PENDING
  → AI Gen Manager reviews each MCQ in H-07 review drawer
  → Approved: 42/50 → status = APPROVED → Celery creates Division D content queue entries
  → Division D SME reviews AI-flagged entries (see entry has `source = AI_GENERATED` tag)
  → SME approves/edits/rejects → publishes to live bank
  → H-01 dashboard shows AI contribution to question bank (KPI tile)
```

### Workflow 4: Data Pipeline Failure Recovery

```
Celery `aggregate_daily_platform_metrics` fails at 01:30 IST
  → analytics_pipeline_run record: status = FAILED, error_message = "<traceback>"
  → In-app notification to Data Engineer (43) and Analytics Manager (42)
  → H-01 dashboard shows "⚠ Data may be stale — last successful run: yesterday 01:04"
  → Data Engineer investigates in H-06 (pipeline monitor)
  → Fixes root cause → triggers manual re-run from H-06
  → Re-run succeeds → staleness indicator clears on H-01
```

### Workflow 5: Scheduled Institution Report Delivery

```
Report Designer (46) builds template in H-08 (monthly summary for coaching centres)
  → Analytics Manager (42) approves and publishes template
  → Schedule: every 1st of month at 06:00 IST
  → Celery `generate_scheduled_reports` runs
  → H-08 delivery log shows: 98/100 coaching centres delivered, 2 failed
  → Report Designer sees failure reason → fixes data mapping → manual re-send
```

---

## Integration Points

| System | How Division H Interacts |
|---|---|
| Division D (Content) | AI-approved MCQs enter Division D's content review queue as `source = AI_GENERATED` entries |
| Division G (BGV) | H-01 shows BGV coverage KPI tile (read from `bgv_institution_compliance`); H-03 shows per-institution BGV status |
| Division J (Customer Success) | H-03 Celery task notifies CSM (53) on CRITICAL churn risk; H-08 reports are used by Account Managers |
| Division F (Exam Ops) | H-05 reads pre-aggregated exam performance data; SLA correlation uses H-05 data |
| Division B (Product) | H-01 shows feature flag adoption metrics; A/B test results are visualised in H-02 student performance |
| Division A (Exec) | H pages are linked from A-01 executive dashboard for deep-dive access; A-24 executive reports uses H-08 templates |
| Institution Portal (tenant) | H-08 generated reports delivered to institution admin dashboards via signed R2 URLs |
| R2 (Cloudflare) | All exported files and reports stored in private R2 bucket; 72h signed URL for downloads |
| Notification Hub (F-06) | H-07 batch complete / H-06 pipeline failure / H-03 churn risk → in-app notifications via Division F notification system |

---

*Pages-list complete.*
*Division H covers: Analytics Dashboard (platform MIS) → Student Performance (cohort + dropout) → Institution Analytics (engagement scoring + churn risk) → Question Intelligence (CTT metrics for 2M+ questions) → Exam & Domain Analytics (cross-domain performance) → Data Pipeline Monitor (Data Engineer workspace) → AI MCQ Generation (batch management + review) → Report Studio (institution-facing template builder).*
