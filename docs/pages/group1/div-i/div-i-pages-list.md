# Division I — Customer Support: Pages List & Architecture

> EduForge platform-level support covering 2,050 institutions and 2.4M–7.6M students.
> 6 core roles + 1 added role (90) = **7 roles total**.
> Support pipeline handles L1 → L2 → L3 escalation with hard SLA enforcement.

---

## Scale Context

| Segment | Count | Avg Monthly Tickets (Est.) |
|---|---|---|
| Schools | 1,000 | ~3,000 |
| Colleges | 800 | ~1,600 |
| Coaching Centres | 100 | ~800 |
| Institution Groups | 150 | ~300 |
| **Total institutions** | **2,050** | **~5,700/month normal** |
| **Exam-day peak** | — | **~18,000–25,000 in 48h window** |

Peak load driver: 74,000 simultaneous exam submissions → login failures, OTP timeouts, and session errors flood L1 simultaneously.

---

## Page Inventory

| Page | Route | Primary Role | Purpose |
|---|---|---|---|
| I-01 | `/support/` | Support Manager | Real-time support health dashboard |
| I-02 | `/support/tickets/` | L1/L2/L3/Support Manager | Paginated ticket worklist with SLA timers |
| I-03 | `/support/tickets/{id}/` | L1/L2/L3/Support Manager | Full ticket thread, actions, escalation |
| I-04 | `/support/institutions/{institution_id}/` | All support roles | Institution-scoped support history + contacts |
| I-05 | `/support/onboarding/` | Onboarding Specialist | Institution onboarding pipeline tracker |
| I-06 | `/support/knowledge-base/` | Training Coordinator | KB article authoring + training session scheduler |
| I-07 | `/support/reports/` | Support Manager | SLA compliance + team performance analytics |

---

## Division I Roles

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 47 | Support Manager | 3 | Team management, SLA config, escalation rules, cross-division coordination, full ticket access | Infra config, billing, data writes outside support module |
| 48 | L1 Support Executive | 3 | Login, OTP, basic navigation, student and institution admin queries | Access L2/L3 queues; trigger code-level fixes; DB writes |
| 49 | L2 Support Engineer | 3 | Bug investigation, log analysis, DB read queries via tool access, technical ticket resolution | L3 fixes (code deploy, hotfix); billing changes |
| 50 | L3 Support Engineer | 4 | Code-level fixes, DB writes under Support Manager approval, hotfixes, rollbacks | Approve content; configure AI pipeline |
| 51 | Onboarding Specialist | 3 | New institution onboarding pipeline, portal setup guidance, admin training coordination | Access student ticket data; L2/L3 queues |
| 52 | Training Coordinator | 2 | Create training docs, schedule and conduct training sessions for institution admins | Access ticket queue; no ticket actions |
| 90 | Support Quality Lead | 3 | Random-sample ticket quality audits, CSAT trend monitoring, L1 agent coaching, KB gap identification, weekly quality report to Support Manager | Cannot reassign or escalate tickets; no direct ticket resolution |

---

## Role-to-Page Access Matrix

| Page | 47 Manager | 48 L1 | 49 L2 | 50 L3 | 51 Onboarding | 52 Training | 90 Quality |
|---|---|---|---|---|---|---|---|
| I-01 Dashboard | Full | Own-queue KPIs only | Own-queue KPIs only | Own-queue KPIs only | Onboarding panel only | No access | Quality panel + CSAT |
| I-02 Ticket Queue | All queues | L1 queue | L2 queue | L3 queue | Onboarding category | No access | Read all (no actions) |
| I-03 Ticket Detail | Full actions | L1 tickets | L2 tickets | L3 tickets | Onboarding tickets | No access | Read + quality annotation |
| I-04 Institution Profile | Full | Read | Read | Read | Full | Read | Read |
| I-05 Onboarding Tracker | Full | No access | No access | No access | Full | Read | No access |
| I-06 Knowledge Base | Full + Approve | Read | Read | Read | Read | Full (Create/Edit) | Read + flag gap |
| I-07 SLA Reports | Full | Own stats | Own stats | Own stats | Onboarding stats | No access | Quality metrics only |

---

## Data Model

### `support_ticket`

| Column | Type | Notes |
|---|---|---|
| id | bigserial PK | — |
| ticket_number | varchar(25) UNIQUE | Format: `SUP-YYYYMMDD-NNNNNN`; sequence resets daily |
| institution_id | int FK → institution | Nullable for platform-level tickets |
| subject | varchar(500) NOT NULL | — |
| category | varchar(30) NOT NULL | See enum below |
| priority | varchar(20) NOT NULL | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`; default `MEDIUM` |
| status | varchar(30) NOT NULL | See state machine below; default `OPEN` |
| tier | varchar(5) NOT NULL | `L1`, `L2`, `L3`; default `L1` |
| source | varchar(30) NOT NULL | `PORTAL`, `EMAIL`, `PHONE`, `INTERNAL`, `DIVISION_H_ALERT`, `DIVISION_F_ESCALATION`; default `PORTAL` |
| assigned_to_id | int FK → user | Nullable; null = unassigned |
| created_by_id | int FK → user | Platform staff who created internal tickets; null for self-service |
| requester_name | varchar(200) | Name of institution admin or student who raised the ticket |
| requester_email | varchar(254) | — |
| requester_role | varchar(50) | `INSTITUTION_ADMIN`, `INSTITUTION_STAFF`, `STUDENT`, `PLATFORM_STAFF` |
| exam_day_incident | boolean DEFAULT false | True = flagged as exam-day critical; bypasses normal queue position |
| linked_exam_id | int FK → exam | Nullable; set for EXAM_ACCESS and EXAM_DAY_INCIDENT categories |
| sla_breach_at | timestamptz NOT NULL | Computed at creation: `created_at + resolution_hours` from `support_sla_config` |
| first_response_at | timestamptz | Set on first non-system reply from an agent |
| sla_pause_started_at | timestamptz | Set when status changes to `PENDING_CUSTOMER` |
| sla_pause_duration_seconds | int DEFAULT 0 | Cumulative seconds of PENDING_CUSTOMER time; subtracted from effective SLA |
| resolved_at | timestamptz | Set when status changes to `RESOLVED` |
| closed_at | timestamptz | Set when status changes to `CLOSED` |
| csat_score | smallint | 1–5; null until customer submits CSAT |
| csat_comment | text | Optional customer text on CSAT submission |
| csat_submitted_at | timestamptz | — |
| quality_audit_score | smallint | 1–5; set by Support Quality Lead (#90) during audit; null = not yet audited |
| quality_audit_note | text | Auditor note on ticket quality |
| quality_audited_at | timestamptz | — |
| tags | varchar[] DEFAULT '{}' | Free-form tags for filtering and KB gap detection |
| created_at | timestamptz DEFAULT now() | — |
| updated_at | timestamptz DEFAULT now() | — |

**Category enum (11 values):**
`LOGIN_ISSUE`, `OTP_FAILURE`, `EXAM_ACCESS`, `RESULT_QUERY`, `BILLING_QUERY`, `TECHNICAL_BUG`, `FEATURE_REQUEST`, `ONBOARDING_HELP`, `DATA_CORRECTION`, `EXAM_DAY_INCIDENT`, `OTHER`

**Routing rules at creation:**
- `EXAM_DAY_INCIDENT` → auto-tier = L2, auto-priority = CRITICAL
- `DATA_CORRECTION` → auto-tier = L2
- `TECHNICAL_BUG` → auto-tier = L1 (escalates to L2 if not resolved in SLA window)
- All others → tier = L1

---

### `support_ticket_message`

| Column | Type | Notes |
|---|---|---|
| id | bigserial PK | — |
| ticket_id | bigint FK → support_ticket | — |
| author_id | int FK → user | Nullable for system messages |
| message_type | varchar(20) NOT NULL | `REPLY`, `INTERNAL_NOTE`, `STATUS_CHANGE`, `ESCALATION`, `QUALITY_ANNOTATION`, `SYSTEM` |
| body | text NOT NULL | Markdown for REPLY; plain text for SYSTEM |
| attachments | jsonb DEFAULT '[]' | `[{filename, r2_key, size_bytes, content_type, uploaded_at}]` |
| is_visible_to_requester | boolean DEFAULT true | False for `INTERNAL_NOTE`, `QUALITY_ANNOTATION`, `ESCALATION` type |
| created_at | timestamptz DEFAULT now() | — |

---

### `support_ticket_escalation`

| Column | Type | Notes |
|---|---|---|
| id | bigserial PK | — |
| ticket_id | bigint FK → support_ticket | — |
| from_tier | varchar(5) | L1 or L2; null if escalated from Support Manager directly |
| to_tier | varchar(5) NOT NULL | L2 or L3 |
| escalated_by_id | int FK → user | — |
| reason | text | Required; displayed in ticket thread |
| escalated_at | timestamptz DEFAULT now() | — |

---

### `support_sla_config`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| tier | varchar(5) NOT NULL | L1, L2, L3 |
| priority | varchar(20) NOT NULL | CRITICAL, HIGH, MEDIUM, LOW |
| first_response_minutes | int NOT NULL | Minutes until first response SLA |
| resolution_minutes | int NOT NULL | Minutes until resolution SLA |
| is_active | boolean DEFAULT true | — |
| UNIQUE(tier, priority) | — | — |

**Default SLA values:**

| Tier | Priority | First Response | Resolution |
|---|---|---|---|
| L1 | CRITICAL | 30 min | 120 min |
| L1 | HIGH | 60 min | 240 min |
| L1 | MEDIUM | 120 min | 480 min |
| L1 | LOW | 240 min | 1,440 min |
| L2 | CRITICAL | 60 min | 240 min |
| L2 | HIGH | 120 min | 480 min |
| L2 | MEDIUM | 240 min | 960 min |
| L2 | LOW | 480 min | 2,880 min |
| L3 | CRITICAL | 120 min | 480 min |
| L3 | HIGH | 240 min | 960 min |
| L3 | MEDIUM | 480 min | 1,440 min |
| L3 | LOW | 1,440 min | 4,320 min |

> Exam-day override: Any ticket with `exam_day_incident=true` and priority=CRITICAL uses L1 first-response = **15 minutes**, regardless of configured value.

---

### `onboarding_instance`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| institution_id | int FK → institution UNIQUE | One onboarding record per institution |
| assigned_specialist_id | int FK → user | Onboarding Specialist (#51) |
| stage | varchar(30) NOT NULL DEFAULT 'INITIATED' | See stage machine below |
| started_at | timestamptz DEFAULT now() | — |
| target_go_live_at | date | Set at initiation; agreed go-live date |
| actual_go_live_at | date | Set when stage transitions to LIVE |
| completed_at | timestamptz | Set when stage = COMPLETED |
| stalled_since | timestamptz | Set by Celery when no activity for 7 days |
| notes | text | Specialist notes |
| updated_at | timestamptz DEFAULT now() | — |

**Stage machine:** `INITIATED → SETUP_CALL_SCHEDULED → PORTAL_CONFIGURED → ADMIN_TRAINED → FIRST_EXAM_CREATED → LIVE → COMPLETED`
Parallel: any stage → `STALLED` (Celery auto-sets after 7 days inactivity); Support Manager can re-activate.

---

### `onboarding_checklist_template`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| stage | varchar(30) NOT NULL | Which stage this item belongs to |
| title | varchar(200) NOT NULL | — |
| description | text | Tooltip/help text for specialist |
| is_mandatory | boolean DEFAULT true | Mandatory items block stage progression |
| sort_order | int NOT NULL | Display order within stage |

---

### `onboarding_checklist_progress`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| instance_id | int FK → onboarding_instance | — |
| template_item_id | int FK → onboarding_checklist_template | — |
| is_completed | boolean DEFAULT false | — |
| completed_by_id | int FK → user | — |
| completed_at | timestamptz | — |
| notes | text | Optional per-item note |
| UNIQUE(instance_id, template_item_id) | — | — |

---

### `onboarding_training_session`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| instance_id | int FK → onboarding_instance | — |
| title | varchar(300) NOT NULL | — |
| session_type | varchar(30) NOT NULL | `PORTAL_WALKTHROUGH`, `EXAM_CREATION`, `STUDENT_MGMT`, `RESULTS_WORKFLOW`, `REFRESHER` |
| scheduled_at | timestamptz NOT NULL | — |
| duration_minutes | int DEFAULT 60 | — |
| meeting_link | varchar(500) | Google Meet / Zoom link |
| conducted_by_id | int FK → user | Onboarding Specialist or Training Coordinator |
| status | varchar(20) DEFAULT 'SCHEDULED' | `SCHEDULED`, `COMPLETED`, `CANCELLED`, `NO_SHOW` |
| attendee_names | text[] DEFAULT '{}' | Names of institution staff who attended |
| recording_url | varchar(500) | Nullable |
| notes | text | Post-session notes |
| created_at | timestamptz DEFAULT now() | — |

---

### `kb_article`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| title | varchar(500) NOT NULL | — |
| slug | varchar(200) UNIQUE NOT NULL | URL-safe; auto-generated from title |
| category | varchar(50) NOT NULL | `LOGIN`, `EXAM_FLOW`, `BILLING`, `ONBOARDING`, `TECHNICAL`, `ADMIN_PORTAL`, `RESULTS`, `GENERAL` |
| body | text NOT NULL | Markdown content |
| status | varchar(20) DEFAULT 'DRAFT' | `DRAFT`, `PENDING_REVIEW`, `PUBLISHED`, `ARCHIVED` |
| author_id | int FK → user | Training Coordinator or Support Manager |
| reviewed_by_id | int FK → user | Support Manager who approved |
| published_at | timestamptz | — |
| archived_at | timestamptz | — |
| view_count | int DEFAULT 0 | Incremented on each view |
| helpful_votes | int DEFAULT 0 | — |
| not_helpful_votes | int DEFAULT 0 | — |
| linked_ticket_categories | varchar[] DEFAULT '{}' | Which `support_ticket.category` values this article helps resolve |
| created_at | timestamptz DEFAULT now() | — |
| updated_at | timestamptz DEFAULT now() | — |

**KB article state machine:** `DRAFT → PENDING_REVIEW → PUBLISHED or DRAFT` (if rejected) → `ARCHIVED`
Training Coordinator (#52) authors; Support Manager (#47) approves. Support Quality Lead (#90) can flag articles for review.

---

### `kb_article_gap_flag`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| flagged_by_id | int FK → user | Support Quality Lead (#90) or any agent |
| ticket_category | varchar(30) | Category where the KB gap was identified |
| description | text NOT NULL | Description of the missing content |
| status | varchar(20) DEFAULT 'OPEN' | `OPEN`, `ASSIGNED`, `RESOLVED` |
| assigned_to_id | int FK → user | Training Coordinator assigned to fill gap |
| created_at | timestamptz DEFAULT now() | — |

---

### `support_quality_audit`

| Column | Type | Notes |
|---|---|---|
| id | serial PK | — |
| audited_by_id | int FK → user | Support Quality Lead (#90) |
| ticket_id | bigint FK → support_ticket | The ticket being audited |
| quality_score | smallint NOT NULL CHECK (1–5) | 1=Poor, 5=Excellent |
| criteria_scores | jsonb | `{tone, accuracy, speed, resolution_quality}` each 1–5 |
| notes | text | Detailed feedback |
| shared_with_agent | boolean DEFAULT false | Whether audit result was shared with ticket agent |
| audited_at | timestamptz DEFAULT now() | — |

---

## Ticket Status State Machine

```
OPEN
  │
  ├─ Agent picks up → IN_PROGRESS
  │     │
  │     ├─ Needs customer input → PENDING_CUSTOMER
  │     │     │
  │     │     └─ Customer replies → IN_PROGRESS (SLA timer resumes)
  │     │
  │     ├─ Needs L2/L3 → ESCALATED (tier updated)
  │     │
  │     └─ Issue fixed → RESOLVED
  │           │
  │           └─ [Auto-close after 7 days no activity] → CLOSED
  │
  └─ (Unassigned >30min, Support Manager assigns) → IN_PROGRESS
```

CSAT survey sent to requester when status changes to `RESOLVED`.
Support Manager can re-open CLOSED tickets (creates INTERNAL_NOTE with reason).

---

## Celery Tasks

| # | Task Name | Schedule | Queue | Action |
|---|---|---|---|---|
| 1 | `check_sla_breaches` | Every 5 min | `support` | Scans open tickets where `sla_breach_at < now()` AND status NOT IN (`RESOLVED`, `CLOSED`, `PENDING_CUSTOMER`); sends breach notification via F-06 to assigned agent + Support Manager |
| 2 | `send_sla_warnings` | Every 15 min | `support` | Finds tickets where `sla_breach_at BETWEEN now() AND now() + interval '60 min'` and status = `IN_PROGRESS`; sends warning notification to assigned agent only |
| 3 | `auto_close_resolved_tickets` | Daily at 00:00 IST | `support` | Closes tickets in `RESOLVED` status with `resolved_at < now() - interval '7 days'` and no new messages; sends CSAT reminder if not yet submitted |
| 4 | `flag_stalled_onboarding` | Daily at 08:00 IST | `support` | Marks onboarding instances as `STALLED` if `updated_at < now() - interval '7 days'` and stage NOT IN (`LIVE`, `COMPLETED`); notifies assigned Onboarding Specialist and Support Manager via F-06 |
| 5 | `generate_support_weekly_report` | Every Monday 09:00 IST | `support` | Computes SLA compliance %, CSAT scores, ticket volume by category, agent performance metrics; stores in `support_weekly_report` table; notifies Support Manager |

---

## Caching Strategy (Memcached)

| Page | Part | TTL | Bypass |
|---|---|---|---|
| I-01 Dashboard | KPI strip | 2 min | Support Manager: `?nocache=true` |
| I-01 Dashboard | Volume chart | 5 min | — |
| I-02 Ticket Queue | Table rows | No cache | Live SLA timers require fresh data |
| I-03 Ticket Detail | Thread messages | No cache | Must reflect real-time replies |
| I-04 Institution Profile | Ticket history table | 5 min | — |
| I-05 Onboarding Tracker | Stage table | 5 min | — |
| I-06 KB Manager | Article list | 10 min | — |
| I-06 KB Manager | Published articles | 60 min | — |
| I-07 SLA Reports | Charts | 15 min | `?nocache=true` |

---

## Integration Points

| External System | Direction | What Flows |
|---|---|---|
| Division F — Exam Day Ops | Inbound | Incident Manager (#38) can create EXAM_DAY_INCIDENT tickets directly in L2 queue via internal API; F-06 routes all ticket notifications (breach, escalation, resolution) |
| Division H — Analytics | Inbound | Anomaly alerts from H-01 can auto-create `source=DIVISION_H_ALERT` tickets assigned to Support Manager for triage |
| Division G — BGV | Inbound | BGV_QUERY tickets auto-route to BGV Manager (#39) via internal handoff note; Support team creates ticket, BGV team resolves |
| Division K — Sales | Inbound | New institution sign-off from Sales creates `onboarding_instance` record; triggers Onboarding Specialist assignment |
| Division B — Product | Outbound | FEATURE_REQUEST tickets with 3+ duplicates generate a feature request item in Product Manager (#5) dashboard |
| AWS SES / WhatsApp | Bidirectional | Email: ticket creation and reply notifications; WhatsApp: CSAT survey delivery after resolution |

---

## Cross-Page Workflows

### Workflow 1 — Exam Day Surge Handling
1. Live exam begins (Division F confirms exam started)
2. I-01 shows yellow exam-day banner: "Exam live: {exam_name} — {N} CRITICAL tickets"
3. All L1 agents see exam-day ticket filter auto-applied in I-02
4. EXAM_DAY_INCIDENT tickets sorted to top of queue; SLA = 15 min first response
5. L1 agents cannot close EXAM_DAY_INCIDENT tickets — must route to L2 minimum
6. After exam ends, banner clears; normal queue resumes

### Workflow 2 — L1 → L2 → L3 Escalation
1. L1 agent in I-03 clicks [Escalate to L2]; required: select reason from dropdown (8 reasons)
2. `support_ticket_escalation` record created; ticket tier updated to L2; old SLA invalidated; new SLA computed from L2 config
3. L2 queue in I-02 shows escalated ticket with red "Escalated from L1" badge
4. L2 can further escalate to L3 (same process); Support Manager can skip tiers in emergency
5. L3 resolves; resolution note visible to all prior tier agents for learning

### Workflow 3 — New Institution Onboarding
1. Sales closes deal → creates `onboarding_instance` (Stage: INITIATED)
2. Onboarding Specialist sees new entry in I-05; picks up and schedules first call
3. I-05 checklist tracks each mandatory item per stage before stage can progress
4. If stalled >7 days: Celery task flags STALLED; Support Manager gets notification
5. On stage = LIVE: `actual_go_live_at` stamped; Training Coordinator schedules follow-up session via I-06

### Workflow 4 — CSAT-Driven Quality Loop
1. Ticket resolved → auto CSAT sent to requester
2. Score < 3 → Support Quality Lead (#90) sees ticket in quality audit queue in I-07
3. Quality Lead audits ticket in I-03 (via quality annotation message type); logs `support_quality_audit` record
4. If agent performance issue: quality audit report shared with Support Manager via I-07
5. Recurring patterns → KB gap flagged via I-06 → Training Coordinator creates/updates article

### Workflow 5 — KB Article Lifecycle
1. Training Coordinator (#52) creates DRAFT article in I-06
2. Submits for review → status = PENDING_REVIEW
3. Support Manager reviews; approves (→ PUBLISHED) or rejects with feedback (→ DRAFT with note)
4. Published articles auto-linked to matching ticket categories
5. L1 agents in I-03 see suggested KB articles when viewing tickets of matching category
6. Support Quality Lead can flag any article for review if identified as inaccurate/outdated

---

## DPDPA 2023 Considerations

- Ticket records contain requester PII (name, email) — classified as **personal data** under DPDPA
- Access strictly role-scoped: agents see only tickets in their queue; Support Manager sees all
- All PII access logged via `support_ticket_message` (system type) for audit trail
- Bulk PII export (ticket export with requester details) requires Data Privacy Officer (#76) approval
- Student tickets: requester email masked in exported reports (`s***@domain.com`)
- **Retention**: `support_ticket` + `support_ticket_message` → 7 years (legal compliance); `onboarding_instance` → 5 years; `kb_article` → permanent (published); `support_quality_audit` → 2 years

---

## Data Retention Policy

| Table | Retention | Method |
|---|---|---|
| `support_ticket` | 7 years | Soft-delete then archive to cold storage |
| `support_ticket_message` | 7 years | Cascades with parent ticket |
| `support_ticket_escalation` | 7 years | Cascades with parent ticket |
| `support_sla_config` | Permanent | Config table; never deleted |
| `onboarding_instance` | 5 years post-completion | Archived after `completed_at + 5 years` |
| `onboarding_checklist_progress` | 5 years | Cascades with instance |
| `onboarding_training_session` | 5 years | Cascades with instance |
| `kb_article` | Permanent (published); 1 year (DRAFT/ARCHIVED) | — |
| `kb_article_gap_flag` | 1 year post-resolution | — |
| `support_quality_audit` | 2 years | — |
| `support_weekly_report` | 3 years | — |
