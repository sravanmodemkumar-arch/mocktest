# EduForge — Ultra-Pro Development Plan (From Scratch)

> **Goal:** Build EduForge from spec to production — 5 crore students, ₹0.60/student/year.
> **Documentation:** 1,633 files, 482,950 lines of specs COMPLETE. Zero guesswork.
> **Philosophy:** Ship the smallest useful thing first. Scale second. Every phase has a deployable product.

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE EDGE (₹0 egress)                      │
│  CDN · R2 Storage · WAF · DDoS · DNS · Workers (edge compute)         │
│  Serves: Questions · Results · Certificates · Notes · Videos · Static  │
│  99% of all reads served here — no Lambda/Fargate touched              │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ Cache MISS only (~1% of traffic)
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     AWS API GATEWAY (ap-south-1)                        │
│  Rate limiting · JWT validation · Routing · HTTPS termination          │
└───┬──────┬──────┬──────┬──────┬──────┬──────────────────────────────────┘
    │      │      │      │      │      │
    ▼      ▼      ▼      ▼      ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│IDENT.││PORTAL││ EXAM ││NOTIF.││BILL. ││  AI  │
│Fast  ││Django││Fast  ││Fast  ││Fast  ││Fast  │
│API   ││HTMX  ││API   ││API   ││API   ││API   │
│Lambda││Farg. ││Lambda││Lambda││Lambda││Lambda│
└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘
   └───────┴───────┴───────┴───────┴───────┘
                       │
           ┌───────────▼───────────┐
           │   PostgreSQL 16 RDS   │
           │  7 schemas, 1 cluster │
           │  + Read replicas      │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │     AWS SQS Queues    │
           │  Async: scoring,      │
           │  notifications, ranks │
           └───────────────────────┘
```

---

## 6 Development Phases

```
PHASE 1 ──── PHASE 2 ──── PHASE 3 ──── PHASE 4 ──── PHASE 5 ──── PHASE 6
Foundation   Institution  Exam         Student      Scale &       Mobile &
& Auth       Portal       Engine       Portal       Optimize      Marketplace
(4 weeks)    (6 weeks)    (5 weeks)    (5 weeks)    (4 weeks)     (6 weeks)
                                                                   
Deploy:      Deploy:      Deploy:      Deploy:      Deploy:       Deploy:
Login works  Schools      Students     5cr students AWS prod      Flutter app
OTP → JWT    can use it   take exams   use portal   Cloudflare    iOS/Android
```

---

## PHASE 1 — Foundation & Auth (Weeks 1–4)

**Outcome:** A person can visit EduForge, log in with OTP, and land on the correct home page based on their role.

### Week 1: Project Bootstrap

| Task | Module Spec | Details |
|---|---|---|
| PostgreSQL schema setup | `00-project-setup` | 7 schemas: identity, portal, exam, notification, billing, ai, analytics |
| Django project restructure | `00-project-setup` | Apps: core, auth, dashboard — shared base templates, dark theme |
| FastAPI identity service | `01-auth` | `/auth/otp/send`, `/auth/otp/verify`, `/auth/token/refresh`, `/health` |
| Docker Compose full stack | `deployment.md` | PostgreSQL 16 + Django (8002) + FastAPI (8001) + Mailpit + pgAdmin |
| Environment config | `deployment.md` | `.env` with all vars, secrets management, dev/prod split |

```python
# Target project structure after Week 1:
mocktest/
├── identity/                    # FastAPI auth service
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── routes/auth.py       # OTP send/verify, token refresh
│   │   ├── models/user.py       # SQLAlchemy: users, otps, sessions
│   │   ├── services/otp.py      # OTP generation, hashing, validation
│   │   ├── services/jwt.py      # JWT create, verify, refresh
│   │   └── config.py            # Settings from env
│   ├── alembic/                 # DB migrations
│   └── requirements.txt
├── portal/                      # Django portal
│   ├── portal/settings.py       # Django config
│   ├── apps/
│   │   ├── core/                # Middleware, context processors, base
│   │   ├── auth_views/          # Login, OTP verify, role select, profile setup
│   │   └── home/                # Dynamic home page per group
│   └── templates/
│       ├── base.html            # Dark theme base
│       └── auth/                # All auth templates
├── docker-compose.yml
└── .env.example
```

### Week 2: Multi-Tenancy & RBAC

| Task | Module Spec | Details |
|---|---|---|
| Multi-tenant middleware | `02-multi-tenancy` | Resolve `{slug}.schools.eduforge.in` → tenant_id in request |
| Institution model | `04-institution-onboarding` | name, domain, type, branding, config JSONB |
| User-Institution linking | `03-roles-permissions` | User can belong to N institutions with different roles |
| RBAC system | `03-roles-permissions` | 87 roles, 6 groups, permission matrix, Django permissions |
| Role-based home routing | `homes/home-routing.md` | After login → detect role → redirect to correct group home |

```sql
-- Core identity tables
CREATE TABLE identity.institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    institution_type VARCHAR(50) NOT NULL,  -- school|college|coaching|exam_domain
    domain VARCHAR(255),
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE identity.user_roles (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES identity.users(id),
    institution_id INT REFERENCES identity.institutions(id),
    role VARCHAR(100) NOT NULL,
    access_level INT DEFAULT 1,  -- 0-5
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, institution_id, role)
);
```

### Week 3: Institution Onboarding & Staff Setup

| Task | Module Spec | Details |
|---|---|---|
| Onboarding wizard | `04-institution-onboarding` | 5-step: basic info → branding → academic year → staff import → go live |
| Academic year/calendar | `05-academic-year-calendar` | Sessions, terms, holidays, exam schedules |
| Branch/campus management | `06-branch-campus-management` | Multi-branch institutions (Sri Chaitanya: 200+ branches) |
| Staff management | `08-staff-management-bgv` | Staff profiles, designations, subjects, timetable assignment |
| Bulk import | `07-student-enrolment` | CSV upload for students and staff with validation |

### Week 4: Student Enrolment & Parent Linking

| Task | Module Spec | Details |
|---|---|---|
| Student profile model | `07-student-enrolment` | Unified student ID, multi-institution linking, access levels S0-S6 |
| Student registration flows | Group 10 div-a specs | Self-reg (exam domain) + institution-created (bulk upload) |
| Parent/guardian management | `09-parent-guardian-management` | Parent registration, child linking via 6-digit code |
| Age-based access levels | Group 10 roles | DOB → auto-assign S0/S1/S2/S3/S4, birthday transitions |
| Student self-registration | `a-01-student-registration.md` | OTP → profile → exam select → plan choice |

**Phase 1 Deliverable:** Login → role-based home → institution setup → students/staff enrolled.

---

## PHASE 2 — Institution Portal (Weeks 5–10)

**Outcome:** Schools, colleges, and coaching centres can run their daily operations on EduForge.

### Week 5: Attendance System

| Task | Module Spec | Details |
|---|---|---|
| School/college attendance | `11-attendance-school-college` | Period-wise, subject-wise, biometric/manual |
| Coaching batch attendance | `12-attendance-coaching-batch` | Batch-wise, session-wise attendance |
| Hostel attendance | `13-attendance-hostel` | Morning/night roll call, leave management |
| Attendance reports | All 3 attendance modules | Daily/weekly/monthly reports, defaulter lists |
| Parent notification | `35-notifications` | Auto SMS/WhatsApp to parents when child is absent |

### Week 6: Academic Core

| Task | Module Spec | Details |
|---|---|---|
| Timetable & scheduling | `10-timetable-scheduling` | Class-wise, teacher-wise, room allocation |
| Syllabus & curriculum | `15-syllabus-curriculum-builder` | Topic mapping, completion tracking, coverage % |
| Homework & assignments | `14-homework-assignments` | Assign, submit, grade, deadline tracking |
| Notes & study material | `16-notes-study-material` | Upload, categorize, share per class/subject |
| Library management | `30-library-management` | Books, issue/return, fine calculation |

### Week 7: Fees & Finance

| Task | Module Spec | Details |
|---|---|---|
| Fee structure management | `24-fee-structure-management` | Fee heads, amounts, due dates, per-class config |
| Fee collection & receipts | `25-fee-collection-receipts` | Online payment (Razorpay), receipt generation, 80C |
| Fee defaulters & recovery | `26-fee-defaulters-recovery` | Overdue tracking, reminders, late fee calculation |
| Billing service (FastAPI) | `56-platform-billing-gst` | Subscription plans, GST invoicing, Razorpay webhooks |
| Payment gateway integration | `57-payment-gateway-byog` | Razorpay Route API (split payment), UPI, cards, netbanking |

### Week 8: Communication & Notifications

| Task | Module Spec | Details |
|---|---|---|
| Notification service (FastAPI) | `35-notifications` | In-app notifications, FCM push, notification preferences |
| WhatsApp integration | `36-whatsapp-addon` | Meta Business API, template messages, OTP fallback |
| SMS service | `38-sms-otp` | MSG91/Twilio, OTP, transactional SMS |
| Email service | `37-email-aws-ses` | AWS SES, templates, bulk email, receipts |
| Announcements & circulars | `34-announcements-circulars` | Institution-wide, class-wise, PDF attachment |

### Week 9: Staff & Admin Features

| Task | Module Spec | Details |
|---|---|---|
| Staff payroll & salary | `27-staff-payroll-salary` | Salary structure, deductions, payslips |
| Hostel management | `28-hostel-management` | Room allocation, mess, complaints |
| Transport & GPS | `29-transport-gps-tracking` | Routes, vehicles, GPS tracking, parent alerts |
| Admission & CRM | `31-admission-enquiry-crm` | Enquiry tracking, follow-up, conversion |
| PTM (Parent-Teacher Meeting) | `33-ptm-parent-teacher-meeting` | Slot booking, video call, feedback |

### Week 10: Compliance & Documents

| Task | Module Spec | Details |
|---|---|---|
| Certificates & TC | `39-certificates-tc` | Generate, verify QR, bonafide, TC, mark sheets |
| Document management | `40-document-management` | Upload, categorize, student document vault |
| POCSO compliance | `41-pocso-compliance` | BGV tracking, mandatory reporting, audit trail |
| DPDP Act compliance | `42-dpdpa-audit-log` | Consent management, data deletion, audit log |
| Counselling & welfare | `32-counselling-student-welfare` | Student welfare events, counsellor notes |

**Phase 2 Deliverable:** Full institution management — attendance, fees, reports, communication.

---

## PHASE 3 — Exam Engine (Weeks 11–15)

**Outcome:** Students can take mock tests with 18L+ concurrent users. This is EduForge's core differentiator.

### Week 11: Question Bank & MCQ System

| Task | Module Spec | Details |
|---|---|---|
| Question bank model | `17-question-bank-mcq` | 18,42,000+ questions, multi-language, LaTeX, images |
| Question authoring UI | Group 9 div-b specs | Rich editor, LaTeX preview, difficulty tagging |
| Bulk upload (Excel/CSV) | `b-02-bulk-upload.md` | Template download, validation, duplicate detection |
| Review & approval pipeline | Group 9 div-c specs | Draft → Review → Approve → Published |
| Content partner portal | Group 9 all specs | Partner registration, content agreement, dashboard |

### Week 12: Exam Paper Builder & Session

| Task | Module Spec | Details |
|---|---|---|
| Exam paper builder | `18-exam-paper-builder` | Auto/manual question selection, blueprint-based |
| Exam session service (FastAPI) | `19-exam-session-proctoring` | Session start, CDN URL, salt, timer |
| IndexedDB architecture | `architecture.md` | Client-side question storage, AES-256 encryption |
| Offline resilience | `c-02-test-attempt.md` | Service Worker, auto-save every 30s, crash recovery |
| Test catalogue | `c-01-test-catalogue.md` | Upcoming, on-demand, calendar view, conflict detection |

```
EXAM ENGINE — 2 Lambda calls per exam (not 200)

Step 1: POST /exam/session/start → returns {session_id, r2_url, salt}
Step 2: Browser fetches encrypted questions from Cloudflare R2 (₹0)
Step 3: Key = HKDF(JWT + salt + test_id) → decrypt in browser
Step 4: All answers stored in IndexedDB (0 server calls during exam)
Step 5: POST /exam/session/{id}/submit → 1 Lambda call
Step 6: Results computed async (SQS) → stored in R2 → served from CDN

Cost per exam: ~₹0.0003 (vs ₹0.15 with traditional REST APIs)
```

### Week 13: Test-Taking Interface

| Task | Module Spec | Details |
|---|---|---|
| NTA-style JEE interface | `c-02-test-attempt.md` | Question palette, section switching, mark for review |
| TCS iON-style SSC interface | `c-02-test-attempt.md` | SSC CGL/CHSL pattern, section tabs |
| Question types | `17-question-bank-mcq` | MCQ single/multi, numerical, match-column, assertion-reasoning |
| Timer & auto-submit | `c-02-test-attempt.md` | Server-side authoritative timer, auto-submit on expiry |
| Language switching | `c-02-test-attempt.md` | Mid-test toggle English ↔ Telugu/Hindi per question |

### Week 14: Results, Ranking & Analytics

| Task | Module Spec | Details |
|---|---|---|
| Submission & auto-grading | `20-exam-submission-auto-grading` | Score computation, negative marking, SQS async |
| Results & rank computation | `21-results-report-cards` | All India Rank across 18L+ students, percentile |
| Leaderboard system | `23-leaderboard-rankings` | AIR, state, city, batch, category-wise ranks |
| Test results & review | `c-03-test-results.md` | Question-by-question, solutions, time analysis |
| Report cards | `21-results-report-cards` | Institution template, PDF generation, QR verification |

### Week 15: Test Series & Mock Test Platform

| Task | Module Spec | Details |
|---|---|---|
| Test series management | `22-test-series-mock-tests` | Scheduled mocks, on-demand, sectional, topic tests |
| Practice questions | `c-04-practice-questions.md` | Untimed, instant feedback, custom filters |
| Previous year papers | `c-05-previous-year-papers.md` | 2,400+ papers, online attempt, cutoff comparison |
| Subscription & access control | `50-subscription-access-control` | Free (5/month) vs Premium (unlimited), institution-gifted |
| Domain configuration | `49-national-exam-catalog` | SSC, Banking, Railways, UPSC, State PSC domain setup |

**Phase 3 Deliverable:** Full exam engine — 18L concurrent, 2 Lambda calls per exam, real-time ranking.

---

## PHASE 4 — Student & Parent Portal (Weeks 16–20)

**Outcome:** 5 crore students have a unified dashboard across all institutions.

### Week 16: Student Dashboard & Performance

| Task | Page Spec | Details |
|---|---|---|
| Unified student dashboard | Group 10 home spec | Institution cards, exam domains, alerts, AI plan |
| Performance dashboard | `b-01-performance-dashboard.md` | Cross-institution score trends, streak tracking |
| Subject analytics | `b-02-subject-analytics.md` | Topic-level drill-down, peer comparison |
| Weak topics & AI | `b-03-weak-topics.md` | Impact-ranked weak areas, recovery plans |
| Leaderboard (student view) | `b-04-leaderboard-rankings.md` | AIR, topper badges, score distribution |

### Week 17: Study Material & Learning

| Task | Page Spec | Details |
|---|---|---|
| Notes library | `d-01-notes-library.md` | Browse, read, bookmark, PDF download (Premium) |
| Video library | `d-02-video-library.md` | 4,200+ hrs, HLS streaming, chapters, resume |
| Video streaming service | `44-video-learning-streaming` | CloudFront HLS, adaptive bitrate, DRM |
| Live classes | `45-live-classes` | WebRTC, chat, recording, attendance |
| Current affairs | `d-05-current-affairs.md` | Daily digest, MCQ quiz, audio summary, monthly PDF |

### Week 18: AI Services

| Task | Module Spec | Details |
|---|---|---|
| AI study plan | `d-03-ai-study-plan.md` | Personalized daily/weekly, goal-based, time-constrained |
| AI doubt solver | `46-ai-doubt-solver` | Image OCR, semantic search, expert routing |
| AI performance analytics | `47-ai-performance-analytics` | Weak topic identification, projected rank |
| AI content generation | `48-ai-content-generation` | MCQ generation from topics, quality scoring |
| Doubt forum | `d-04-doubt-forum.md` | AI auto-answer, community, expert (Premium) |

### Week 19: Fees, Payments & Documents (Student)

| Task | Page Spec | Details |
|---|---|---|
| Fee statement (cross-institution) | `e-01-fee-statement.md` | Unified view across all institutions |
| Online payment | `e-02-online-payment.md` | Razorpay, UPI, cards, split payments |
| Documents & certificates | `e-03-documents-certificates.md` | ID cards, bonafide, rank cards, QR verification |
| Scholarship & aid | `e-04-scholarship-financial-aid.md` | Merit, SC/ST/EWS subsidy, govt schemes |
| Subscription management | `a-03-subscription-plans.md` | Free → Premium, institution-gifted, renewal |

### Week 20: Parent Portal & Privacy

| Task | Page Spec | Details |
|---|---|---|
| Parent portal (all divisions) | Group 8 all specs | Onboarding, academic monitoring, fees, communication |
| Student privacy & consent | `a-05-data-privacy-consent.md` | Parent access levels, cross-platform sharing, DPDP |
| Progress reports | `b-05-progress-reports.md` | Auto-generated monthly, institution template, PDF |
| Settings & preferences | `a-04-settings-preferences.md` | Notifications, theme, accessibility, sessions |
| Student profile | `a-02-student-profile.md` | Unified identity, institution linking, age transitions |

**Phase 4 Deliverable:** Student + Parent portals live. 5cr students can register, test, learn, pay.

---

## PHASE 5 — Scale & Optimize (Weeks 21–24)

**Outcome:** Production-ready for 74,000 concurrent exam submissions.

### Week 21: Cloudflare Edge Layer

| Task | Details |
|---|---|
| Cloudflare R2 setup | Questions, results, certificates, notes, videos stored in R2 |
| CDN caching strategy | Cache-Control headers, edge caching rules, cache purge API |
| Cloudflare Workers | Edge compute for question decryption validation, rate limiting |
| WAF rules | DDoS protection, bot detection, geo-blocking (India-only for exams) |
| DNS & SSL | All subdomains: *.schools.eduforge.in, ssc.eduforge.in, etc. |

### Week 22: AWS Production Infrastructure

| Task | Details |
|---|---|
| RDS PostgreSQL 16 Multi-AZ | db.t4g.medium → db.r6g.large scaling path, read replicas |
| Lambda deployment | SAM/CDK, cold start optimization, provisioned concurrency for exam |
| ECS Fargate | Django portal, 2× tasks minimum, auto-scaling to 8× |
| SQS queues | Exam scoring, notification dispatch, rank computation, report generation |
| EventBridge | Nightly cleanup (expired OTPs), rank recalculation, report scheduling |

### Week 23: Performance & Load Testing

| Task | Details |
|---|---|
| Locust load testing | 74,000 concurrent exam submissions simulation |
| Database query optimization | `EXPLAIN ANALYZE` on every critical query, index tuning |
| Connection pooling | PgBouncer for Lambda → RDS connection management |
| CDN cache hit ratio | Target 99%+ cache hit ratio for static content |
| Monitoring | CloudWatch dashboards, Sentry error tracking, custom metrics |

### Week 24: Security & Compliance

| Task | Module Spec | Details |
|---|---|---|
| Security hardening | `43-legal-data-compliance` | JWT rotation, KMS encryption, WAF tuning |
| DPDP Act compliance | `42-dpdpa-audit-log` | Consent log, data deletion pipeline, DPO dashboard |
| POCSO compliance | `41-pocso-compliance` | BGV tracking, mandatory reporting |
| CERT-In readiness | `43-legal-data-compliance` | 6-hour breach reporting, incident response plan |
| Penetration testing | — | OWASP top 10, IDOR prevention, rate limiting verification |

**Phase 5 Deliverable:** Production-ready. 74K concurrent. Compliant. Monitored.

---

## PHASE 6 — Mobile & Marketplace (Weeks 25–30)

**Outcome:** Flutter app live + B2B content marketplace + TSP white-label.

### Weeks 25–26: Flutter Mobile App

| Task | Details |
|---|---|
| Flutter project setup | iOS + Android, dark theme matching web |
| Auth flow | OTP login, biometric (fingerprint/face), JWT storage in Hive AES-256 |
| Student dashboard | Home, performance, test catalogue, notes, videos |
| Exam interface | Offline-capable, IndexedDB equivalent (Hive), auto-sync |
| Push notifications | FCM integration, notification preferences |

### Weeks 27–28: B2B & TSP Portals

| Task | Page Specs | Details |
|---|---|---|
| Content partner portal | Group 9 all specs | Partner registration, content authoring, revenue dashboard |
| Content marketplace | `51-b2b-api-partner-portal` | Question licensing, revenue sharing (₹0.02/student/question) |
| TSP white-label portal | Group 7 all specs | Coaching centres create branded test-series platforms |
| White-label customization | `52-white-label-tsp-portal` | Custom domain, branding, student portal |
| API partner portal | `51-b2b-api-partner-portal` | REST API access for institutional integrations |

### Weeks 29–30: Platform Admin & Analytics

| Task | Page Specs | Details |
|---|---|---|
| Platform admin portal | Group 1 all specs | All 15 divisions, exec dashboard, tenant management |
| Analytics service (FastAPI) | `53-platform-analytics-reports` | Platform MIS, revenue reports, usage analytics |
| Feature flags | `54-platform-settings-feature-flags` | Gradual rollout, A/B testing, kill switches |
| Incident management | `55-incident-management-sla` | P0-P3 incidents, war room, SLA tracking |
| Platform billing | `56-platform-billing-gst` | Institution invoicing, GST, Razorpay settlements |

**Phase 6 Deliverable:** Complete platform. Mobile app. Marketplace. Full admin.

---

## Infrastructure Cost Projections

| Phase | Students | Database | Compute | Cloudflare | Total/Month |
|---|---|---|---|---|---|
| Phase 1–2 (Dev) | 0–1K | db.t4g.micro (₹2,500) | 1× Fargate (₹3,000) | Free plan | ~₹8,000 |
| Phase 3 (Beta) | 1K–50K | db.t4g.medium (₹4,500) | 2× Fargate + Lambda | Pro (₹1,500) | ~₹25,000 |
| Phase 4 (Launch) | 50K–2L | db.t4g.large + replica | 4× Fargate + Lambda | Pro | ~₹55,000 |
| Phase 5 (Scale) | 2L–10L | db.r6g.large + 2 replicas | 8× Fargate + Lambda | Business | ~₹1,50,000 |
| Phase 6 (5cr) | 10L–5cr | Aurora Serverless v2 | Auto-scale | Enterprise | ~₹3,00,000+ |

**At 5 crore students: ₹3,00,000/month ÷ 5,00,00,000 students = ₹0.72/student/year** ✅

---

## Tech Stack Decision Matrix

| Layer | Choice | Why Not Alternatives |
|---|---|---|
| Portal rendering | Django + HTMX | Next.js = over-engineered for SSR. HTMX = zero JS bundle, fast on ₹8K phones |
| API services | FastAPI (Python) | Express/Go = team knows Python. FastAPI = async, auto-docs, type hints |
| Database | PostgreSQL 16 | MongoDB = no JOINs for analytics. MySQL = weaker JSON support |
| Cache | Cloudflare CDN + Memcached | Redis = ₹16,800/year wasted. CDN handles 99% of reads |
| Queue | AWS SQS | RabbitMQ = self-managed. SQS = zero ops, pay-per-message |
| File storage | Cloudflare R2 | S3 = ₹56L/year egress at scale. R2 = ₹0 egress |
| CDN | Cloudflare | CloudFront = 8 India PoPs. Cloudflare = 22 India PoPs, free tier |
| Payments | Razorpay | Stripe = not strong in India UPI. Razorpay = 62% UPI market |
| Mobile | Flutter | React Native = slower animations. Flutter = single codebase, Hive encryption |
| Notifications | WhatsApp + SMS + FCM | Email-only = 12% open rate in India. WhatsApp = 82% open rate |

---

## Development Priorities — What to Build First

```
PRIORITY 0 (Week 1): Can a human log in?
  identity service → OTP → JWT → Django login → home page

PRIORITY 1 (Weeks 2–4): Can an institution exist?
  multi-tenancy → institution model → RBAC → onboarding wizard → students enrolled

PRIORITY 2 (Weeks 5–10): Can an institution operate daily?
  attendance → fees → timetable → notifications → compliance

PRIORITY 3 (Weeks 11–15): Can students take exams?
  question bank → exam engine → IndexedDB → results → leaderboard

PRIORITY 4 (Weeks 16–20): Can students learn and grow?
  student dashboard → analytics → AI study plan → video library → payments

PRIORITY 5 (Weeks 21–24): Can it handle 5 crore students?
  Cloudflare edge → AWS prod → load testing → security → monitoring

PRIORITY 6 (Weeks 25–30): Can it make money?
  content marketplace → TSP white-label → platform billing → mobile app
```

---

## Key Architectural Decisions (Non-Negotiable)

| # | Decision | Reason |
|---|---|---|
| 1 | **No Redis** | PostgreSQL + Cloudflare CDN handles everything. Saves ₹16,800/year and one more service to manage. |
| 2 | **IndexedDB exam engine** | 2 Lambda calls per exam vs 200. At 74K concurrent, this is the difference between ₹300/day and ₹30,000/day. |
| 3 | **Cloudflare R2 over S3** | Zero egress cost. At 5cr students reading questions/results/notes, S3 egress alone = ₹56L/year. |
| 4 | **Django HTMX over React** | Zero JS bundle size. HTMX partial renders are faster on ₹8K Android phones than React hydration. |
| 5 | **Schema-per-service** | One PostgreSQL cluster, 7 schemas. Cross-schema JOINs for analytics. Row-level security for isolation. |
| 6 | **Stateless JWT** | No network call to validate. Every Lambda invocation saves 1 round-trip to a session store. |
| 7 | **SQS for async** | Exam scoring, notifications, rank computation — all async via SQS. Zero ops. Pay per message. |
| 8 | **Cloudflare Workers** | Edge compute for rate limiting, bot detection, and serving cached results. Zero cold start. |

---

## Git Strategy

```
main                    ← production (always deployable)
├── develop             ← integration branch
│   ├── feature/phase-1-auth          ← Phase 1 work
│   ├── feature/phase-2-institution   ← Phase 2 work
│   ├── feature/phase-3-exam-engine   ← Phase 3 work
│   └── ...
├── staging             ← pre-production testing
└── hotfix/*            ← emergency production fixes
```

Every feature branch → PR → review → merge to develop → staging → main.

---

## Testing Strategy

| Level | Tool | Coverage Target | When |
|---|---|---|---|
| Unit | pytest | 80%+ | Every commit |
| Integration | pytest + TestClient | API contracts | Every PR |
| E2E | Playwright | Critical user journeys | Nightly |
| Load | Locust | 74K concurrent | Before Phase 5 deploy |
| Security | OWASP ZAP + manual | OWASP Top 10 | Before launch |
| Accessibility | axe-core | WCAG 2.1 AA | Before launch |

---

## Monitoring & Observability

| Layer | Tool | What It Watches |
|---|---|---|
| Application errors | Sentry | Python exceptions, JS errors, breadcrumbs |
| Infrastructure | CloudWatch | Lambda duration/errors, RDS CPU/connections, SQS depth |
| Uptime | Cloudflare Health Checks | All 7 service endpoints, every 60s |
| Performance | Cloudflare Analytics | CDN hit ratio, TTFB, bandwidth |
| Business metrics | Custom dashboard | DAU, exams/day, revenue, churn |
| Alerting | PagerDuty / Slack | P0: 5 min, P1: 30 min, P2: 4 hrs |

---

*Last updated: 2026-04-01 · EduForge Development Plan v1.0*
