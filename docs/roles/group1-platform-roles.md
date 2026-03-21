# EduForge — Group 1: Platform Level Roles
> EduForge company employees only. Not institution staff.
> Total: 99 roles across 15 divisions.

---

## Scale Context

| Segment | Count | Students |
|---|---|---|
| Schools | 1,000 | ~12,00,000 |
| Colleges | 800 | ~4,80,000 |
| Coaching Centres | 100 | ~10,00,000 |
| Institution Groups | 150 | (child institutions counted above) |
| **Total** | **2,050 institutions** | **~24L–76L (2.4M–7.6M)** |

Peak concurrent exam load: **74,000 simultaneous submissions**

---

## Platform Modules → Role Ownership

| Module | Owned By Division |
|---|---|
| Tenant onboarding/offboarding | Sales + Support + Engineering |
| User management across all tenants | Platform Admin + L2/L3 Support |
| MCQ Bank (create, review, publish) | Content + SMEs |
| Notes (upload, structure, publish) | Content + Notes Editor |
| Video Library (YouTube mapping) | Video & Learning |
| Exam Engine (live tests, timing) | Exam Operations |
| Exam Day Monitoring (74K concurrent) | Exam Operations + DevOps |
| Results & Rank Computation | Results Coordinator + Data |
| BGV for all institution staff | BGV Division |
| AI-based MCQ Generation | AI/ML Engineer + AI Gen Manager |
| WhatsApp/SMS Notifications | Notification Manager + Exam Ops |
| Billing & Subscriptions | Finance + Billing Admin |
| Analytics & MIS | Data & Analytics |
| DPDP / POCSO Compliance | Legal & Compliance |
| Infrastructure (Lambda, RDS, CDN) | Engineering + DevOps |
| Incident Response (Exam Day) | Incident Manager + SRE |

---

## System Access Levels

| Level | Label | Can Do |
|---|---|---|
| 0 | No Platform Access | Internal tools only (HR, Marketing, Admin) |
| 1 | Read Only | Dashboards, reports, audit logs — no edits |
| 2 | Content Manager | Create, edit, approve content (MCQ, notes, videos) |
| 3 | Tenant Manager | Manage institutions, users, exams, subscriptions |
| 4 | Infrastructure | System config, DB access, deployments, security keys |
| 5 | Super Admin | Unrestricted — all data, all tenants, all modules |

---

## Division A — Executive Leadership (4 roles)

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 1 | Platform Owner / CEO | 5 | Everything | — |
| 2 | Platform CTO | 5 | Tech architecture, infra, security, deployments | Commercial deals |
| 3 | Platform COO | 3 | Operations, SLAs, team mgmt, support escalations | Infra config, billing |
| 4 | Platform CFO | 1 | Revenue reports, GST, Razorpay settlements | Any data edit |

---

## Division B — Product & Design (5 roles)

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 5 | Product Manager — Platform | 3 | Feature flags, plan config, release notes | Infra, billing |
| 6 | Product Manager — Exam Domains | 3 | SSC/RRB/Board domain config, test series structure | Content publish |
| 7 | Product Manager — Institution Portal | 3 | School/college/coaching portal features, role config | Infra |
| 8 | UI/UX Designer | 1 | Read-only — design review, no data changes | All writes |
| 9 | QA Engineer | 3 | Test all modules, create test tenants, validate flows | Production data edit |

---

## Division C — Engineering (8 roles)

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 10 | Platform Admin | 5 | All tenant mgmt, user provisioning, system config | Nothing blocked |
| 11 | Backend Engineer | 4 | API config, service deployments, DB migrations | Billing config |
| 12 | Frontend Engineer | 4 | HTMX templates, CDN cache invalidation, R2 assets | DB access |
| 13 | Mobile Engineer — Flutter | 4 | App builds, Hive encryption, FCM config, app store | DB access |
| 14 | DevOps / SRE Engineer | 4 | AWS Lambda, ECS, RDS, CI/CD, auto-scaling, rollbacks | Content/billing |
| 15 | Database Administrator | 4 | PostgreSQL all 7 schemas, backups, migrations, tuning | Business config |
| 16 | Security Engineer | 4 | JWT secret rotation, KMS, WAF rules, CERT-In reports | Content, billing |
| 17 | AI / ML Engineer | 4 | MCQ generation pipeline, model prompts, AI API config | Content approval |

---

## Division D — Content & Academics (13 roles)

> Each SME owns their subject end-to-end.
> One wrong question at 74K concurrent = mass rank distortion.

| # | Role | Level | Subject Scope | Can Publish? |
|---|---|---|---|---|
| 18 | Content Director | 2 | All subjects, all exam types | Yes — after Approver |
| 19 | SME — Mathematics | 2 | Arithmetic, Algebra, Geometry, DI, Calculus | No — needs Approver |
| 20 | SME — Physics | 2 | Mechanics, Optics, Electricity, Modern Physics | No |
| 21 | SME — Chemistry | 2 | Organic, Inorganic, Physical Chemistry | No |
| 22 | SME — Biology | 2 | Botany, Zoology, Human Physiology | No |
| 23 | SME — English | 2 | Grammar, RC, Vocabulary, Error Spotting | No |
| 24 | SME — General Knowledge | 2 | Current Affairs, Polity, History, Geography, Economy | No |
| 25 | SME — Reasoning | 2 | Verbal, Non-Verbal, Logical, Analytical | No |
| 26 | SME — Computer Science | 2 | IT Fundamentals, Programming, Digital Literacy | No |
| 27 | SME — Regional Language | 2 | Telugu, Hindi, Urdu for State Board exams | No |
| 28 | Question Reviewer | 2 | All subjects — quality check, accuracy, language | No — sends back or forward |
| 29 | Question Approver | 2 | All subjects — **final publish gate** | **Yes — only role that publishes** |
| 30 | Notes Editor | 2 | Structures, formats, tags all faculty-uploaded notes | Yes — for notes only |

---

## Division E — Video & Learning (11 roles)

> Phase 1 roles (31–33) handle YouTube curation and channel management.
> Phase 2 roles (82–89) form the in-house video production pipeline.
> Every MCQ question in the bank (Div D) can have a corresponding explanatory video produced by this division.

**Curation & Channel (Phase 1)**

| # | Role | Level | Owns |
|---|---|---|---|
| 31 | Video Curator | 2 | Map YouTube videos → subject → topic → exam type |
| 32 | Playlist Manager | 2 | Create structured learning paths per syllabus/exam |
| 33 | YouTube Channel Manager | 2 | EduForge official channel — uploads, playlists, metadata |

**Production Pipeline (Phase 2)**

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 82 | Content Producer — Video | 2 | End-to-end production pipeline mgmt; commission briefs; SLA ownership; final publish | Cannot approve scripts (Reviewer 84 does that) |
| 83 | Video Scriptwriter | 2 | Author scripts from MCQ briefs; incorporate SME-provided explanation text | Cannot approve own scripts; cannot upload animation/edit assets |
| 84 | Script Reviewer | 2 | Review scripts for factual accuracy, pedagogy, language quality; approve or return | Cannot author scripts; cannot publish |
| 85 | Motion Graphics / Animation Artist | 2 | Create animated explainer videos from approved scripts; upload animation exports | Cannot approve own work; cannot publish to YouTube |
| 86 | Graphics Designer — Video | 2 | Thumbnails, lower-thirds, chapter cards, intro/outro motion assets | Cannot upload animation or final edit files |
| 87 | Video Editor | 2 | Assemble final video from animation + VO + graphics; colour grade; export at spec | Cannot upload subtitle files; cannot publish |
| 88 | Subtitle & Localisation Editor | 2 | Add subtitles (EN + regional languages: HI, TE, UR); verify timing sync | Cannot approve final video; cannot upload animation/edit assets |
| 89 | Video Quality Reviewer | 2 | Final QA gate — accuracy check, A/V quality, subtitle sync, spec compliance; pass or fail | Cannot publish directly; PASS routes to Publish Queue for Producer (82) |

---

## Division F — Exam Day Operations (5 roles)

> Most critical division on exam day.
> 74,000 students submit simultaneously — this team runs the war room.

| # | Role | Level | Owns | Critical Action |
|---|---|---|---|---|
| 34 | Exam Operations Manager | 3 | Monitor all live exams, pause/extend duration if needed | Pause exam for all tenants |
| 35 | Exam Support Executive | 3 | Handle student issues during live exam window | Override stuck session |
| 36 | Results Coordinator | 3 | Trigger rank computation, review before publish | Approve result publish |
| 37 | Notification Manager | 3 | WhatsApp/SMS/Email templates, result broadcasts, OTP routing | Send bulk 74K notifications |
| 38 | Incident Manager — Exam Day | 4 | Escalate infra issues to DevOps, coordinate war room | Emergency Lambda scale-up |

---

## Division G — Background Verification (4 roles)

> POCSO Act 2012 — mandatory BGV for all staff with minor access.
> Any unverified staff found = legal liability for EduForge.
> 2,050 institutions · ~28,000 staff requiring BGV · NCPCR mandatory reporting within 24h.

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 39 | BGV Manager | 3 | BGV policy, vendor onboarding & config, API key rotation, escalation to institutions, institution compliance tracker, compliance report export, POCSO oversight | Cannot process individual verifications (Executive scope) |
| 40 | BGV Executive | 3 | Process assigned BGV requests, document review & upload, vendor submission, result recording, notes | Cannot approve FLAGGED results; cannot view institution-level compliance; cannot configure vendors |
| 41 | POCSO Compliance Officer | 1 | Read-only audit of BGV coverage across all institutions; NCPCR mandatory annual report generation | All writes blocked — cannot escalate, add staff, log communications, or approve any decision |
| 92 | BGV Operations Supervisor | 3 | Approve FLAGGED/INCONCLUSIVE verification decisions; queue assignment across executives; SLA monitoring; bulk vendor submission | Cannot configure vendors or system settings; cannot self-approve decisions submitted by themselves |

---

## Division H — Data & Analytics (5 roles)

> All analytics data lives in a separate pre-aggregated analytics schema.
> Analytics pages always read from pre-computed tables — never live cross-tenant scans.
> 7 Celery aggregation tasks run nightly across 2,050 tenant schemas.

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 42 | Analytics Manager | 1 | Platform-wide MIS; anomaly alerts; institution churn reporting; report template approval and publish; AI cost oversight | No data edits; cannot trigger pipeline runs; cannot create AI batches |
| 43 | Data Engineer | 4 | Analytics schema DDL; Celery aggregation pipeline operations; manual re-runs; data freshness monitoring; SQL explorer; warehouse management | Cannot approve AI MCQs; cannot approve report templates; no business configuration |
| 44 | Data Analyst | 1 | Student performance analysis; institution health investigation; question quality flagging; dropout signal analysis; export requests | No data edits; no pipeline management; no AI pipeline access; cannot send CSM notifications |
| 45 | AI Generation Manager | 3 | AI MCQ batch creation; model config and prompt management; MCQ quality review before Division D; cost tracking | Cannot approve MCQs for publish (Division D Approver only); cannot modify existing question bank; cannot trigger analytics pipelines |
| 46 | Report Designer | 1 | Institution-facing MIS report template design; section configuration; preview and testing; delivery scheduling | No data edits; cannot publish templates (Analytics Manager approval required); cannot trigger manual report deliveries |

---

## Division I — Customer Support (7 roles)

| # | Role | Level | Handles | Response Time |
|---|---|---|---|---|
| 47 | Support Manager | 3 | Team management, SLA tracking, escalation rules, cross-division coordination | — |
| 48 | L1 Support Executive | 3 | Login, OTP, basic navigation, student and institution admin queries | < 2 hours |
| 49 | L2 Support Engineer | 3 | Bug investigation, log analysis, DB read queries | < 8 hours |
| 50 | L3 Support Engineer | 4 | Code-level fixes, DB writes, hotfixes, rollbacks | < 24 hours |
| 51 | Onboarding Specialist | 3 | New institution onboarding pipeline, portal setup, admin training coordination | Per onboarding |
| 52 | Training Coordinator | 2 | Create training docs, KB articles (needs approval), conduct training sessions | Scheduled |
| 90 | Support Quality Lead | 3 | Random-sample ticket quality audits, CSAT trend monitoring, L1 agent coaching, KB gap identification, weekly quality report | Ongoing |

---

## Division J — Customer Success (6 roles)

> At 2,050 institutions and ₹ARR across school/college/coaching segments, CS owns retention, expansion, and escalation resolution.
> Health scores computed nightly from exam frequency, engagement depth, support burden, payment health, and relationship recency.

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 53 | Customer Success Manager | 3 | Institution health score, retention risk, renewal pipeline, playbook governance, NPS programme, portfolio strategy | Billing config, infra config |
| 54 | Account Manager | 3 | Existing institution relationship, upsell, expansion seats, renewal co-ownership | Cannot send bulk surveys; cannot approve playbook templates |
| 55 | Escalation Manager | 3 | Critical institution complaints, SLA breach handling, cross-division war-room coordination for account-threatening incidents | Cannot approve content; cannot modify billing |
| 56 | Renewal Executive | 1 | Track subscription expiry, send renewal reminders, update renewal stage to COMMITTED | Cannot close/win renewals (AM or CSM must confirm); no data writes outside renewal module |
| 93 | Customer Success Analyst | 1 | Health score model maintenance, churn signal analysis, portfolio cohort analytics, NPS/CSAT data analysis, weekly CS performance data pack | No customer-facing comms; no playbook execution; no billing access; no notifications |
| 94 | Implementation Success Manager | 3 | First-90-day post-onboarding success journey (receives handoff from Division I Onboarding Specialist #51), time-to-value tracking, go-live readiness verification, first EBR facilitation | Billing config; renewal ownership hands off to Account Manager at day 90; no L2/L3 support queue access |

---

## Division K — Sales & Business Development (10 roles)

> Pipeline covers 2,050 institutions across schools, colleges, coaching centres, and groups.
> Channel partners and government contracts add multi-institution deal velocity.
> Avg sales cycle: 3–8 weeks (schools), 8–24 weeks (govt/groups).

| # | Role | Level | Territory / Scope | Can Do | Cannot Do |
|---|---|---|---|---|---|
| 57 | B2B Sales Manager | 3 | All segments — pricing approvals, deal sign-off | View all pipeline; approve pricing exceptions; set quotas; assign territories; all reports | Billing config; infra config |
| 58 | Sales Executive — Schools | 3 | 1,000 schools — day scholar + hosteler institutions | Own leads — create, log activities, advance stages, schedule demos | Access other execs' leads; approve pricing; create demo tenants |
| 59 | Sales Executive — Colleges | 3 | 800 intermediate colleges | Same as #58 | Same as #58 |
| 60 | Sales Executive — Coaching | 3 | 100 coaching centres (5K–15K members each) | Same as #58 | Same as #58 |
| 61 | Partnership Manager | 3 | State board govt contracts, coaching chain MoUs | Manage all partnerships; upload MoUs; track renewals; log partner activities | Demo tenant management; channel partner commissions; billing |
| 62 | Demo Manager | 3 | All segments — free trial tenant lifecycle | Create/reset/extend/deactivate demo tenants; link to leads; seed data; generate access links | Edit production tenants; access billing; approve deals |
| 63 | Channel Partner Manager | 1 | Reseller/partner network — commission tracking | View partner performance; log partner interactions; commission reports | Commission approval (Sales Manager does that); onboard without Manager approval |
| 95 | Sales Operations Analyst | 1 | Platform-wide — CRM data quality, pipeline reporting | Read all pipeline; quota reports; win/loss analysis; territory map view; export reports | Any pipeline edits; no customer-facing actions; no territory reassignment |
| 96 | Pre-Sales / Solutions Engineer | 3 | Large deals (>₹2L ARR) and government tenders | Technical discovery calls; RFP/tender response builder; PoC tenant deployment; document feature gaps for product team | Cannot close deals (Sales Exec owns); cannot approve pricing; no commission management |
| 97 | Inside Sales Executive | 3 | Inbound queue — website leads, marketing-sourced, trial activations | Manage inbound leads; qualify and assign; first contact calls; schedule demos; move PROSPECT→CONTACTED | Cannot access outbound pipeline of other execs; no pricing approvals; no demo tenant creation |

---

## Division L — Marketing & Growth (8 roles)

> Original 5 roles (64–68) have Level 0 for the EduForge student/institution platform — they use external tools (Meta Ads, Google Search Console, YouTube Studio).
> 3 new roles added (#98, #99, #100) to complete the division.
> All 8 roles access the internal Marketing Operations portal (`/marketing/`) for campaign mgmt, content pipeline, SEO, social, brand, attribution, and reporting.

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 64 | Marketing Manager | 0 | Brand strategy; approve all content, assets, campaigns; quarterly budget allocation; full L-portal access | EduForge platform config; billing; infra; sales pipeline edits |
| 65 | SEO / Content Executive | 0 | Blog, landing pages, exam prep articles for organic traffic; keyword tracking; GSC monitoring | Approve own content; approve brand assets; paid ad config |
| 66 | Social Media Manager | 0 | YouTube, Instagram, Twitter — student community building; post scheduling; platform analytics | Performance ad budget; content publishing approval; brand asset upload |
| 67 | Performance Marketing Exec | 0 | Google Ads, Meta Ads — school/coaching decision-maker targeting; UTM config; A/B test campaigns | Content approve; brand asset upload; attribution model config |
| 68 | Brand Manager | 0 | Visual identity per domain (SSC brand ≠ School brand); asset upload, versioning, deprecation; brand compliance review | Performance ad management; content authoring; social post scheduling |
| 98 | Marketing Analyst | 1 | Attribution model config (First/Last/Linear); CAC/ROAS/CPL reporting; conversion funnel analytics; channel mix analysis; lead quality scoring; weekly data pack | No campaign edits; no content edits; no asset uploads; no customer-facing comms |
| 99 | Content Strategist | 2 | Editorial calendar CRUD; content brief creation and assignment; keyword cluster strategy; content performance review; approve content (co-gate with Marketing Manager) | Performance ad management; brand asset upload; social scheduling; no EduForge platform writes |
| 100 | Email & CRM Marketing Executive | 0 | Drip sequence creation; email template authoring; contact list management; send scheduling; open/click/bounce analytics; WhatsApp broadcast scripts | Cannot send to >10K contacts without Manager approval; no access to sales financial data; no platform config |

---

## Division M — Finance & Billing (8 roles)

> At 2,050 institutions and ₹18Cr–₹90Cr ARR, finance operations span invoice generation, Razorpay settlement reconciliation, GST compliance (SAC 9993), refund processing, and subscription tier management.
> ~2,050 invoices generated per month. Overdue rate 3–5% (~60–100 institutions). GST obligations under GSTR-1/3B/9.

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 69 | Finance Manager | 1 | Revenue P&L oversight, Razorpay reconciliation sign-off, investor reporting, refund approvals > ₹10K, write-off decisions, AR escalation resolution | Cannot edit invoices directly (must go via Billing Admin); cannot configure plan tiers (Pricing Admin) |
| 70 | Billing Admin | 3 | Invoice generation, subscription plan assignment, invoice edits, refund request creation, account suspension/reactivation, bulk invoice dispatch | Cannot approve refunds > ₹10K (Finance Manager approval required); cannot configure plan tiers (Pricing Admin owns that) |
| 71 | Accounts Receivable Exec | 1 | Outstanding dues tracking, reminder dispatch, promise-to-pay logging, payment follow-up for 0–60 day overdue accounts, AR aging report review | No invoice writes; cannot issue demand notices or suspend accounts; read-only on all financial records |
| 72 | GST / Tax Consultant | 1 | SAC 9993 compliance, CGST/SGST/IGST computation per invoice, GSTR-1/3B/9 filing, TDS 194J tracking, Razorpay TCS reconciliation | Cannot edit invoices or subscriptions; no access to pricing configuration or refund processing |
| 73 | Refund Processing Exec | 3 | Validate refund eligibility against policy, process approved refunds via Razorpay API, track Razorpay refund_id and status, handle failed refunds | Cannot approve refunds > ₹10K (Finance Manager approves first); cannot create refund requests (Billing Admin or Finance Manager creates them) |
| 74 | Pricing Admin | 3 | Subscription tier configuration (create/edit/archive plans), institution-specific custom discounts, promo code lifecycle management, pricing change history | Cannot assign plans to institutions (Billing Admin does that); cannot approve discounts > 20% (Finance Manager must approve) |
| 101 | Finance Analyst | 1 | ARR/MRR waterfall analysis (new/expansion/contraction/churn), P&L variance investigation, investor deck data preparation, cohort revenue analysis, NRR/GRR modelling, revenue forecast maintenance, segment-wise revenue attribution | No data edits anywhere; read-only across all finance modules; can export aggregated analytics only (not raw payment/invoice records) |
| 102 | Collections Executive | 3 | Outbound dunning calls for 60+ day overdue accounts, formal demand notice generation and dispatch, payment plan negotiation and structured agreement logging, suspension coordination with Billing Admin, escalation of unresolvable accounts to Finance Manager for write-off | Cannot write off invoices; cannot approve refunds; no access to subscriptions, pricing config, or GST module |

---

## Division N — Legal & Compliance (4 roles)

| # | Role | Level | Owns |
|---|---|---|---|
| 75 | Legal Officer | 1 | Institution contracts, ToS, privacy policy updates |
| 76 | Data Privacy Officer (DPO) | 1 | DPDP Act 2023, consent records, 72-hour breach notification |
| 77 | Regulatory Affairs Exec | 1 | TRAI (SMS sender ID EDUFGE), CERT-In, MeitY filings |
| 78 | POCSO Reporting Officer | 1 | Mandatory incident reporting to NCPCR, child welfare coordination |

---

## Division O — HR & Administration (3 roles)

> No platform system access.

| # | Role | Level | Owns |
|---|---|---|---|
| 79 | HR Manager | 0 | Hiring, payroll, policies — internal only |
| 80 | Recruiter | 0 | Talent acquisition only |
| 81 | Office Administrator | 0 | Facilities, vendor payments — no platform access |

> Note: Internal IT (employee laptops, GitHub, VPN) is handled by DevOps Engineer (#14).

---

## Full Role Count Summary

| Division | Roles |
|---|---|
| A — Executive Leadership | 4 |
| B — Product & Design | 5 |
| C — Engineering | 8 |
| D — Content & Academics | 13 |
| E — Video & Learning | 11 (3 Phase 1 + 8 Phase 2) |
| F — Exam Day Operations | 5 |
| G — Background Verification | 4 |
| H — Data & Analytics | 5 |
| I — Customer Support | 7 |
| J — Customer Success | 6 |
| K — Sales & Business Development | 10 (7 original + 3 new: #95, #96, #97) |
| L — Marketing & Growth | 8 (5 original + 3 new: #98, #99, #100) |
| M — Finance & Billing | 8 (6 original + 2 new: #101, #102) |
| N — Legal & Compliance | 4 |
| O — HR & Administration | 3 |
| **Total** | **101** |

---

## Headcount at Each Phase

| Phase | Students | Approx Team Size |
|---|---|---|
| Launch (Phase 1) | 0 – 50K | 15–20 people |
| Growth (Phase 2) | 50K – 2L | 30–40 people |
| Scale (Phase 3) | 2L – 10L | 60–80 people |
| Mature (Phase 4) | 10L – 25L | 100–150 people |
