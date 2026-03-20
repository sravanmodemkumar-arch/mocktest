# Group 1 — Division C: Engineering — Pages Reference

> **Division:** C — Engineering
> **Roles:** Platform Admin · Backend Engineer · Frontend Engineer · Mobile Engineer · DevOps/SRE · Database Administrator · Security Engineer · AI/ML Engineer
> **Base URL prefix:** `/engineering/`
> **Access Level:** Level 4 (Engineering) · Level 5 (Platform Admin — unrestricted)
> **Status key:** ✅ Spec done · 🔨 In progress · ⬜ Not started

---

## Scale Context (always keep in mind when designing every page)

| Dimension | Value |
|---|---|
| Total institution tenants | 2,050 (each = isolated PostgreSQL schema) |
| Total PostgreSQL schemas | 2,051 (2,050 tenant + 1 shared platform schema) |
| Peak concurrent users | **74,000 simultaneous exam submissions** |
| Lambda functions | ~60–80 across all services |
| Redis keyspace at peak | ~40M keys |
| Total students | 2.4M–7.6M |
| Mobile installs | 3M+ (Flutter iOS + Android) |
| Questions in bank | 2M+ |
| AWS primary region | ap-south-1 (Mumbai) · DR: ap-southeast-1 (Singapore) |
| Active CI/CD repos | ~12 (portal · mobile · infra · content · AI pipeline) |
| RDS instance | PostgreSQL 15 · Multi-AZ · db.r6g.2xlarge + 2 read replicas |
| ElastiCache | Redis 7.x · cluster mode · 3 shards × 2 nodes |
| CloudFront distributions | 3 (portal · static assets · API edge) |
| Monthly AI API spend | ₹8L–₹15L (LLM for MCQ generation) |
| CERT-In breach reporting window | **6 hours** from discovery |
| DPDPA 2023 breach notification | **72 hours** to Data Protection Board |

---

## Division C — Role Summary

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 10 | Platform Admin | 5 | All tenant mgmt · user provisioning · system config · emergency overrides | Nothing blocked |
| 11 | Backend Engineer | 4 | API config · Lambda deployments · DB migrations · service health | Billing config |
| 12 | Frontend Engineer | 4 | HTMX templates · CDN cache invalidation · R2/S3 static assets | DB access |
| 13 | Mobile Engineer — Flutter | 4 | Flutter builds · Hive encryption · FCM server config · App Store submission | DB access |
| 14 | DevOps / SRE Engineer | 4 | AWS Lambda · ECS · RDS · ElastiCache · CI/CD · auto-scaling · rollbacks · on-call | Content · billing |
| 15 | Database Administrator | 4 | PostgreSQL all 2,051 schemas · backups · migrations · query tuning · PITR | Business config |
| 16 | Security Engineer | 4 | JWT secrets · KMS · WAF rules · CERT-In reports · DPDPA breach · VAPT coordination | Content · billing |
| 17 | AI / ML Engineer | 4 | MCQ generation pipeline · LLM model config · prompt versioning · AI API cost | Content approval |

---

## Platform Admin — Pages (Role 10) · 3 pages

> Level 5 — no restrictions. Highest blast radius in system. Every action 2FA-gated and audit-logged with IP.

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-01 | Tenant Manager | `/engineering/tenants/` | `c-01-tenant-manager.md` | P0 | ✅ | Full CRUD for all 2,050 institution tenants: schema provisioning · plan assignment · suspension (read-only mode) · hard delete with 30-day grace period · emergency data wipe · Celery async provisioning with live progress bar · schema health check · tenant impersonation (Platform Admin only) |
| C-02 | Staff Account Manager | `/engineering/staff/` | `c-02-staff-accounts.md` | P1 | ✅ | All 81 platform staff accounts across 15 divisions: role assignment · 2FA enforcement per level · account suspension · login history · failed login tracking · quarterly access review workflow · SSO (Google Workspace SAML) config · emergency account lock |
| C-03 | System Configuration | `/engineering/system-config/` | `c-03-system-config.md` | P1 | ✅ | Global platform settings: maintenance mode toggle (affects all 2,050 portals simultaneously) · session timeouts per access level · global rate limit overrides · CORS allowed origins · AWS SES sender domain config · Redis cache TTL defaults · emergency master kill switches · feature flag master override |

---

## Backend Engineer — Pages (Role 11) · 2 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-04 | API Health Monitor | `/engineering/api-health/` | `c-04-api-health.md` | P0 | ✅ | All Lambda endpoints: P50/P95/P99 latency per endpoint · error rate by HTTP status code · cold start frequency · throttle events · exam-critical SLA tracking (exam submit < 200ms · result fetch < 500ms) · API version registry (v1/v2/v3) · deprecation tracker with sunset countdowns · endpoint dependency map |
| C-05 | Service Deployment Manager | `/engineering/deployments/` | `c-05-deployments.md` | P1 | ✅ | Lambda function version history · blue/green weighted routing (e.g. 95%/5% canary) · Lambda alias management ($LATEST vs named versions) · one-click rollback to any previous version · pre/post-deploy health check automation · deployment log with actor + timestamp · integration with CI/CD (C-09) and Release Manager (Div B page 03) |

---

## Frontend Engineer — Pages (Role 12) · 1 page

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-06 | CDN & Asset Manager | `/engineering/cdn/` | `c-06-cdn-assets.md` | P2 | ✅ | CloudFront cache invalidation (path patterns · wildcard `/static/*` · emergency full purge) · R2/S3 static asset browser (CSS · JS · images · fonts · WOFF2) · cache hit rate per distribution · asset version registry (content-hash file names) · Brotli/gzip compression status · HTMX template deployment log · CDN cost per GB |

---

## Mobile Engineer — Pages (Role 13) · 1 page

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-07 | Mobile Build Pipeline | `/engineering/mobile-builds/` | `c-07-mobile-builds.md` | P2 | ✅ | Flutter build status iOS + Android · GitHub Actions build logs (live tail) · code signing management (iOS provisioning profiles · Apple certificates · Android keystore) · App Store Connect + Google Play submission tracker · Firebase App Distribution for beta · Crashlytics deep analysis (crash-free rate · ANR rate · affected device models · OS version breakdown) · build artifact registry with version tagging · dSYM/ProGuard symbol upload status |

---

## DevOps / SRE Engineer — Pages (Role 14) · 3 pages

> Most operationally critical role. Owns the platform at 74K peak exam day.

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-08 | Infrastructure Monitor | `/engineering/infrastructure/` | `c-08-infrastructure.md` | P0 | ✅ | Real-time AWS: Lambda total + reserved concurrency per function · ECS cluster CPU/memory/task count · RDS primary + replicas (CPU · connections · IOPS · storage · replica lag) · ElastiCache memory/hit-rate/evictions · ALB request rate + 5xx · CloudFront bandwidth + cache ratio · S3 bucket sizes · All with WRITE controls: change concurrency · restart ECS tasks · promote read replica · drain ALB target |
| C-09 | CI/CD Pipeline Manager | `/engineering/cicd/` | `c-09-cicd.md` | P0 | ✅ | GitHub Actions runs across all 12 repos · pipeline stages (Test → Lint → Build → Deploy Staging → QA Gate → Pre-Prod → Prod) · manual approval gate for production · parallel pipeline grid view · rollback (re-run last passing workflow) · failed pipeline log tail · integration with QA sign-off (Div B page 21) and Release Manager (Div B page 03) · deployment frequency + DORA metrics |
| C-10 | Auto-scaling & Capacity Planner | `/engineering/scaling/` | `c-10-scaling.md` | P1 | ✅ | Lambda reserved + provisioned concurrency config per function · scheduled scaling rules (pre-warm 30 min before exam start) · ECS task min/max per service · RDS read replica add/remove · ElastiCache shard/node scaling · exam calendar integration: upcoming peak events with estimated load · capacity simulation: "at 80K VUs — which service throttles first?" · cost impact of scaling decisions |

---

## Database Administrator — Pages (Role 15) · 2 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-11 | Database Admin Dashboard | `/engineering/database/` | `c-11-database.md` | P0 | ✅ | All 2,051 PostgreSQL schemas: slow query log (> 1s) · active connections per schema · PgBouncer pool status · table sizes top-20 · index health (unused / missing / bloated indexes) · autovacuum status per table · lock monitoring (long-running locks with kill option) · replication lag primary → replicas · query EXPLAIN analyzer · schema size growth trend |
| C-12 | Backup & Migration Manager | `/engineering/db-migrations/` | `c-12-db-migrations.md` | P1 | ✅ | RDS automated snapshot schedule (daily · 30-day retention) · manual snapshot on demand (before risky migrations) · PITR restore to any second in retention window · Django migration status across all 2,051 schemas · pending unapplied migrations list · selective schema migration execution · migration rollback (`migrate app 000X`) · data archival to S3 Glacier (data > 2 years old) · backup cost tracking |

---

## Security Engineer — Pages (Role 16) · 2 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-13 | Security Operations Dashboard | `/engineering/security/` | `c-13-security-ops.md` | P0 | ✅ | AWS WAF rules (block · rate-limit · geo-restrict) · failed auth heatmap (IP · country · time-of-day) · account lockout event log · suspicious JWT anomaly detection · CVE tracker (pip audit + npm audit) · CERT-In incident log with 6h countdown timer · DPDPA breach tracker with 72h notification countdown · full VAPT results · dependency vulnerability scanner · active threat alerts |
| C-14 | Secret & Key Manager | `/engineering/secrets/` | `c-14-secrets.md` | P0 | ✅ | Complete secret inventory: JWT signing keys · AWS KMS CMKs · RDS master credentials · Razorpay API keys (test + live) · FCM server keys · Hive AES-256 keys · S3 presign keys · SMTP credentials · OAuth client secrets · rotation schedule per secret · 2FA-gated rotation trigger · rotation history audit · AWS Secrets Manager sync status · expiry countdowns |

---

## AI / ML Engineer — Pages (Role 17) · 2 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| C-15 | AI Pipeline Dashboard | `/engineering/ai-pipeline/` | `c-15-ai-pipeline.md` | P2 | ✅ | MCQ generation pipeline: batch job status · questions generated vs target · auto-rejection funnel (hallucination · duplicate · formatting · copyright) · prompt version A/B performance comparison · LLM model tracking (Claude · GPT-4o · Gemini) · human review queue depth · review-to-approval rate · per-domain generation stats · error classification breakdown |
| C-16 | AI Cost & Usage Monitor | `/engineering/ai-costs/` | `c-16-ai-costs.md` | P2 | ✅ | LLM token consumption: input + output per model per day · cost per exam domain · cost per question type · monthly budget with 80% alert / 95% hard stop · wasted spend (cost of rejected questions) · model cost comparison · optimization flags (expensive prompts with high rejection rate) · ₹ spend trend MoM · cost per approved question metric |

---

## Cross-Role Shared Pages · 2 pages

| # | Page Name | URL | File | Priority | Status | Description | Roles |
|---|---|---|---|---|---|---|---|
| C-17 | Centralized Log Viewer | `/engineering/logs/` | `c-17-logs.md` | P1 | ✅ | CloudWatch Logs aggregation: structured JSON search · correlation ID trace (single exam submission across all Lambda hops) · log level filter · service filter · tenant filter · time range picker · saved search queries · alert rules (log pattern → PagerDuty) · log retention policy per service | All Div C roles |
| C-18 | Engineering Incident Manager | `/engineering/incidents/` | `c-18-incidents.md` | P0 | ✅ | Active incident board (P0–P2) · incident timeline (detection→ack→mitigate→resolve) · runbook library (30+ known incident types) · on-call schedule (current + 2 weeks) · PagerDuty + OpsGenie integration · postmortem tracker with action items · MTTR analytics · links to War Room (Div A page 32) for exam-day P0s | Platform Admin · DevOps · Security |

---

## Role-to-Page Access Matrix

| Page | Admin (10) | Backend (11) | Frontend (12) | Mobile (13) | DevOps (14) | DBA (15) | Security (16) | AI/ML (17) |
|---|---|---|---|---|---|---|---|---|
| C-01 Tenant Manager | ✅ Full | 👁 Read | — | — | 👁 Read | 👁 Read | 👁 Read | — |
| C-02 Staff Accounts | ✅ Full | — | — | — | — | — | 👁 Read | — |
| C-03 System Config | ✅ Full | — | — | — | ✅ Full | — | 👁 Read | — |
| C-04 API Health | ✅ Full | ✅ Full | 👁 Read | — | ✅ Full | — | 👁 Read | — |
| C-05 Deployments | ✅ Full | ✅ Full | 👁 Read | — | ✅ Full | — | — | — |
| C-06 CDN & Assets | ✅ Full | — | ✅ Full | — | ✅ Full | — | — | — |
| C-07 Mobile Builds | ✅ Full | — | — | ✅ Full | 👁 Read | — | — | — |
| C-08 Infrastructure | ✅ Full | 👁 Read | — | — | ✅ Full | 👁 Read | 👁 Read | — |
| C-09 CI/CD Pipeline | ✅ Full | 👁 Read | 👁 Read | 👁 Read | ✅ Full | — | — | 👁 Read |
| C-10 Auto-scaling | ✅ Full | — | — | — | ✅ Full | 👁 Read | — | — |
| C-11 Database Admin | ✅ Full | 👁 Read | — | — | 👁 Read | ✅ Full | — | — |
| C-12 DB Migrations | ✅ Full | ✅ Full | — | — | 👁 Read | ✅ Full | — | — |
| C-13 Security Ops | ✅ Full | — | — | — | 👁 Read | — | ✅ Full | — |
| C-14 Secrets | ✅ Full | — | — | — | ✅ Full | — | ✅ Full | — |
| C-15 AI Pipeline | ✅ Full | 👁 Read | — | — | 👁 Read | — | — | ✅ Full |
| C-16 AI Costs | ✅ Full | — | — | — | 👁 Read | — | — | ✅ Full |
| C-17 Log Viewer | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| C-18 Incidents | ✅ Full | 👁 Read | — | — | ✅ Full | 👁 Read | ✅ Full | — |

> ✅ Full = read + write + destructive · 👁 Read = read-only · — = no access

---

## Shared Drawers (reused across div-c pages)

| Drawer | Trigger | Width | Tabs |
|---|---|---|---|
| tenant-detail-drawer | Tenant Manager row click | 720px | Config · Schema · Usage · Audit |
| lambda-function-drawer | API Health / Deployments row | 640px | Metrics · Versions · Live Logs · Config |
| migration-detail-drawer | DB Migrations row | 560px | SQL Preview · Affected Schemas · History |
| secret-detail-drawer | Secret Manager row | 560px | Current (masked) · History · Rotation Schedule |
| incident-detail-drawer | Incident Manager row | 720px | Timeline · Runbook · Communications · Postmortem |
| pipeline-run-drawer | CI/CD row | 720px | Stages · Logs · Artifacts · Approvals |
| ai-job-drawer | AI Pipeline row | 640px | Job Config · Sample Questions · Errors · Cost |
| db-query-drawer | Database slow query row | 640px | Explain Plan · Index Suggestions · Historical Trend |

---

## Implementation Priority Order

```
P0 — Before any institution goes live
  C-01  Tenant Manager          (platform cannot run without tenant provisioning)
  C-04  API Health Monitor      (exam submit < 200ms SLA — must track from day 1)
  C-08  Infrastructure Monitor  (74K exam day — real-time AWS with write controls)
  C-09  CI/CD Pipeline Manager  (every deploy goes through this)
  C-11  Database Admin          (2,051 schemas — DBA needs live monitoring)
  C-13  Security Operations     (WAF · CERT-In 6h · DPDPA 72h — compliance from day 1)
  C-14  Secret & Key Manager    (JWT rotation · KMS — security foundation)
  C-18  Incident Manager        (P0 incidents need runbooks before first exam)

P1 — Sprint 2
  C-02  Staff Account Manager   (all 81 roles need accounts before platform opens)
  C-03  System Configuration    (maintenance mode · rate limits · session config)
  C-05  Service Deployment Mgr  (Lambda version control and rollback)
  C-10  Auto-scaling Planner    (pre-warm for exam peaks — needed before first 74K event)
  C-12  Backup & Migration Mgr  (snapshot + PITR before data grows large)
  C-17  Log Viewer              (debugging needs logs from day 1)

P2 — Sprint 3
  C-06  CDN & Asset Manager     (when static assets are significant in scale)
  C-07  Mobile Build Pipeline   (when Flutter app goes to stores)
  C-15  AI Pipeline Dashboard   (when MCQ AI generation is active)
  C-16  AI Cost Monitor         (when AI spend reaches ₹8L+/month)
```

---

## Key Architectural Decisions

| Decision | Approach | Why |
|---|---|---|
| 2,051 separate PostgreSQL schemas | Schema-level multi-tenancy | Row-level tenancy risks cross-tenant leaks from ORM bugs; schema isolation = impossible cross-tenant access |
| Lambda for all API | Serverless | Auto-scales 0 → 74K concurrent without pre-provisioning; at 74K simultaneous exam submits, fixed servers require massive over-provisioning |
| Provisioned concurrency on exam endpoints | Warm Lambdas always ready | Cold starts at 74K = 3–5s delay for first request; provisioned concurrency guarantees < 200ms response |
| Multi-AZ RDS + 2 read replicas | High availability | Primary failure during exam → 74K students lose connection; Multi-AZ auto-failover < 60s |
| Shared RDS, separate schemas | Cost vs isolation balance | 2,050 separate RDS instances = ₹3 Cr/month; shared RDS with schema isolation = ₹80K/month |
| Redis cluster (3 shards × 2 nodes) | Horizontal Redis scaling | Single node bottlenecks at ~40M keys during peak exam; cluster distributes keys across shards |
| PgBouncer transaction-mode pooling | Connection management | 2,050 tenants × 10 Django workers = 20,500 potential connections; PostgreSQL max_connections ≈ 500 |
| Celery for async tenant provisioning | Non-blocking | Provisioning 15,000 students takes 15–25 min; Celery offloads to workers, HTTP responds immediately |
| Prompt versioning for AI | Git-tracked, A/B testable | Prompt changes directly affect question quality; bad prompts increase hallucination; rollback must be instant |

---

## Compliance Obligations for Division C

| Regulation | Obligation | Deadline | Owner | Page |
|---|---|---|---|---|
| CERT-In 2022 Directions | Report cybersecurity incidents | **6 hours** from discovery | Security Engineer (16) | C-13 |
| DPDPA 2023 §31 | Notify Data Protection Board of breach | **72 hours** | Security (16) + DPO (Div N) | C-13 |
| DPDPA — data localisation | Indian student PII stored in India only | Always | DevOps (14) | C-08 |
| IT Act 2000 §43A | Reasonable security for sensitive personal data | Always | Security (16) | C-13, C-14 |
| RBI tokenisation | No raw card data — Razorpay tokens only | Always | Security (16) | C-14 |

---

*Last updated: 2026-03-20*
*Total pages: 18 (C-01 to C-18)*
*Roles covered: 8 (Roles 10–17)*
*Status: Pages list complete — individual page specs pending*
