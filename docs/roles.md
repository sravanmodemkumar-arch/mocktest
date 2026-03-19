# EduForge — Roles & Permissions

Total: **87 distinct roles** across 6 groups.

---

## Group 1 — Platform Level (32 roles)

> These are EduForge company employees — not institution staff.
> Divided into 4 functional divisions.

### Division A — Executive & Ownership (4 roles)

| # | Role | What They Control |
|---|---|---|
| 1 | Platform Owner / CEO | Full access — all data, all tenants, billing, strategy |
| 2 | Platform CTO | Technical infrastructure, architecture decisions |
| 3 | Platform COO | Day-to-day operations, SLAs, team management |
| 4 | Platform CFO | Revenue, invoicing, Razorpay settlements, GST filings |

### Division B — Technical Operations (10 roles)

| # | Role | What They Control |
|---|---|---|
| 5 | Platform Admin | All tenant management, user provisioning, system config |
| 6 | DevOps Engineer | AWS Lambda, ECS, RDS, deployments, CI/CD |
| 7 | Database Admin | PostgreSQL schemas, backups, migrations, query tuning |
| 8 | Security Admin | JWT keys, KMS, WAF rules, breach response |
| 9 | API Gateway Admin | Rate limits, routing rules, throttling per tenant |
| 10 | Cloudflare Admin | CDN rules, R2 buckets, WAF policies, DNS |
| 11 | Monitoring Engineer | CloudWatch dashboards, Sentry, alert rules |
| 12 | L1 Support Engineer | First response — login issues, password reset |
| 13 | L2 Support Engineer | Bug investigation, DB queries, log analysis |
| 14 | L3 Support Engineer | Code-level fix, hotfixes, escalation owner |

### Division C — Content & Academics (10 roles)

| # | Role | What They Control |
|---|---|---|
| 15 | Content Director | All MCQ bank, notes, video strategy across all exams |
| 16 | SME — Mathematics | Creates/reviews Maths MCQs (SSC, RRB, Board) |
| 17 | SME — Science | Physics, Chemistry, Biology questions |
| 18 | SME — English | Grammar, comprehension, vocabulary |
| 19 | SME — General Knowledge | Current affairs, static GK, polity, history |
| 20 | SME — Reasoning | Verbal + non-verbal reasoning |
| 21 | Question Reviewer | Reviews AI-generated + SME-written MCQs for quality |
| 22 | Question Approver | Final publish authority — no one bypasses this |
| 23 | Notes Editor | Structures and formats faculty-uploaded notes |
| 24 | Video Curator | Maps YouTube videos to subjects/topics/exams |

### Division D — Business & Compliance (8 roles)

| # | Role | What They Control |
|---|---|---|
| 25 | B2B Sales Manager | Institution onboarding pipeline, pricing strategy |
| 26 | B2B Sales Executive | Individual school/college/coaching acquisition |
| 27 | Account Manager | Existing institution relationships, renewal, upsell |
| 28 | Partnership Manager | State board tie-ups, coaching chain deals |
| 29 | Billing Admin | Subscription management, invoice generation, refunds |
| 30 | Legal / Compliance Officer | DPDP 2023, POCSO, GST filings, data residency |
| 31 | Analytics Manager | Platform-wide MIS — usage, revenue, exam trends |
| 32 | Data Analyst | Institution reports, rank trends, dropout signals |

---

## Group 2 — Institution Group Level (7 roles)

| Role | Scope |
|---|---|
| Group Chairman | All colleges/schools in group |
| Group CEO / Director | Operations across all branches |
| Group Academic Director | Curriculum, exams, results |
| Group Finance Director | Fees, billing, audits |
| Group IT Admin | All portals in group |
| Group HR Manager | Staff across branches |
| Group Audit Officer | Reports, MIS, compliance |

---

## Group 3 — School Roles (31 roles)

### Admin Staff (8 roles)

| Role | Key Permissions |
|---|---|
| School Owner / Chairman | Full school access |
| Principal | Academic + admin |
| Vice Principal | Academic oversight |
| Academic Director | Syllabus, exams |
| Exam Controller | Exams, results, ranks |
| Admission Coordinator | Enrolment, TC |
| Accountant / Finance | Fee collection, reports |
| Administrative Officer | General management |

### Teaching Staff (8 roles)

| Role | Key Permissions |
|---|---|
| HOD | Dept. teachers, syllabus |
| Senior Teacher | Classes, marks, attendance |
| Class Teacher | Attendance, behaviour, welfare |
| Subject Teacher | Lesson plans, marks |
| Lab Instructor | Practical schedules |
| Sports Coach | Physical, sports records |
| Librarian | Books, library records |
| Counsellor | Student welfare events |

### Support Staff (4 roles)

| Role | Key Permissions |
|---|---|
| Hostel Warden | Hosteler management |
| Hostel Matron | Daily welfare check |
| Transport Coordinator | Routes, vehicles |
| Security Staff | Gate entry logs |

### Student Types — School (9 roles)

| Type | Description |
|---|---|
| Day Scholar — Regular | Standard day student |
| Day Scholar — Scholarship | Fee concession tracking |
| Day Scholar — RTE | Right to Education quota |
| Hosteler — AC | Premium hostel |
| Hosteler — Non-AC | Standard hostel |
| Hosteler — Scholarship | Subsidised hostel |
| Special Needs | IEP tracking, welfare |
| NRI / Foreign National | Separate fee structure |
| TC Received | Transfer certificate in |

### Parent / Guardian Types — School (5 roles)

| Type | Access Level |
|---|---|
| Father | Full parent portal |
| Mother | Full parent portal |
| Guardian | Full parent portal |
| Emergency Contact | View only, notifications |
| Court-appointed Guardian | Restricted, POCSO-aware |

---

## Group 4 — College Roles (20 roles)

### Admin Staff (8 roles)

| Role |
|---|
| College Principal |
| Vice Principal |
| Dean of Academics |
| Examination Branch Head |
| Admission Officer |
| Student Affairs Officer |
| Placement Officer |
| Finance Officer |

### Faculty (6 roles)

| Role |
|---|
| Head of Department |
| Senior Lecturer |
| Lecturer |
| Guest Lecturer |
| Lab Instructor |
| NSS / NCC / Sports Coordinator |

### Student Types — College (6 roles)

| Type |
|---|
| Regular Student |
| Lateral Entry |
| Scholarship — Merit |
| Scholarship — Government |
| Hosteler |
| Fee Defaulter (restricted access) |

---

## Group 5 — Coaching Centre Roles (16 roles)

### Management (6 roles)

| Role |
|---|
| Institute Owner / Director |
| Branch Manager |
| Academic Coordinator |
| Sales / Admission Counsellor |
| Fee Collection Staff |
| Back Office / Data Entry |

### Faculty (4 roles)

| Role |
|---|
| Senior Faculty |
| Faculty |
| Demo / Guest Faculty |
| Online Faculty (recorded content) |

### Student Types — Coaching (6 roles)

| Type | Description |
|---|---|
| Regular Batch | Full-time classroom |
| Weekend Batch | Saturday/Sunday only |
| Online Batch | Live classes only |
| Correspondence | Material + tests only |
| Crash Course | Short duration |
| B2B (via institution tie-up) | Billed to institution |

---

## Group 6 — Online Mock Test Domain Roles (8 roles)

| Role | Description |
|---|---|
| Domain Admin | Manages one exam domain (SSC, RRB, etc.) |
| Content Creator | Writes and uploads MCQs |
| Question Reviewer | Reviews quality before publish |
| Question Approver | Final approval + publish |
| Student — Free | Limited tests/month |
| Student — Premium | Unlimited tests |
| Student — B2B | Via coaching institution subscription |
| Topper / Ranker | Special badge, leaderboard visibility |

---

## Permission Matrix

| Permission | Platform Admin | Group Director | Principal | HOD | Teacher | Student | Parent |
|---|---|---|---|---|---|---|---|
| View all tenants | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage institution | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage staff | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage students | ✅ | ✅ | ✅ | ❌ | partial | ❌ | ❌ |
| Take exam | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| View own child | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Upload notes | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Create MCQs | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Approve MCQs | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ✅ | ✅ | partial | own only | own child |
| Manage billing | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage hostel | ✅ | ✅ | ✅ | ❌ | warden only | ❌ | ❌ |
| View results | ✅ | ✅ | ✅ | ✅ | own class | own only | own child |
