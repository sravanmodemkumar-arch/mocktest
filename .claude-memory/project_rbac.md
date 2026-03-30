---
name: EduForge RBAC — Roles & Permissions Summary
description: 11 role groups, 87 distinct roles, 3-dimension permission model, and key role rules for EduForge
type: project
---

EduForge has 87 distinct roles across 11 groups, defined in Module 03 and docs/roles.md.

## 11 Role Groups
1. Platform Admin (EduForge employees) — 76 roles across 14 divisions
2. Institution Group Admin
3. School (Principal, VP, HOD, Class Teacher, Subject Teacher, Accountant, etc.)
4. College (Principal, Dean, HOD, Professor, Lab Incharge, etc.)
5. Coaching (Owner, Director, Academic Head, Batch Coordinator, Faculty, etc.)
6. Exam Domain (content creators, exam admins, domain managers)
7. TSP — Test Series Provider (white-label test series publishers)
8. Parents (12 parent types, access levels P0–P5)
9. B2B API Partners (API key only, no UI login)
10. Students
11. Alumni (database record only — no login, no portal access)

## 3-Dimension Permission Model
Every permission = Action × Module × Scope (all three must be satisfied).
- Action: CREATE / READ / UPDATE / DELETE / APPROVE / PUBLISH / EXPORT
- Module: which EduForge module (attendance, fees, exams, etc.)
- Scope: OWN / SECTION / CLASS / BRANCH / GROUP / ALL_TENANTS

## System Access Levels (Platform staff)
- Level 0 = none
- Level 1 = read-only
- Level 2 = content writes
- Level 3 = tenant management (PM/QA)
- Level 4 = engineering/infra writes
- Level 5 = Platform Admin — unrestricted, all actions 2FA + audit-logged

## Key Rules
- No user can assign or modify a role at or above their own level
- All role assignments generate immutable audit log entries
- EduForge retains control over base permission primitives at all times
- Alumni = no login, no access — record only
- Parents: 12 types (Father, Mother, Guardian, Grandparent, Elder Sibling, Court-Appointed, Adoptive, Foster, Emergency Contact, NRI, Divorced-Custody, Divorced-Non-Custody)
- Institution onboarding: EduForge team creates all tenants (no self-signup)
