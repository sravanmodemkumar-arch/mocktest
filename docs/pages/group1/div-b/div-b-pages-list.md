# Group 1 — Division B: Product & Design — Pages Reference

> **Division:** B — Product & Design
> **Roles:** Product Manager Platform · Product Manager Exam Domains · Product Manager Institution Portal · UI/UX Designer · QA Engineer
> **Base URL prefix:** `/product/`
> **Theme:** Dark (`portal_base_dark.html`)
> **Status key:** ✅ Spec done · 🔨 In progress · ⬜ Not started

---

## Scale Context (always keep in mind when designing every page)

| Dimension | Value |
|---|---|
| Schools | 1,000 · 200–5,000 students each · avg 1,000 · total ~10L |
| Colleges (Intermediate) | 800 · 150–2,000 each · avg 500 · total ~4L |
| Institution Groups | 150 · 5–50 child institutions per group |
| Coaching Centres | 100 · 5,000–15,000 members each · avg 10,000 · total ~10L |
| **Total institutions** | **2,050** |
| **Total students** | **2.4M–7.6M** |
| Peak concurrent exam load | **74,000 simultaneous submissions** |
| Exam domains | 6 (SSC · RRB · NEET · JEE · AP Board · TS Board) + IBPS/SBI/Banking |
| Active feature flags | ~120 flags in production |
| Subscription plan tiers | 4 (Starter · Standard · Professional · Enterprise) |
| New institutions/month | 30–50 onboardings |
| Test series active | ~800+ across all domains |
| Questions in bank | 2M+ |
| Mobile app installs | ~3M+ (Flutter — iOS + Android) |

---

## Division B — Role Summary

| # | Role | Level | Owns | Cannot Do |
|---|---|---|---|---|
| 5 | Product Manager — Platform | 3 | Feature flags · plan config · release notes · roadmap · A/B tests · announcements · mobile app config | Infra config · billing transactions |
| 6 | Product Manager — Exam Domains | 3 | SSC/RRB/Board domain config · exam patterns · syllabus structure · test series · domain analytics | Content publish (Division D Approver only) |
| 7 | Product Manager — Institution Portal | 3 | School/college/coaching portal features · institution role config · portal templates · onboarding workflows · notification templates | Infra |
| 8 | UI/UX Designer | 1 | Read-only: design review · component audit · design issue logging | ALL writes blocked |
| 9 | QA Engineer | 3 | Test all modules · create test tenants · validate flows · defect tracking · performance testing · automation monitoring | Production data edit |

---

## PM Platform — Pages (Role 5) · 8 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| 01 | Product Dashboard | `/product/dashboard/` | `01-product-dashboard.md` | P0 | ⬜ | Central command — release velocity, flag health, roadmap burndown, QA blockers, feature adoption KPIs, activity feed |
| 02 | Feature Flags | `/product/feature-flags/` | `02-feature-flags.md` | P0 | ⬜ | 120+ flag lifecycle: create · rollout % · per-institution overrides · kill switch · dependency graph · audit trail |
| 03 | Release Manager | `/product/releases/` | `03-release-manager.md` | P1 | ⬜ | Release pipeline: planning → staging → production · changelog editor · QA sign-off gate · rollback · deployment notes |
| 04 | Plan & Pricing Config | `/product/plan-config/` | `04-plan-config.md` | P1 | ⬜ | 4-tier plan catalog · feature entitlement matrix · add-ons · upgrade/downgrade rules · proration preview · 2FA-gated publish |
| 05 | Product Roadmap | `/product/roadmap/` | `05-product-roadmap.md` | P2 | ⬜ | Epics · features · milestones · quarter capacity · Kanban board + timeline toggle · priority scoring · stakeholder view |
| 06 | A/B Test Manager | `/product/experiments/` | `06-ab-test-manager.md` | P2 | ⬜ | Controlled experiments: variant config · rollout % · institution-type targeting · statistical significance tracker · winner declaration |
| 07 | Announcement Manager | `/product/announcements/` | `07-announcement-manager.md` | P2 | ⬜ | Product comms to 2,050 institutions: in-app banners · email digests · targeting by type/plan · schedule · delivery reports |
| 08 | Mobile App Config | `/product/mobile-config/` | `08-mobile-app-config.md` | P2 | ⬜ | Flutter app: minimum version enforcement · force update policy · iOS vs Android feature flags · FCM topic config · Hive key rotation schedule |

---

## PM Exam Domains — Pages (Role 6) · 5 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| 09 | Exam Domain Config | `/product/exam-domains/` | `09-exam-domain-config.md` | P1 | ⬜ | SSC/RRB/NEET/JEE/AP Board/TS Board + IBPS/SBI domain cards · metadata · publish/unpublish · domain-level settings |
| 10 | Syllabus Builder | `/product/syllabus/` | `10-syllabus-builder.md` | P1 | ⬜ | Drag-drop hierarchy: Subject → Chapter → Topic · coverage % against 2M+ question bank · per-domain mapping · version history |
| 11 | Test Series Manager | `/product/test-series/` | `11-test-series-manager.md` | P1 | ⬜ | Series lifecycle: create · assign exams · schedule · enrollment caps · 100K+ enrollments · progress tracking · series analytics |
| 12 | Exam Pattern Builder | `/product/exam-patterns/` | `12-exam-pattern-builder.md` | P1 | ⬜ | Section config · Q per section · marks/negative marking · time limits · normalization formulas (RRB multi-shift) · pattern versioning |
| 13 | Domain Analytics | `/product/domain-analytics/` | `13-domain-analytics.md` | P2 | ⬜ | Per-domain: enrollment trends · question coverage · test series usage · institution adoption · dropout points · competitive benchmarks |

---

## PM Institution Portal — Pages (Role 7) · 5 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| 14 | Portal Feature Config | `/product/portal-features/` | `14-portal-feature-config.md` | P1 | ⬜ | 80+ features × 4 institution types × 4 plan tiers entitlement matrix · toggle overrides · dependency warnings · audit log |
| 15 | Institution Role Config | `/product/institution-roles/` | `15-institution-role-config.md` | P2 | ⬜ | Institution-side roles (teacher/HOD/admin/principal/parent) · permission sets · role hierarchy · assignment rules per institution type |
| 16 | Portal Templates | `/product/portal-templates/` | `16-portal-templates.md` | P2 | ⬜ | Layout templates per institution type · nav order · module visibility · white-label rules · branding config · live preview |
| 17 | Onboarding Workflow | `/product/onboarding/` | `17-onboarding-workflow.md` | P2 | ⬜ | Step builder for 30–50 new institutions/month · mandatory vs skippable steps · per-institution-type flows · completion tracking |
| 18 | Notification Template Manager | `/product/notification-templates/` | `18-notification-template-manager.md` | P2 | ⬜ | Email/SMS/WhatsApp templates institutions use for student comms · variable substitution · per-plan availability · preview · A/B variant |

---

## UI/UX Designer — Pages (Role 8) · 2 pages

> All pages: Level 1 read-only. Zero write operations permitted for this role.

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| 19 | Design System | `/product/design-system/` | `19-design-system.md` | P2 | ⬜ | Component library browser · colour tokens · typography scale · spacing system · animation specs · dark/light token audit · Figma links |
| 20 | UI Review Board | `/product/ui-review/` | `20-ui-review-board.md` | P3 | ⬜ | Production design deviation log · severity triage · assign to dev · resolution tracking · screen comparison · WCAG audit results |

---

## QA Engineer — Pages (Role 9) · 6 pages

| # | Page Name | URL | File | Priority | Status | Description |
|---|---|---|---|---|---|---|
| 21 | QA Dashboard | `/product/qa/` | `21-qa-dashboard.md` | P1 | ⬜ | Coverage % · open defects by severity · test run history · module health scores · automation pass rate · release readiness gauge |
| 22 | Test Tenant Manager | `/product/test-tenants/` | `22-test-tenant-manager.md` | P1 | ⬜ | Sandbox tenant CRUD · scenario presets · data reset · config snapshots · institution-type simulations · concurrent user simulation |
| 23 | Test Case Repository | `/product/test-cases/` | `23-test-case-repository.md` | P2 | ⬜ | Test cases by module/feature/release · test plans · release checklists · execution history · traceability matrix · coverage gaps |
| 24 | Performance Test Dashboard | `/product/performance/` | `24-performance-test-dashboard.md` | P1 | ⬜ | 74K concurrent exam load scenarios · latency profiles · throughput charts · Lambda scaling graphs · pre-release pass/fail gate |
| 25 | Defect Tracker | `/product/defects/` | `25-defect-tracker.md` | P1 | ⬜ | Full defect lifecycle: Open→In Progress→In Review→Resolved→Closed · aging · severity triage · regression flags · module heatmap |
| 26 | Automation Monitor | `/product/automation/` | `26-automation-monitor.md` | P2 | ⬜ | CI/CD test run status · flaky test detection · execution time trends · GitHub Actions integration · test suite health by module |

---

## Cross-Division Shared Drawers (reused across all div-b pages)

| Drawer | Trigger | Width | Tabs | Description |
|---|---|---|---|---|
| flag-detail-drawer | Feature Flags → row click | 560px | Config · Overrides · History · Dependencies | Flag config · rollout slider · per-institution overrides · audit log |
| release-detail-drawer | Release Manager → row click | 640px | Summary · Changelog · Flags · QA Sign-off · Rollback | Full release record · QA checklist · flag inventory |
| plan-edit-drawer | Plan Config → Edit | 640px | Pricing · Features · Limits · Preview | Editable plan card · 2FA-gated save |
| domain-config-drawer | Exam Domain → card | 720px | Metadata · Patterns · Syllabus · Analytics | Domain details + pattern editor |
| test-tenant-drawer | Test Tenants → row | 560px | Config · Scenarios · Reset · Audit | Tenant settings · data reset flow |
| defect-detail-drawer | Defect Tracker → row | 560px | Details · Steps · History · Comments | Reproduce steps · status timeline |
| design-token-drawer | Design System → token | 480px | Values · Usage · Components | Token values · usage locations |
| announcement-preview-drawer | Announcement Manager | 600px | In-App · Email · SMS | Rendered preview per channel |

---

## Implementation Priority Order

```
P0 — Must have before div-b goes live
  01-product-dashboard
  02-feature-flags

P1 — Sprint 2
  03-release-manager
  04-plan-config
  09-exam-domain-config
  10-syllabus-builder
  11-test-series-manager
  12-exam-pattern-builder
  14-portal-feature-config
  21-qa-dashboard
  22-test-tenant-manager
  24-performance-test-dashboard
  25-defect-tracker

P2 — Sprint 3
  05-product-roadmap
  06-ab-test-manager
  07-announcement-manager
  08-mobile-app-config
  13-domain-analytics
  15-institution-role-config
  16-portal-templates
  17-onboarding-workflow
  18-notification-template-manager
  19-design-system
  23-test-case-repository
  26-automation-monitor

P3 — Backlog
  20-ui-review-board
```

---

*Last updated: 2026-03-20*
*Total pages: 26*
