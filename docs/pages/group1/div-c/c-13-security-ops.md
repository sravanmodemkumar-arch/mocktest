# C-13 — Security Operations Dashboard

> **Route:** `/engineering/security/`
> **Division:** C — Engineering
> **Primary Role:** Platform Admin (Role 10) · Security Engineer (Role 16)
> **Read Access:** DevOps/SRE (Role 14)
> **File:** `c-13-security-ops.md`
> **Priority:** P0 — Required before first institution goes live
> **Status:** ✅ Spec done

---

## 1. Page Name & Route

**Page Name:** Security Operations Dashboard
**Route:** `/engineering/security/`
**Part-load routes:**
- `/engineering/security/?part=kpi` — security health KPI
- `/engineering/security/?part=waf` — AWS WAF rules panel
- `/engineering/security/?part=auth-heatmap` — failed auth heatmap
- `/engineering/security/?part=lockout-log` — account lockout event log
- `/engineering/security/?part=jwt-anomaly` — JWT anomaly detection
- `/engineering/security/?part=cve` — CVE tracker
- `/engineering/security/?part=certIn` — CERT-In incident log
- `/engineering/security/?part=dpdpa` — DPDPA breach tracker
- `/engineering/security/?part=vapt` — VAPT results
- `/engineering/security/?part=dependency-scan` — dependency vulnerability scanner
- `/engineering/security/?part=threats` — active threat alerts

---

## 2. Purpose (Business Objective)

The Security Operations Dashboard is the Security Engineer's command centre for protecting all 2,050 institution portals and the platform's internal engineering surface. With 7.6M potential student accounts and all their exam data, PII, and payment history, the platform is a high-value target.

The page provides both real-time threat detection (failed auth bursts, suspicious JWT patterns, WAF block events) and compliance management (CERT-In 6-hour incident reporting countdown, DPDPA 72-hour breach notification tracking). Any data breach that is not reported to CERT-In within 6 hours is a regulatory violation with criminal liability for the company.

**Business goals:**
- Detect credential-stuffing, brute-force, and session hijacking attempts in near-real-time
- Control AWS WAF rules (block/rate-limit/geo-restrict) without AWS console access
- Track CVEs in platform dependencies with severity triage
- Manage CERT-In and DPDPA incident reporting with automated countdown timers
- Maintain VAPT findings tracker with remediation status

---

## 3. User Roles

| Role | Access Level | Permissions |
|---|---|---|
| Platform Admin (10) | Level 5 | Full view + all write actions |
| Security Engineer (16) | Level 4 | Full view + all write actions |
| DevOps / SRE (14) | Level 4 — Read | View WAF · threat alerts · cannot modify |

---

## 4. Section-Wise Detailed Breakdown

---

### Section 1 — Page Header & Security Posture

**Purpose:** Instant overall security health verdict.

**Security Posture Score:**
- Calculated composite score (0–100): based on unresolved critical CVEs · active threats · WAF bypasses · overdue VAPT findings
- Display: large circular gauge, colour: green (80–100) · amber (60–79) · red (< 60)
- Trend: "↑ improved from 74 last week"

**Active Alerts Banner:**
- Red pulsing if any: P0 active threat · CERT-In countdown active · Critical CVE with no remediation plan
- Example: "🚨 CERT-In breach countdown active: 4h 12m remaining"

**Header elements:**
- H1 "Security Operations Dashboard"
- Security Posture Score gauge
- Active alerts count: "3 active alerts"
- "Create Security Incident" button → pre-fills C-18
- Last full security scan: "OWASP ZAP scan: 3 days ago"

---

### Section 2 — KPI Strip

**KPI Cards:**

| Card | Metric | Alert |
|---|---|---|
| Failed Logins (1h) | Count of failed authentication attempts | > 500 amber · > 2,000 red |
| Locked Accounts (24h) | Count of auto-locked accounts | > 10 amber |
| WAF Blocks (1h) | Count of requests blocked by WAF | spike > 200% baseline = amber |
| Critical CVEs | Unresolved CVSS > 9.0 CVEs | > 0 = red |
| CERT-In Incidents | Open incidents (not yet reported) | > 0 = red (immediate action) |
| DPDPA Notifications | Open breach notifications pending | > 0 = red |

---

### Section 3 — AWS WAF Rules Panel

**Purpose:** View, add, modify, and reorder AWS WAF rules protecting all platform endpoints.

**WAF Rules Table:**

| Priority | Rule Name | Type | Action | Scope | Hit Rate (24h) | Last Modified | Status |
|---|---|---|---|---|---|---|---|
| 1 | Block known bad IPs | IP Set | Block | All | 842 blocks | 2 days ago | ✅ Active |
| 2 | Rate limit auth endpoints | Rate-based | Count → Block after 100/5min | /api/auth/* | 124 triggers | 1 week ago | ✅ Active |
| 3 | Rate limit exam submit | Rate-based | Block after 200/min | /api/exams/*/submit/ | 12 triggers | 3 days ago | ✅ Active |
| 4 | Geo-restrict admin routes | Geo match | Block if not IN/SG/US | /engineering/* | 34 blocks | 1 month ago | ✅ Active |
| 5 | AWS Managed (CommonRuleSet) | Managed | Block | All | 1,240 blocks | Auto | ✅ Active |
| 6 | AWS Managed (SQLi) | Managed | Block | All | 84 blocks | Auto | ✅ Active |
| 7 | Block TOR exit nodes | IP Set | Block | All | 192 blocks | Auto | ✅ Active |

**Add Rule (Security Engineer / Admin):**
- Rule type: IP Set match · Rate-based · Geo match · String match · SQL injection · XSS · Custom regex
- Action: Block · Count · CAPTCHA challenge
- Scope: path pattern (e.g., `/api/exams/*`) · all requests
- Priority: number (lower = evaluated first)

**Edit/Delete Rule:**
- Edit: inline form; changes take effect within 1 min (CloudFront distribution update)
- Delete: confirmation modal; "Are you sure? Deleting a blocking rule may expose endpoints."
- Reorder: drag-and-drop priority reordering (or edit priority number)

**IP Block List:**
- Dedicated sub-panel: manually blocked IPs + block reason + blocked by + expires at
- "Add IP to block list" → CIDR notation input + reason + expiry (1h / 6h / 24h / 7d / permanent)
- "Emergency IP block" → one-click block from failed-auth heatmap (feeds directly into WAF IP set)

**WAF Metrics Charts:**
- Requests blocked per hour (last 24h) — by rule name (stacked bars)
- Geographic distribution of blocked IPs

**Data Flow:**
- WAF rules from AWS WAFV2 API (GetWebACL + ListWebACLs)
- Hit rate from CloudWatch WAF metrics
- Cached Redis 5 min; full refresh on page load
- Rule changes applied via WAFV2 UpdateWebACL API

---

### Section 4 — Failed Auth Heatmap

**Purpose:** Visual detection of credential-stuffing, brute-force, and distributed attack patterns.

**Heatmap View:**
- X axis: time (last 24h in 15-min buckets)
- Y axis: source IP / country / tenant portal
- Cell colour: green (normal) → amber → red (high failure rate)

**View toggles:**
- By IP address: shows which IPs are generating most failures
- By country: geographic distribution (useful for detecting offshore attack waves)
- By tenant portal: which portals are being targeted (useful for targeted attacks)
- By time of day: when failures cluster (typical: overnight for automated attacks)

**Top offenders table:**

| IP Address | Country | Failed Attempts (1h) | Targeted Accounts | Unique IPs in subnet | Action |
|---|---|---|---|---|---|
| 45.142.212.100 | Russia | 842 | 124 | 48 (coordinated) | Block IP · Block /24 subnet |
| 104.21.18.42 | USA | 124 | 12 | 1 | Block IP · Monitor |

**Actions per row:**
- "Block IP" → immediately adds to WAF IP block set (30-day expiry default)
- "Block /24 subnet" → blocks the /24 CIDR (wider block) — 2FA required (higher blast radius)
- "Investigate" → jumps to auth-service CloudWatch logs filtered to this IP

**Pattern detection:**
- Distributed attack detection: if 50+ IPs from same /24 subnet with synchronized attempts → amber banner "Coordinated attack detected from subnet {x.x.x.0/24}"
- Credential stuffing pattern: many different accounts, low per-account failure rate from same IP → flag raised

**Data Flow:**
- Source: auth-service Lambda CloudWatch logs (`failed_login` events)
- Aggregated by Celery job every 15 min into `platform_failed_auth_stats` Redis sorted set
- Real-time feed: last 100 failed login events (15s poll)

---

### Section 5 — Account Lockout Event Log

**Purpose:** Log of all student and staff account lockouts with investigation links.

**Columns:**

| Column | Description |
|---|---|
| Timestamp | When account was locked |
| Account Type | Student · Staff |
| Account Email | Masked: `jo**@gmail.com` |
| Tenant | Institution portal (for student accounts) |
| Lock Reason | Too many failed logins · Admin manual lock · Suspicious pattern |
| Failed Attempts | Count of failures that triggered lock |
| Source IPs | List of IPs that generated failures |
| Lock Duration | Until unlocked by admin or auto-expires (30 min default) |
| Status | Locked · Auto-unlocked · Admin unlocked |

**Filters:** Account type · Date range · Lock reason · Still locked (toggle)

**Quick unlock (Security/Admin):**
- Per-row "Unlock" action → immediate unlock without 2FA (speed for legitimate user support)
- Unlock logged with actor + timestamp

**Mass unlock:**
- "Unlock all accounts locked in last 1h" → for mass false-positive lockout events (e.g., SES IP changed causing all password-reset emails to bounce → users retry → lockout)
- 2FA required

---

### Section 6 — JWT Anomaly Detection

**Purpose:** Detect suspicious JWT token usage patterns that may indicate session hijacking or token theft.

**Anomaly Types Detected:**

| Anomaly | Description | Risk Level |
|---|---|---|
| Token reuse from multiple IPs | Same JWT used from 2+ geographically distinct IPs within 5 min | Critical |
| Token used after logout | JWT used after explicit logout event (token should be in deny-list) | High |
| Algorithm confusion | JWT decoded with algorithm other than expected HS256/RS256 | Critical |
| Future iat claim | JWT with `issued_at` in the future (replay or forged token) | Critical |
| Expired token accepted | JWT with exp in past being accepted (server-side validation bug) | Critical |
| Staff JWT from student endpoint | Staff JWT used on student-facing endpoints | High |

**Anomaly Events Table:**

| Timestamp | Anomaly Type | User | JWT ID (jti) | IP(s) Involved | Action Taken |
|---|---|---|---|---|---|
| 5 min ago | Token reuse from multiple IPs | `student_48291` | jti:abc123 | 45.1.2.3 (IN) + 192.20.1.1 (RU) | Token revoked · Account locked |
| 2h ago | Token used after logout | `staff_priya@...` | jti:def456 | 10.0.0.1 | Token revoked |

**Automatic responses (configured):**
- Token reuse from different country: automatic token revocation + account lock
- Algorithm confusion: automatic token revocation + security incident created in C-18
- Expired token accepted: automatic alert to Backend team (indicates server-side bug) + C-18 incident

**Manual actions per event:**
- "Revoke token" → adds `jti` to Redis deny-list (`token:denied:{jti}`)
- "Lock account" → locks the associated account
- "View full JWT payload" → decoded (non-sensitive fields only; signature not exposed)
- "Create security incident" → pre-fills C-18

**Data Flow:**
- JWT validation middleware logs anomalies to CloudWatch
- Celery job aggregates from CloudWatch every 5 min into `platform_jwt_anomalies` table
- Real-time: 30s HTMX poll

---

### Section 7 — CVE Tracker

**Purpose:** Track security vulnerabilities in all platform dependencies.

**Data Sources:**
- Python: `pip-audit` (run in CI/CD C-09 on every commit) + Snyk for continuous monitoring
- JavaScript: `npm audit` (CI/CD)
- System packages: Amazon Inspector (EC2/Lambda)

**CVE Summary Table:**

| Severity | Count | Change from last week |
|---|---|---|
| Critical (CVSS 9.0–10.0) | 2 | +1 (new) |
| High (CVSS 7.0–8.9) | 8 | -1 (fixed) |
| Medium (CVSS 4.0–6.9) | 24 | +3 |
| Low (CVSS 0.1–3.9) | 42 | +2 |

**CVE Details Table:**

| CVE ID | Severity | Package | Version | CVSS | Affected Service | Status | Remediation |
|---|---|---|---|---|---|---|---|
| CVE-2025-12345 | 🔴 Critical | `cryptography` | 41.0.3 | 9.8 | auth-service | ⏳ In progress | Upgrade to 42.0.0 |
| CVE-2025-67890 | 🔴 Critical | `pillow` | 10.0.0 | 9.1 | content-service | ✅ Fixed | Upgraded to 10.3.0 |
| CVE-2024-98765 | 🟠 High | `django` | 4.2.8 | 7.5 | All services | ⏳ In progress | Upgrade to 4.2.15 |

**Status workflow:**
- New → Triaged → In Progress → Fixed · Accepted Risk (with written justification)

**Actions per CVE:**
- "Mark as triaged" → assign to engineer + set target fix date
- "Accept risk" → Security Engineer only · 2FA · written justification (min 100 chars) · review date set
- "View in pip-audit report" → CI/CD run that first detected this CVE
- "Create fix PR" → auto-opens GitHub issue in affected repo (links to CVE ID)

**Accepted risk policy:**
- Accepted CVEs auto-expire after 30 days — must be re-accepted (prevents permanent ignoring)
- Critical CVEs cannot be accepted at risk without Platform Admin co-approval

**Dependency scanner (on-demand):**
- "Run full dependency scan" button → triggers Celery job: runs pip-audit + npm audit + Snyk API scan across all services
- Estimated 10–15 min; results update CVE table

---

### Section 8 — CERT-In Incident Log

**Purpose:** Track all security incidents that require CERT-In (Indian Computer Emergency Response Team) notification within 6 hours.

**CERT-In Reportable Events (as per CERT-In guidelines 2022):**
- Data breach (any PII of Indian citizens)
- Ransomware attacks
- DDoS attacks
- Malware spread
- Unauthorised access to critical information infrastructure
- Compromise of identity management systems

**Active Incidents Countdown:**
- For each open incident: large countdown timer "Report to CERT-In in: 4h 12m 05s"
- Background turns red when < 1 hour remaining
- Overdue: pulsing red "OVERDUE: CERT-In notification required immediately"

**Incident Table:**

| Incident | Detected At | Severity | Type | CERT-In Status | Time Remaining | Actions |
|---|---|---|---|---|---|---|
| Unauthorised access attempt — tenant_042 | 2h ago | P1 | Auth breach attempt | ⏳ Not yet submitted | 4h 12m | Submit report · View details |
| Credential stuffing attack — 842 accounts | 6h ago | P2 | Auth attack | ✅ Submitted 4h ago | — | View report |

**CERT-In Report Submission:**
- "Submit report" → opens CERT-In report form pre-filled with incident details:
  - Incident type (from CERT-In category list)
  - Date/time of discovery
  - Affected systems
  - Suspected attack vector
  - Data potentially compromised (type + estimated count)
  - Immediate actions taken
- "Download report as PDF" → formatted for CERT-In submission
- "Mark as submitted" → records submission timestamp + acknowledgement number from CERT-In portal

**Report templates:**
- Pre-built templates for each incident type
- Auto-populates: affected systems (from C-18 incident linked data) · timeline of events

---

### Section 9 — DPDPA Breach Tracker

**Purpose:** Track personal data breaches requiring notification to the Data Protection Board under DPDPA 2023 within 72 hours.

**DPDPA Breach Criteria (as per DPDPA 2023):**
- Unauthorised access to or disclosure of personal data
- Accidental destruction or loss of personal data
- Alteration of personal data without authorisation

**Active Breach Countdown:**
- Large countdown timer: "Notify Data Protection Board in: 68h 24m"
- Background amber → red when < 12h remaining

**Breach Record Table:**

| Breach | Detected | Data Type | Affected Users | DPB Status | Deadline | Action |
|---|---|---|---|---|---|---|
| Exam result data exposed via API bug | 6h ago | Exam results (non-PII) | ~840 students | ⏳ Notification draft | 66h remaining | Submit notification |

**DPB Notification Form:**
- Nature of the breach
- Data principal categories affected (students · teachers · parents)
- Approximate number affected
- Likely consequences
- Measures taken/proposed
- Contact of Data Protection Officer

**Data Localisation verification:**
- Confirms primary data storage: ap-south-1 (Mumbai) ✅
- Confirms no PII replication outside India: ✅
- If cross-border data transfer detected: immediate red flag

---

### Section 10 — VAPT Results

**Purpose:** Track Vulnerability Assessment and Penetration Testing findings with remediation status.

**VAPT Engagement History:**

| Engagement | Vendor | Type | Date | Total Findings | Open | Fixed | Status |
|---|---|---|---|---|---|---|---|
| Annual VAPT 2026 | SecureIndia Pvt Ltd | External VAPT | Jan 2026 | 42 | 8 | 34 | In remediation |
| Bug Bounty Program | HackerOne | Continuous | Ongoing | 124 (all time) | 3 | 121 | Active |
| OWASP ZAP Scan | Internal | Automated | Weekly | Last: 12 findings | 4 | 8 | Ongoing |

**Findings Table (filtered by status: Open):**

| Finding ID | Severity | Title | OWASP Category | Found By | Found At | Assigned To | Fix Deadline | Status |
|---|---|---|---|---|---|---|---|---|
| VAPT-2026-007 | 🔴 Critical | JWT algorithm not validated server-side | A02 (Auth Failures) | SecureIndia | Jan 2026 | Rohan (Backend) | Mar 15 | In Progress |
| VAPT-2026-012 | 🟠 High | Missing HSTS header on portal | A05 (Misconfiguration) | SecureIndia | Jan 2026 | Priya (Frontend) | Mar 30 | In Progress |

**Finding detail (expandable):**
- Full description · reproduction steps (masked for external findings) · CVSS score · OWASP category
- Remediation notes (engineer who owns it)
- Fix evidence (PR link · test results showing fix)

**OWASP ZAP Integration:**
- Auto-triggered weekly by CI/CD (C-09)
- Latest scan results imported automatically
- "Run OWASP ZAP scan now" button (on-demand)
- Last scan: 3 days ago · 12 findings · 4 open

---

### Section 11 — Active Threat Alerts

**Purpose:** Centralised real-time feed of all active security alerts requiring attention.

**Alert Feed:**

| Time | Alert | Severity | Source | Status | Action |
|---|---|---|---|---|---|
| 5 min ago | Credential stuffing: 842 failed logins from 48 IPs | P1 | Failed Auth Heatmap | ⚡ Active | Block IPs · Create incident |
| 22 min ago | New CVE detected: cryptography 9.8 CVSS | P2 | pip-audit CI run | ⏳ Triaging | View CVE |
| 1h ago | JWT anomaly: token reuse from RU IP | P1 | JWT Detector | ✅ Resolved | View details |
| 2h ago | WAF spike: 2,400 blocked requests in 5 min | P2 | AWS WAF | ✅ Resolved | View WAF |

**Alert filtering:** Severity · Source · Status (Active / Resolved / Acknowledged)

**Alert acknowledgement:** "Acknowledge" button → removes from active count but keeps in log

**Integration with C-18:** "Create incident" per alert → pre-fills incident with alert context

---

## 5. User Flow

### Flow A — Responding to Credential Stuffing Attack

1. KPI strip: "Failed Logins (1h): 3,200" (red alert)
2. Security Engineer opens Failed Auth Heatmap
3. Heatmap shows: 48 IPs from 45.142.212.0/24 (Russia) — coordinated attack
4. "Distributed attack detected" banner shown
5. Security Engineer clicks "Block /24 subnet" → 2FA confirmation
6. WAF rule added: block 45.142.212.0/24 (24h expiry)
7. Failed login rate drops to baseline within 2 min
8. CERT-In assessment: credential stuffing is reportable if accounts compromised
9. Runs investigation: no successful logins from attack IPs → no breach
10. Incident logged in C-18 as "Attack contained — no breach"

### Flow B — CERT-In Breach Reporting

1. Security breach detected: SQL injection exposed 420 student exam records
2. CERT-In incident auto-created from anomaly detection
3. Countdown timer starts: 6h from detection
4. Security Engineer navigates to CERT-In Incident Log
5. Opens incident → fills report form (pre-filled from C-18 incident data)
6. Reviews: affected systems · attack vector · data type · count (420 records)
7. Downloads PDF report
8. Submits to CERT-In portal (external) → enters acknowledgement number
9. Marks as "Submitted" in platform → countdown stops
10. DPDPA assessment: exam results not PII — no DPB notification needed

### Flow C — CVE Triage

1. Weekly CI/CD run detects: new CVE-2025-12345 in `cryptography` package (CVSS 9.8)
2. CVE Tracker: new critical CVE in red
3. Security Engineer reviews: auth-service uses `cryptography` for JWT signing
4. Risk: CVE allows private key extraction → JWT forgery risk
5. Security Engineer creates fix ticket → assigns to Backend Engineer
6. Target fix date: 3 days (critical SLA)
7. CI/CD (C-09) deploys fix → CVE marked as "Fixed" with PR link as evidence
8. Security posture score improves +8 points

---

## 6. Component Structure (Logical)

```
SecurityOpsDashboardPage
├── PageHeader
│   ├── SecurityPostureScore (gauge)
│   ├── ActiveAlertsBanner
│   ├── PageTitle
│   └── CreateIncidentButton
├── KPIStrip × 6
├── WAFRulesPanel
│   ├── WAFRulesTable (priority order)
│   ├── IPBlockList
│   └── WAFMetricsCharts
├── FailedAuthHeatmap
│   ├── HeatmapVisualization (IP/country/tenant/time views)
│   ├── TopOffendersTable
│   └── PatternDetectionBanner
├── AccountLockoutLog
├── JWTAnomalyDetection
│   ├── AnomalyEventsTable
│   └── AutoResponseConfig
├── CVETracker
│   ├── CVESummaryCards × 4
│   ├── CVEDetailsTable
│   └── DependencyScannerPanel
├── CERTInIncidentLog
│   ├── ActiveCountdownTimers
│   ├── IncidentTable
│   └── ReportSubmissionModal
├── DPDPABreachTracker
│   ├── ActiveBreachCountdown
│   └── BreachRecordTable
├── VAPTResultsPanel
│   ├── EngagementHistory
│   └── OpenFindingsTable
└── ActiveThreatAlerts
```

---

## 7. Data Model (High-Level)

### platform_security_incidents

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| incident_type | ENUM | data_breach/auth_attack/ddos/malware/jwt_anomaly/vapt_finding |
| severity | ENUM | p0/p1/p2/p3 |
| title | VARCHAR(200) | |
| description | TEXT | |
| detected_at | TIMESTAMPTZ | |
| certIn_required | BOOLEAN | |
| certIn_submitted_at | TIMESTAMPTZ | nullable |
| certIn_ack_number | VARCHAR(50) | nullable |
| certIn_deadline | TIMESTAMPTZ | computed: detected_at + 6h |
| dpdpa_required | BOOLEAN | |
| dpdpa_submitted_at | TIMESTAMPTZ | nullable |
| dpdpa_deadline | TIMESTAMPTZ | computed: detected_at + 72h |
| status | ENUM | active/contained/resolved/reported |
| resolved_at | TIMESTAMPTZ | nullable |
| resolved_by | UUID FK → platform_staff | nullable |

### platform_cve_registry

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| cve_id | VARCHAR(30) | e.g., CVE-2025-12345 |
| severity | ENUM | critical/high/medium/low |
| cvss_score | DECIMAL(3,1) | |
| package_name | VARCHAR(100) | |
| affected_version | VARCHAR(50) | |
| fixed_version | VARCHAR(50) | nullable |
| affected_services | JSONB | array of service names |
| status | ENUM | new/triaged/in_progress/fixed/accepted_risk |
| accepted_risk_reason | TEXT | nullable |
| accepted_risk_expires_at | DATE | nullable |
| assigned_to | UUID FK → platform_staff | nullable |
| fix_deadline | DATE | nullable |
| fix_pr_url | VARCHAR(512) | nullable |
| first_detected_at | TIMESTAMPTZ | |
| fixed_at | TIMESTAMPTZ | nullable |

---

## 8. Validation Rules

| Rule | Detail |
|---|---|
| WAF rule priority | Must be unique per WebACL; system auto-adjusts conflicts |
| Block /24 subnet | 2FA required · max CIDR: /16 (cannot block entire ISP) |
| Accept CVE risk (critical) | Requires Platform Admin co-approval · justification min 100 chars · max acceptance period: 30 days |
| CERT-In report | Must submit within 6h of breach detection; overdue triggers escalation email to CTO |
| DPDPA notification | Must submit within 72h; overdue triggers legal team notification |
| JWT deny-list | Token revocation entries: 15-day TTL in Redis (longer than any valid JWT lifespan) |
| VAPT finding close | Requires evidence attachment (PR link / test result) before marking as Fixed |
| IP block permanent | Admin + Security only · 2FA · reason required |

---

## 9. Security Considerations

| Control | Detail |
|---|---|
| WAF WAFV2 API | Server-side only; `wafv2:UpdateWebACL` scoped to platform WebACL ARN; cannot modify other WAF resources |
| CERT-In report data | Contains breach details; access restricted to Security Engineer + Platform Admin; not visible to other roles |
| Account lockout details | Student emails masked in UI (`jo**@gmail.com`); full email visible in audit log (Security/Admin only) |
| JWT anomaly data | `jti` values logged; actual JWT signatures never exposed; payload decoded server-side only |
| CVE data | pip-audit results stored in S3 encrypted; only summary shown in UI; full report downloadable by Security/Admin |
| This page itself | Security Ops page behind Level 4 auth; no public routes; 2FA re-challenge after 15 min idle |
| VAPT reproduction steps | Masked/redacted for external-vendor findings; shown only to Security Engineer after "view sensitive details" 2FA challenge |

---

## 10. Edge Cases (System-Level)

| Scenario | Handling |
|---|---|
| Multiple CERT-In incidents open simultaneously | Each has independent countdown; most urgent shown first; "3 incidents open — 2 overdue" escalation |
| CERT-In portal (external) unavailable at deadline | System recommends email submission as fallback; email template auto-generated with all required fields |
| WAF rule conflicts (same path in multiple rules) | AWS WAF evaluates in priority order; system warns if conflicting rules detected: "Rule #3 and Rule #7 both match /api/exams/*. Rule #3 will take precedence." |
| False positive CVE (package version incorrect in dependency graph) | "Mark as false positive" option; Security Engineer provides reason; excluded from future scans until acknowledged |
| Mass lockout event (exam day network issue) | Mass unlock available; Security Engineer must review pattern first to confirm it's not a real attack |
| DPDPA breach involving minors (school students < 18) | Separate "Data Principal: Minor" flag; parental guardian notification also required; system prompts Security Engineer to add guardian contact details to breach report |
| Security incident during CERT-In reporting window | C-18 incident linked to CERT-In record; any updates to incident status auto-update CERT-In report draft |

---

## 11. Performance & Scaling Strategy

| Concern | Strategy |
|---|---|
| Failed auth aggregation | CloudWatch Logs Insights query aggregated every 15 min by Celery; UI shows last-computed result (not real-time) + live event stream (last 100 events) |
| WAF metrics | CloudWatch WAF namespace; batched with other CloudWatch calls; 5-min cache |
| JWT anomaly detection | Lambda middleware writes anomaly events to SQS; Celery consumer processes and writes to DB; 30s processing lag acceptable |
| Heatmap rendering | Pre-aggregated buckets (15-min × IP/country/tenant); stored in Redis sorted sets; heatmap rendered server-side as SVG; no D3 in browser |
| CVE database | pip-audit + Snyk run in CI/CD (not on this page); results webhook into platform; page reads from DB; no on-demand scanning except "Run scan" button |
| CERT-In/DPDPA countdowns | Client-side countdown (JS) seeded from server-provided `deadline_at` timestamp; no server polling for countdown itself |
| Security posture score | Computed by Celery beat every hour; stored in Redis; page load reads from cache < 5ms |
