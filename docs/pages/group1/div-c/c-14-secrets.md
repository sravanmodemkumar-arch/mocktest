# C-14 — Secret & Key Manager

> **Route:** `/engineering/secrets/`
> **Division:** C — Engineering
> **Primary Role:** Platform Admin (Role 10) · Security Engineer (Role 16) · DevOps/SRE (Role 14)
> **File:** `c-14-secrets.md`
> **Priority:** P0 — Required before any credential-holding service goes live
> **Status:** ✅ Spec done

---

## 1. Page Name & Route

**Page Name:** Secret & Key Manager
**Route:** `/engineering/secrets/`
**Part-load routes:**
- `/engineering/secrets/?part=kpi` — secrets health KPI
- `/engineering/secrets/?part=inventory` — secret inventory table
- `/engineering/secrets/?part=drawer&secret_id={id}` — secret detail drawer
- `/engineering/secrets/?part=rotation-schedule` — rotation schedule calendar
- `/engineering/secrets/?part=rotation-history` — rotation audit history
- `/engineering/secrets/?part=kms-panel` — AWS KMS CMK panel

---

## 2. Purpose (Business Objective)

The Secret & Key Manager is the master inventory and rotation control centre for every sensitive credential the platform uses. From JWT signing keys to Razorpay API keys, from RDS master credentials to FCM server keys — all are catalogued here with their rotation schedules, current health, and AWS Secrets Manager sync status.

The most critical capability on this page is the rotation trigger: a compromised JWT signing key must be rotated within minutes, not hours. This page provides a 2FA-gated, one-click rotation mechanism that handles the full lifecycle: generate new secret → update in AWS Secrets Manager → notify dependent services → confirm propagation.

Key management failure is the most common cause of high-severity security incidents in cloud systems. This page makes the invisible visible: every secret has an owner, an expiry, a rotation schedule, and a propagation status.

**Business goals:**
- Complete inventory of all platform secrets with zero unknown/untracked secrets
- Automated rotation reminders 30 days before expiry
- 2FA-gated emergency rotation within minutes of compromise detection
- AWS Secrets Manager sync status verification for every secret
- KMS Customer Master Key management for data encryption
- Audit trail of every secret creation, rotation, and access event

---

## 3. User Roles

| Role | Access Level | Permissions |
|---|---|---|
| Platform Admin (10) | Level 5 | Full: view inventory (masked) · trigger rotation · view rotation history · manage KMS |
| Security Engineer (16) | Level 4 | Full: view inventory (masked) · trigger rotation · view rotation history · manage KMS |
| DevOps / SRE (14) | Level 4 | View inventory (masked) · trigger rotation for infra secrets · view rotation history |

> **Critical:** No role on this page can view the actual secret value. Values are always masked. Secret values are only accessible to the services that consume them via AWS Secrets Manager SDK at runtime.

---

## 4. Section-Wise Detailed Breakdown

---

### Section 1 — Page Header & Secrets Health

**Purpose:** Instant health verdict on the entire secret estate.

**Secrets Health Banner:**

| State | Colour | Text |
|---|---|---|
| ✅ All secrets healthy | Green | "42 secrets · All within rotation schedule · No expiring in < 30 days" |
| ⚠ Rotation due | Amber | "3 secrets due for rotation in < 30 days" |
| 🚨 Secret expired or compromised | Red | "1 secret expired · Emergency rotation required" |

**Header elements:**
- H1 "Secret & Key Manager"
- Secrets health banner
- Total secrets count: "42 secrets tracked"
- "Add Secret" button (Admin/Security)
- "Run Rotation Audit" button → scans all secrets for expiry + Secrets Manager sync status
- Last audit: "Rotation audit: 2 days ago · All healthy"

---

### Section 2 — KPI Strip

**KPI Cards:**

| Card | Metric | Alert |
|---|---|---|
| Total Secrets | Count in registry | — |
| Expiring < 30 days | Secrets with expiry within 30 days | > 0 = amber |
| Expiring < 7 days | Secrets with expiry within 7 days | > 0 = red |
| Rotation Overdue | Secrets past scheduled rotation date | > 0 = red |
| AWS Secrets Manager Sync | Secrets not synced to Secrets Manager | > 0 = red |
| KMS Keys Enabled | All CMKs in enabled state | Any disabled = amber |

---

### Section 3 — Secret Inventory Table

**Purpose:** Complete catalogue of all platform secrets with health status and metadata.

**Table Columns:**

| Column | Description | Sortable |
|---|---|---|
| Secret Name | Human-readable name | ✅ |
| Category | Signing key · Database · Third-party API · Encryption · OAuth · Infrastructure | ✅ |
| Service(s) | Which Lambda functions/services use this secret | — |
| AWS Secrets Manager ARN | Short ARN (last 30 chars visible) | — |
| KMS Key | Which CMK encrypts this secret | — |
| Last Rotated | Date of last rotation | ✅ |
| Rotation Schedule | Monthly / Quarterly / Annually / Never (with justification) | ✅ |
| Next Rotation Due | Date | ✅ |
| Expiry | If the secret has a hard expiry (API keys, certificates) | ✅ |
| Days to Expiry | Number (colour: green > 90 · amber 30–90 · red < 30) | ✅ |
| Secrets Manager Sync | ✅ Synced · ⚠ Stale · ❌ Not synced | — |
| Status | ✅ Healthy · ⚠ Rotation due · 🚨 Expired · 🔴 Compromised | ✅ |

**Secret Categories and Examples:**

| Category | Examples |
|---|---|
| JWT Signing Keys | `jwt-access-signing-key` · `jwt-refresh-signing-key` |
| Database Credentials | `rds-master-password` · `rds-readonly-password` · `pgbouncer-auth-password` |
| AWS KMS CMKs | `platform-data-cmk` · `platform-tenant-media-cmk` · `mobile-hive-aes-key-ref` |
| Third-party API Keys | `razorpay-key-id` · `razorpay-key-secret` · `fcm-server-key` · `ses-smtp-password` · `sentry-dsn` |
| OAuth Secrets | `google-oauth-client-secret` · `saml-sp-private-key` |
| Infrastructure | `cloudflare-api-token` · `github-actions-pat` · `pagerduty-integration-key` |
| Mobile | `hive-aes-256-key` · `ios-push-cert-p8` · `android-keystore-ref` |
| AI/ML | `openai-api-key` · `anthropic-api-key` · `google-ai-api-key` |

**Filter Bar:**
- Category filter
- Status filter (Healthy / Rotation Due / Expired / Compromised)
- Service filter (which service uses this secret)
- Sort: next rotation due · days to expiry · last rotated

**No secret values shown anywhere in the table.** The table contains only metadata.

---

### Section 4 — Secret Detail Drawer

**Purpose:** Full detail for a single secret without ever exposing the value.

**Drawer Width:** 560px
**Tabs:**

---

#### Tab 1 — Current Secret Details

**Fields:**

| Field | Value | Notes |
|---|---|---|
| Secret Name | `jwt-access-signing-key` | |
| Description | "HMAC-SHA256 key for signing JWT access tokens" | |
| Category | JWT Signing Key | |
| AWS Secrets Manager ARN | `arn:aws:secretsmanager:ap-south-1:...` | Full ARN shown |
| KMS Encryption Key | `platform-data-cmk (alias/platform-data)` | |
| Secret Type | String · JSON · Binary | |
| Value | `••••••••••••••••••••` (always masked) | Never shown |
| Value Length | "512-bit key (64 bytes)" | Metadata only |
| Consuming Services | `auth-service-login · auth-service-token · auth-service-refresh` | |
| Owner | Priya Sharma (Security Engineer) | |
| Created At | Jan 2024 | |
| Created By | Arjun Mehta (Platform Admin) | |
| Last Rotated | Feb 2026 (via automated rotation) | |
| Next Rotation Due | May 2026 | |
| Rotation Schedule | Quarterly | |
| Hard Expiry | None | |
| Secrets Manager Sync | ✅ Synced · Version AWSCURRENT | |
| Last Sync Verified | 2h ago | |

**Actions (Security/Admin):**
- "Trigger Rotation" (primary action — see Section 6)
- "Update Description" (inline edit · no 2FA)
- "Change Owner" (inline select)
- "Change Rotation Schedule" (select + 2FA)
- "Mark as Compromised" (red button · 2FA · triggers emergency rotation workflow)

---

#### Tab 2 — Rotation History

**Purpose:** Immutable log of all rotation events for this secret.

**Columns:**

| Column | Description |
|---|---|
| Timestamp | Rotation completed at |
| Triggered By | Manual (actor name) · Automated (Celery beat) · Emergency (reason) |
| Method | AWS Secrets Manager automatic · Platform manual rotation |
| Previous Version | Short fingerprint of old value (first 8 chars of hash — not the value) |
| New Version | Short fingerprint of new value |
| Propagation | Services that received the new value + confirmation timestamps |
| 2FA Verified | ✅ / — (automated) |

**Retention:** Full rotation history retained permanently (security audit requirement)

---

#### Tab 3 — Propagation Status

**Purpose:** Confirm that all services consuming this secret have received the latest version.

**Table:**

| Service | Last Fetched Version | Fetched At | Status |
|---|---|---|---|
| auth-service-login | AWSCURRENT | 4 min ago | ✅ Current |
| auth-service-token | AWSCURRENT | 3 min ago | ✅ Current |
| auth-service-refresh | AWSPREVIOUS (stale) | 2h ago | ⚠ Stale |

**Propagation mechanism:**
- Lambda functions fetch secrets at cold start (cached locally for function lifetime)
- After rotation: stale services use `AWSPREVIOUS` version (still valid during overlap window)
- Overlap window: 2h (both AWSCURRENT and AWSPREVIOUS valid simultaneously)
- After overlap: `AWSPREVIOUS` deleted; stale services must cold-start to get new version

**"Force restart affected services" action:**
- Flushes Lambda warm pool for all consuming services (sets reserved concurrency to 0 → restores immediately)
- Forces cold starts → services fetch AWSCURRENT on next invocation
- 2FA required

---

### Section 5 — Rotation Schedule Calendar

**Purpose:** Month view of all upcoming secret rotation events.

**Calendar Layout:**
- Month view (default) · List view toggle
- Each rotation event: chip on the date it's due
- Colour: green (> 30 days away) · amber (< 30 days) · red (< 7 days) · black (overdue)

**Calendar Entries:**

| Secret | Due Date | Type | Status |
|---|---|---|---|
| jwt-refresh-signing-key | Mar 25, 2026 | Quarterly rotation | 🟡 Due in 5 days |
| rds-master-password | Apr 1, 2026 | Quarterly rotation | ✅ Due in 12 days |
| razorpay-key-secret | Apr 15, 2026 | Annual review | ✅ Due in 26 days |

**Upcoming this month summary card:**
- "4 rotations due in March 2026 — 1 overdue"
- Quick links to each overdue/upcoming secret

**Notification settings:**
- Email notification to secret owner: 30 days before · 7 days before · day-of
- Configurable per secret or platform-wide

---

### Section 6 — Secret Rotation Workflow

**Purpose:** Guided, safe rotation of any secret — from normal scheduled rotation to emergency rotation.

**Trigger:** "Trigger Rotation" button in secret detail drawer

**Two rotation paths:**

---

#### Path A — Standard Rotation

Used for: Scheduled quarterly/annual rotations

**Step 1 — Review:**
- Current secret metadata shown
- "Rotation type: Standard (scheduled)"
- "Services that will be affected: auth-service (3 Lambda functions)"
- "Overlap window: 2 hours (both old and new value valid simultaneously)"
- Warning if active exams: "2 exams currently in progress. Students mid-exam use active JWT tokens. Standard rotation uses overlap window — existing tokens remain valid. Safe to proceed."

**Step 2 — Method:**
- AWS Secrets Manager automatic rotation (Lambda rotation function): recommended for DB credentials + API keys that support automated rotation
- Platform-managed rotation: for secrets that require manual key generation (e.g., JWT signing keys — must generate cryptographically secure random bytes)

**Step 3 — 2FA Confirmation:**
- TOTP input
- "Rotate Secret" button

**On rotation:**
- New value generated (either by AWS Lambda rotation function or platform Celery job)
- AWS Secrets Manager version: new value = AWSCURRENT · old value = AWSPREVIOUS
- Overlap window (2h): both versions valid simultaneously for consuming services
- Propagation tracking in Tab 3 updates
- Rotation history entry created

---

#### Path B — Emergency Rotation

Used for: Suspected or confirmed secret compromise

**Trigger:** "Mark as Compromised" button OR from C-13 Security Ops threat alert

**Key differences from standard rotation:**
- **No overlap window** — old secret value invalidated immediately
- All consuming services force-restarted (Lambda warm pool flushed)
- All active sessions using JWT signed with compromised key: invalidated (Redis session deny-list bulk insert)
- CERT-In assessment triggered: "Was this secret compromise a data breach? If any student/staff data was accessed using this compromised credential, CERT-In notification required."
- C-18 incident automatically created

**Step 1 — Compromise Assessment:**
- Compromise type: Exposed in code · Leaked to logs · Phishing · Insider threat · Unknown
- Estimated time of compromise (date-time picker)
- "How many accounts may have been affected?" (estimate for CERT-In/DPDPA)

**Step 2 — 2FA (both Admin + Second Approver):**
- Emergency rotation requires dual-admin approval (same pattern as emergency data wipe in C-01)
- Second approver notified immediately via email + platform alert

**Step 3 — Execute:**
- System actions (all atomic):
  1. Generate new secret value
  2. Update AWS Secrets Manager (AWSCURRENT)
  3. Set old value to AWSPENDING (will be deleted in 15 min — no overlap window for emergency)
  4. Flush Lambda warm pools for all consuming services
  5. Bulk-invalidate all active sessions (for JWT keys only) via Redis SCAN + DEL
  6. Create C-18 incident
  7. Log to CERT-In incident log (if applicable)
  8. Notify all consuming service owners via email

**Duration:** Emergency rotation completes in < 5 minutes (fast path)

---

### Section 7 — AWS KMS Customer Master Key Panel

**Purpose:** Manage the AWS KMS CMKs used to encrypt all secrets and data-at-rest.

**CMK Inventory:**

| Key Alias | Key ID (short) | Purpose | Status | Key Rotation | Last Rotation | Created |
|---|---|---|---|---|---|---|
| alias/platform-data | key-abc123 | Encrypts all Secrets Manager secrets | ✅ Enabled | ✅ Annual (auto) | Jan 2026 | Jan 2023 |
| alias/platform-rds | key-def456 | RDS storage encryption | ✅ Enabled | ✅ Annual (auto) | Jan 2026 | Jan 2023 |
| alias/platform-s3 | key-ghi789 | S3 bucket encryption (non-public) | ✅ Enabled | ✅ Annual (auto) | Jan 2026 | Jan 2023 |
| alias/platform-tenant-media | key-jkl012 | Tenant uploaded media encryption | ✅ Enabled | ✅ Annual (auto) | Jan 2026 | Jan 2023 |
| alias/mobile-hive-aes | key-mno345 | Flutter Hive AES-256 key material | ✅ Enabled | Manual (annual) | Jan 2026 | Jan 2023 |

**CMK Status Badges:**
- Enabled ✅
- Disabled ⚠ (no decryption possible — data locked)
- Pending deletion 🚨 (highly destructive — cannot be undone)

**Actions per CMK (Admin/Security):**
- "Enable/Disable" → 2FA required · Disable warning: "Disabling this key will prevent all services from decrypting data encrypted with it. This will break the platform."
- "Schedule key deletion" → Admin only · 2FA · minimum 7-day grace period · warning: "IRREVERSIBLE: All data encrypted with this key will be permanently inaccessible after deletion."
- "View key policy" → IAM policy JSON (read-only view)
- "View key usage" → Count of cryptographic operations/day (CloudWatch KMS metrics)

**Key rotation status:**
- AWS KMS automatic annual rotation: enabled/disabled toggle
- When rotation occurs: new key material generated; old key material retained for decryption of existing data; new encryptions use new material
- Manual rotation: only for keys that need to be rotated on non-annual schedule

**KMS audit (CloudTrail):**
- "View KMS usage in CloudTrail" → filtered CloudTrail events for this key (Decrypt, Encrypt, GenerateDataKey operations)
- Anomaly detection: unusual Decrypt volume for a key → Security Engineer alerted

---

### Section 8 — Dependency Map

**Purpose:** Show which services depend on which secrets — "what breaks if this secret is rotated?"

**Visualization:**
- Directed graph: secrets (circle nodes, colour by category) → services (square nodes)
- Click a secret node → highlights all dependent services
- Click a service node → highlights all secrets it depends on

**Use cases:**
- Pre-rotation: "If I rotate razorpay-key-secret, which services will need cold starts?" → 2 services highlighted
- Incident response: "The auth-service is failing — which secrets does it depend on?" → 4 secrets highlighted

**Table view alternative (for those who prefer tables over graphs):**

| Secret | Consuming Services | Lambda Functions | ECS Services |
|---|---|---|---|
| jwt-access-signing-key | auth-service | auth-service-login, auth-service-token, auth-service-refresh | — |
| rds-master-password | All DB-touching services | 12 Lambda functions | celery-worker (via Django) |
| razorpay-key-secret | billing-service | billing-service-order, billing-service-webhook | — |

---

## 5. User Flow

### Flow A — Quarterly JWT Key Rotation

1. Security Engineer receives rotation reminder: "jwt-access-signing-key due in 5 days"
2. Opens `/engineering/secrets/` → finds secret in table (amber status)
3. Clicks row → drawer opens → "Trigger Rotation"
4. Step 1: reviews affected services (3 auth Lambda functions)
5. Step 2: method = Platform-managed (generate 512-bit random key)
6. Step 3: TOTP entered → "Rotate Secret" clicked
7. New key generated; AWS Secrets Manager updated
8. Propagation tab: all 3 services still on AWSPREVIOUS (Lambda haven't cold-started yet)
9. 2h overlap window: both old and new JWT keys valid
10. After 2h: AWSPREVIOUS deleted; all Lambda cold-start with new key
11. Rotation history: entry created with fingerprint comparison

### Flow B — Emergency Rotation After Key Leak

1. Developer accidentally commits JWT signing key to GitHub (detected by git-secrets hook)
2. Security Engineer opens C-13 → creates security incident
3. Navigates to C-14 → finds `jwt-access-signing-key`
4. Clicks "Mark as Compromised" → describes: "Exposed in git commit abc123"
5. Dual-admin approval: second admin approves via email link
6. Emergency rotation executes:
   - New key generated in < 1s
   - Old key invalidated immediately (no overlap window)
   - All 74,000 active JWT tokens invalidated (Redis bulk delete)
   - Lambda warm pools flushed
   - Students logged out → must re-login
7. Duration: ~4 min total
8. CERT-In assessment: key leak without confirmed data access → file informational report

### Flow C — Pre-Exam Secrets Health Check

1. DevOps runs rotation audit before major exam day
2. All 42 secrets: ✅ synced to Secrets Manager
3. KMS panel: all 5 CMKs enabled
4. Calendar: no rotations due in next 24h (good — no planned disruption)
5. Razorpay key: 84 days until expiry (green — no action needed)
6. JWT key: next rotation in 22 days (green — safe for exam)
7. DevOps confirms: "All secrets healthy — exam day green"

---

## 6. Component Structure (Logical)

```
SecretKeyManagerPage
├── PageHeader
│   ├── SecretsHealthBanner
│   ├── PageTitle
│   ├── AddSecretButton
│   └── RunRotationAuditButton
├── KPIStrip × 6
├── SecretInventoryTable
│   ├── FilterBar
│   └── SecretRow × 42
│       └── (all columns — values always masked)
├── SecretDetailDrawer (560px)
│   └── DrawerTabs
│       ├── CurrentDetailsTab
│       ├── RotationHistoryTab
│       └── PropagationStatusTab
├── RotationWorkflow (inline modal/panel)
│   ├── PathA_StandardRotation (3 steps)
│   └── PathB_EmergencyRotation (3 steps + dual-admin approval)
├── RotationScheduleCalendar
│   ├── MonthView / ListView toggle
│   └── UpcomingRotationSummaryCard
├── KMSPanel
│   ├── CMKInventoryTable
│   └── CMKDetailActions
└── DependencyMap
    ├── GraphView
    └── TableView (alternative)
```

---

## 7. Data Model (High-Level)

### platform_secret_registry

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| secret_name | VARCHAR(100) | human-readable name |
| description | TEXT | |
| category | ENUM | jwt/database/api_key/kms/oauth/infra/mobile/ai |
| aws_secrets_manager_arn | VARCHAR(512) | full ARN |
| kms_key_alias | VARCHAR(100) | |
| consuming_services | JSONB | array of service names + Lambda function names |
| owner_id | UUID FK → platform_staff | |
| rotation_schedule | ENUM | monthly/quarterly/annual/manual/never |
| last_rotated_at | DATE | |
| next_rotation_due | DATE | computed |
| hard_expiry | DATE | nullable |
| rotation_method | ENUM | aws_automatic/platform_managed |
| status | ENUM | healthy/rotation_due/expired/compromised |
| created_by | UUID FK → platform_staff | |
| created_at | TIMESTAMPTZ | |

### platform_secret_rotation_log (immutable)

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| secret_id | UUID FK | |
| rotation_type | ENUM | standard/emergency |
| triggered_by | UUID FK → platform_staff | nullable (automated) |
| approved_by | UUID FK → platform_staff | nullable (dual-admin for emergency) |
| twofa_verified | BOOLEAN | |
| previous_version_fingerprint | CHAR(16) | SHA256 of old value, first 16 chars |
| new_version_fingerprint | CHAR(16) | SHA256 of new value, first 16 chars |
| propagation_status | JSONB | per-service propagation timestamps |
| certIn_triggered | BOOLEAN | |
| reason | TEXT | nullable (for emergency/compromised) |
| created_at | TIMESTAMPTZ | immutable |

---

## 8. Validation Rules

| Rule | Detail |
|---|---|
| Standard rotation | 2FA required for all rotations regardless of schedule |
| Emergency rotation | Dual-admin approval (two separate TOTP submissions) · reason required · cannot be bypassed |
| KMS key deletion schedule | Minimum 7-day waiting period; cannot be shortened · Admin only |
| KMS key disable | 2FA + "disable during exam hours" blocked (blocks all decryption) |
| Rotation during active exam | Standard rotation: allowed (overlap window protects in-flight JWTs) · Emergency rotation: allowed with warning "All 74K active sessions will be terminated" |
| Adding new secret | Must have: name · description · category · Secrets Manager ARN · owner · rotation schedule |
| Secret value viewing | Blocked for all roles on this page — value only accessible via AWS Secrets Manager SDK at service runtime |
| Rotation schedule "Never" | Requires written justification (min 50 chars) · Security Engineer approval |
| Overlap window for emergency | Cannot be set; always zero (immediate invalidation) |

---

## 9. Security Considerations

| Control | Detail |
|---|---|
| Secret values never displayed | Enforced at API layer: endpoint returns metadata only; actual secret value never included in API response; AWS Secrets Manager GetSecretValue never called from this page |
| AWS IAM scope | `secretsmanager:DescribeSecret` + `secretsmanager:GetSecretValue` (for metadata only, not value) + `secretsmanager:RotateSecret`; cannot ListSecrets outside platform namespace (resource-level IAM restriction) |
| KMS key usage audit | All KMS API calls logged to CloudTrail; anomaly detection on unusual Decrypt volume |
| Rotation log immutability | `platform_secret_rotation_log` INSERT-only; same pattern as audit logs throughout platform |
| Dual-admin emergency rotation | Prevents single-admin social engineering or coercion; both approval tokens delivered via separate email |
| Propagation force-restart | Lambda warm pool flush logs to `platform_infra_events` (C-08 audit trail) |
| Session invalidation on JWT rotation | Redis bulk SCAN for `session:*` keys; bulk DEL; < 2 min for 40M key namespace; students must re-login — this is expected behaviour for emergency rotation |
| SAML private key rotation | Requires coordination with Google Workspace admin (SAML metadata must be updated externally); system provides step-by-step instructions in rotation wizard |

---

## 10. Edge Cases (System-Level)

| Scenario | Handling |
|---|---|
| AWS Secrets Manager unavailable during rotation | Rotation fails gracefully; old secret remains valid; "Rotation failed — Secrets Manager API unavailable. Retry when resolved." + alert to Security team |
| Lambda service doesn't pick up new secret after overlap window | "Force restart" button in Propagation tab; Celery job flushes warm pool; service will fetch new secret on next cold start |
| Rotation triggered for a secret that doesn't support AWS automatic rotation | System falls back to "Platform-managed rotation" — generates new value locally, stores in Secrets Manager manually |
| KMS key accidentally disabled | System detects "Decrypt failed" errors in Lambda CloudWatch logs within 5 min; C-18 auto-incident created; Security Engineer alerted; re-enable requires 2FA |
| Compromise detected for RDS master password | Emergency rotation + all DB connection pools closed (PgBouncer restart) + all Django worker processes restarted (new DB credentials fetched) + full outage for ~3 min |
| Secret with no consuming services | Amber flag: "No services listed as consumers. Verify this secret is still needed or archive it." |
| Rotation reminder email bounces (owner email changed) | Platform sends to Platform Admin as fallback; system prompts to update owner on secrets with bounced notifications |

---

## 11. Performance & Scaling Strategy

| Concern | Strategy |
|---|---|
| 42 secrets inventory (small scale) | All 42 secrets loaded at once; no pagination needed; full page load < 100ms |
| AWS Secrets Manager API calls | `DescribeSecret` (metadata only) called for each of 42 secrets; batched; cached Redis 5 min |
| Rotation audit (on-demand) | Celery job: 42 × DescribeSecret + GetSecretRotationStatus + Secrets Manager sync check; completes in < 30s |
| Propagation status polling | Draws from C-04 / C-05 Lambda cold-start telemetry; no new API calls needed |
| Emergency rotation < 5 min | All steps async via Celery; UI polls job status every 5s; critical path (generate + Secrets Manager update) < 10s; Lambda flush + Redis bulk delete run in parallel |
| KMS metrics | CloudWatch `AWS/KMS` namespace; batched with other CloudWatch calls; 5 min cache |
| Dependency graph rendering | Rendered server-side (Graphviz or D3 pre-computed SVG); 42 secrets × ~3 services each = small graph; render < 200ms |
