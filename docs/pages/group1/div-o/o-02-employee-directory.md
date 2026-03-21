# O-02 — Employee Directory

**Route:** `GET /hr/employees/`
**Method:** Django `TemplateView` + HTMX part-loads; server-side pagination
**Primary roles:** HR Manager (#79), HR Business Partner (#106)
**Also sees:** Recruiter (#80) — read-only (for offer → employee conversion view); Payroll & Compliance Executive (#105) — read-only (name, designation, PF UAN, ESIC IP, bank details — payroll-relevant fields only); L&D Coordinator (#107) — read-only (name, designation, division, skills, certifications); Office Administrator (#81) — read-only (name, work location, asset assignments)

---

## Purpose

Single source of truth for all EduForge employees. At 100–150 employees across multiple cities, roles, and employment types, HR Manager and HRBP need a reliable, structured record of who works here, in what capacity, under which manager, and with what documentation on file. This page handles the full employee lifecycle record: creation at offer acceptance, updates through designation changes and transfers, and archival at exit. It also surfaces org structure, document completeness, and asset assignments — all in one place.

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| Employee table | `hr_employee` JOIN `hr_department` JOIN `hr_employee` as manager | 5 min |
| Employee count badges (tabs) | `hr_employee` GROUP BY status | 5 min |
| Employee profile drawer | `hr_employee` single row + `hr_employee_document` + `hr_asset` WHERE assigned_to + `hr_leave_balance` + `hr_skills` + `hr_certification` | No cache |
| Department org chart | `hr_employee` WHERE status='ACTIVE', hierarchical (manager_id self-join) | 30 min |
| Search / typeahead | `hr_employee` (name, employee_id, designation) | 60 min (search index) |

Cache keys scoped to `(user_id, filters)`. `?nocache=true` for HR Manager (#79) only.

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?status` | `active`, `on_notice`, `exited`, `inactive`, `all` | `active` | Filter by employment status |
| `?division` | A–O (single or comma-sep) | `all` | Filter by division/department |
| `?employment_type` | `full_time`, `part_time`, `contract`, `intern` | `all` | Filter by employment type |
| `?work_location` | `delhi`, `hyderabad`, `bengaluru`, `remote`, `all` | `all` | Filter by work location |
| `?join_before` | `YYYY-MM-DD` | — | Joined before this date |
| `?join_after` | `YYYY-MM-DD` | — | Joined on or after this date |
| `?q` | string ≥ 2 chars | — | Full-text search: name, employee_id, designation |
| `?sort` | `name_asc`, `name_desc`, `join_date_asc`, `join_date_desc`, `designation`, `division` | `name_asc` | Table sort order |
| `?page` | integer | `1` | Server-side pagination (25 per page) |
| `?view` | `table`, `org_chart` | `table` | Toggle between table and org chart view |
| `?export` | `csv` | — | Export filtered employee list (HR Manager only) |
| `?nocache` | `true` | — | Bypass Memcached (HR Manager #79 only) |

---

## HTMX Part-Load Routes

| Part | Route | Trigger | Target ID |
|---|---|---|---|
| Employee table | `?part=table` | Page load + filter + sort + page | `#o2-emp-table` |
| Status tab counts | `?part=tab_counts` | Page load; after add/edit/exit | `#o2-status-tabs` |
| Employee profile drawer | `?part=drawer&id={employee_id}` | Row click / [View] action | `#o2-drawer` |
| Add employee modal | `?part=add_modal` | [+ Add Employee] click | `#modal-container` |
| Edit employee drawer | `?part=edit_drawer&id={employee_id}` | [Edit] action in drawer | `#o2-drawer` |
| Org chart | `?part=org_chart` | [Org Chart] tab click | `#o2-org-chart` |
| Document upload modal | `?part=doc_upload_modal&id={employee_id}` | [Upload Document] in drawer | `#modal-container` |

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Employee Directory   [🔍 Search name, ID, designation...]  [+ Add]  │
├──────────────────────────────────────────────────────────────────────┤
│  [Active(112)] [On Notice(7)] [Exited(38)] [Inactive(2)] [All(159)]  │
├──────────────────────────────────────────────────────────────────────┤
│  FILTER BAR                                                          │
│  [Division ▼] [Employment Type ▼] [Location ▼] [Join Date ▼]         │
│  Active filters: Division: C, D ×                    [Clear All]    │
├──────────────────────────────────────────────────────────────────────┤
│  [☐ Select All]  N selected  [Bulk: Export | Send Announcement]     │
│  Showing 1–25 of 42   Sort: [Name ↑▼]    [Table | Org Chart] toggle │
├──────────────────────────────────────────────────────────────────────┤
│  ☐ │ Emp ID │ Name │ Designation │ Division │ Manager │ Join │ Loc │ │
│    │ Type  │ Status │ Docs │ Actions                                  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Employee Table

| Column | Description |
|---|---|
| ☐ | Checkbox for bulk selection |
| Emp ID | `EF-XXXX` format (auto-generated sequential). Monospace. |
| Name | Full name + avatar (initials-based). Click → opens profile drawer |
| Designation | Official designation title |
| Division | Division letter badge (A–O) + division name |
| Manager | Reporting manager name (link → opens that manager's profile drawer) |
| Join Date | Date (relative if < 30 days: "3 days ago") |
| Location | City badge: DELHI / HYDERABAD / BENGALURU / REMOTE |
| Type | FULL_TIME (green) / PART_TIME (blue) / CONTRACT (amber) / INTERN (grey) |
| Status | ACTIVE (green) / ON_NOTICE (amber) / EXITED (red) / INACTIVE (grey) |
| Docs | Document completeness indicator: ✓ if all required docs filed; ⚠ N missing |
| Actions | [View] [Edit] [···] kebab |

**Kebab menu options (role-gated):**
- [Edit] — HR Manager and HRBP (own-division employees)
- [Initiate Exit] — HR Manager only → opens offboarding workflow in O-04
- [Reset Password] — HR Manager only → triggers password reset email
- [Download Payslip] — Payroll Exec for own-records context
- [View in Org Chart] — all roles

**Exited employee row:** greyed out. Status badge "EXITED" + last working date shown. [View] available; no edit actions.

**Contract employee row:** amber left border. "CONTRACT" type badge. Shows contract end date in tooltip on hover.

---

## Employee Profile Drawer

Full right-side drawer. 6 tabs.

```
┌──────────────────────────────────────────────────────────────────┐
│  Rohan Verma · EF-0047                               [Edit] [×]  │
│  Backend Engineer · Division C · Reports to: Arjun K. (CTO)     │
│  📍 Hyderabad · Full-Time · Joined: 12 Jun 2024 (9 months)      │
│  Status: ACTIVE                                                  │
├──────────────────────────────────────────────────────────────────┤
│  [Profile] [Documents] [Assets] [Leave] [Skills] [Timeline]     │
└──────────────────────────────────────────────────────────────────┘
```

**Tab 1 — Profile**

```
  Personal Details
  ─────────────────────────────
  Date of Birth:     12 Mar 1996 (29 years)
  Gender:            Male
  PAN:               ABCDE1234F
  Aadhaar (last 4):  ×××× 7891
  Personal Email:    rohan.v@gmail.com
  Emergency Contact: Priya Verma · +91-98765-43210 (Spouse)

  Employment Details
  ─────────────────────────────
  Employee ID:       EF-0047
  Designation:       Backend Engineer
  Grade:             L3
  Division:          C — Engineering
  Reporting Manager: Arjun Kumar (CTO #2)
  Work Location:     Hyderabad
  Employment Type:   Full-Time (Permanent)
  Probation:         Completed (confirmed 12 Sep 2024)
  Notice Period:     60 days
  CTC:               ₹14,40,000 p.a. (₹1,20,000/month gross)

  Statutory Compliance
  ─────────────────────────────
  PF UAN:            100123456789
  ESIC IP Number:    (not applicable — CTC > ₹21,000/month ESIC wage ceiling)
  Bank Account:      SBI ××××4521 (IFSC: SBIN0001234)
  PT State:          Telangana (₹200/month)
```

**Tab 2 — Documents**

```
  ☐ Document            Status      Uploaded    Expiry
  ✓ Offer Letter        On file     12 Jun 2024  —
  ✓ Appointment Letter  On file     12 Jun 2024  —
  ✓ PAN Card            On file     14 Jun 2024  —
  ✓ Aadhaar Card        On file     14 Jun 2024  —
  ✓ BGV Report          CLEAR       20 Jun 2024  —
  ✓ Form 16 FY24-25     On file     20 Jun 2025  —
  ⚠ Medical Fitness Cert Missing    —            —
  [+ Upload Document]
```

Required documents per employment type:
- FULL_TIME: Offer Letter, Appointment Letter, PAN, Aadhaar, BGV Report, Bank Details
- CONTRACT: Offer Letter, PAN, Aadhaar, Contract Agreement, GST Certificate (if vendor)
- INTERN: Offer Letter, Aadhaar, College NOC

[+ Upload Document]: opens document upload modal (document_type dropdown → file upload → submit). File size max 10 MB. Accepted: PDF, JPG, PNG. Stored in Cloudflare R2 with KMS encryption.

[View] on each document: opens PDF/image in-browser viewer. HR Manager and HRBP only.

**Visible to:** HR Manager (#79) full; Payroll Exec (#105) — statutory documents only (PAN, Aadhaar, bank details, Form 16); HRBP (#106) — non-financial documents; others: no documents tab.

**Tab 3 — Assets**

```
  Assigned Assets
  ─────────────────────────────
  LAPTOP    Dell Latitude 5540   SN: DL5540-78923   Assigned: 14 Jun 2024
  HEADSET   Jabra Evolve2        SN: JAB-4421        Assigned: 14 Jun 2024
  ACCESS    Card #047            Access zones: Office A, B    Assigned: 14 Jun 2024
  [+ Assign Asset]   [Mark Return]
```

[+ Assign Asset]: Office Administrator (#81) and HR Manager (#79) only. Dropdown of available assets.

[Mark Return]: on exit initiation, marks asset as returned → updates `hr_asset.status='AVAILABLE'`.

**Tab 4 — Leave**

Current year leave balance summary. Read-only in this context (full management in O-06).

```
  Leave Balances (FY 2025-26)
  ─────────────────────────────
  Casual Leave (CL)       Balance: 3 / 12
  Sick Leave (SL)         Balance: 5 / 12
  Earned Leave (EL)       Balance: 18 / 30 (carry-forward: 8)
  Comp Off                Balance: 2 / —
  Loss of Pay (LOP)       Used: 0 days

  Recent leave:
  SL   22 Mar 2026   1 day   APPROVED   [View]
  CL   15-16 Jan     2 days  APPROVED   [View]
```

**Tab 5 — Skills & Certifications**

```
  Skills
  ─────────────────────────────
  Python           ADVANCED   assessed 10 Feb 2026
  Django           EXPERT     assessed 10 Feb 2026
  PostgreSQL       ADVANCED   assessed 10 Feb 2026
  AWS (Lambda)     INTERMEDIATE

  Certifications
  ─────────────────────────────
  AWS Certified Developer – Associate   Issued: Mar 2025   Expires: Mar 2028   [View cert]
  [+ Add Certification]
```

[+ Add Certification]: HRBP (#106), L&D Coordinator (#107), or HR Manager (#79) can add.

**Tab 6 — Timeline**

Immutable audit log of all events in the employee's lifecycle.

```
  21 Mar 2026   HR Manager   Leave request approved (SL 22 Mar)
  14 Jan 2026   HRBP         OKR Q1 2026 check-in recorded
  10 Feb 2026   L&D Coord    Skills assessment updated
  12 Sep 2024   HR Manager   Probation confirmation — CONFIRMED
  12 Jun 2024   HR Manager   Employee record created (join date)
  ...
```

Sorted newest first. Infinite scroll (25 events per load).

---

## Add Employee Modal

```
┌──────────────────────────────────────────────────────────────────┐
│  Add Employee                                                    │
├──────────────────────────────────────────────────────────────────┤
│  Full Name*           [Rohan Verma                     ]         │
│  Personal Email*      [rohan.v@gmail.com               ]         │
│  Work Email*          [rohan.v@eduforge.com            ]         │
│  Designation*         [Backend Engineer                ]         │
│  Division*            [C — Engineering               ▼]          │
│  Reporting Manager*   [Search manager...             ▼]          │
│  Employment Type*     [Full-Time (Permanent)         ▼]          │
│  Work Location*       [Hyderabad                     ▼]          │
│  Join Date*           [2026-04-01                     ]          │
│  Grade                [L3                              ]         │
│  CTC (Annual, ₹)*     [1440000                         ]         │
│  PF UAN               [Optional — blank if new to PF   ]         │
│  Bank Account No.*    [                                ]         │
│  IFSC Code*           [                                ]         │
│  PT State*            [Telangana                     ▼]          │
│                                                                  │
│  [Cancel]                              [Create Employee Record]  │
└──────────────────────────────────────────────────────────────────┘
```

**Validation:**
- Full Name: required; min 2 chars; letters and spaces only
- Work Email: required; auto-generated suggestion `firstname.lastname@eduforge.com`; must be unique
- CTC: required; positive integer in ₹
- Join Date: required; cannot be > 90 days in the past (data integrity guard — historical entries need HR Manager override reason)
- Reporting Manager: required; must be an active employee; cannot self-report
- PT State: required; used to determine correct PT deduction slab

On submit: creates `hr_employee` record with `status='ACTIVE'`. If linked to an accepted offer (`hr_offer`), `hr_offer.offer_status` transitions to `CONVERTED` and `hr_candidate.current_stage` → `JOINED`. Triggers Task O-8 (probation reminder scheduling).

**Visible to:** HR Manager (#79) only.

---

## Edit Employee Drawer

Same form as Add, pre-populated. HR Manager can edit all fields. HRBP (#106) can edit: designation, grade, reporting manager, division (internal transfers). Payroll Exec (#105) can edit: bank account, IFSC, PT state, PF UAN, ESIC IP number.

All edits are appended to the employee Timeline (Tab 6) as immutable audit entries: `changed_field, old_value, new_value, changed_by, changed_at`.

---

## Org Chart View

`?view=org_chart` — Hierarchical tree of all active employees.

```
  Platform Owner / CEO (#1) [Arjun Kumar]
  ├── Platform CTO (#2)
  │   ├── Backend Engineer [Rohan V.]
  │   ├── Frontend Engineer [Kavya R.]
  │   └── DevOps/SRE Engineer [...]
  ├── Platform COO (#3)
  │   ├── Exam Operations Manager [...]
  │   └── ...
  └── HR Manager (#79) [Meera G.]
      ├── Recruiter [...]
      └── ...
```

- Rendered as a collapsible tree using D3.js (SVG)
- Each node: avatar + name + designation
- Click node → opens Employee Profile Drawer
- [Export as PNG] button — HR Manager only
- Collapse/expand by division
- Orphan detection: employees with `manager_id=NULL` (other than CEO) shown in amber — data quality alert

**Visible to:** HR Manager (#79), HR Business Partner (#106).

---

## Bulk Export CSV

Filename: `eduforge_employees_YYYY-MM-DD.csv`

**Columns for HR Manager:** employee_id, name, personal_email, work_email, designation, grade, division, manager_name, employment_type, work_location, join_date, status, ctc_annual, pf_uan, pt_state, notice_period_days

**Columns for Payroll Exec (#105, on explicit request):** employee_id, name, designation, bank_account, ifsc, pf_uan, esic_ip, pt_state, ctc_annual — only accessible via O-05 salary register export, not from this page.

Sensitive fields (PAN, Aadhaar, bank details) are NOT included in the general employee export CSV. Payroll-sensitive exports are gated to O-05 and require explicit HR Manager approval if bulk.

---

## Empty States

| Condition | Message |
|---|---|
| No employees match filters | "No employees found for the selected filters." with [Clear Filters] |
| No active employees | "No active employees on record." with [+ Add Employee] |
| No documents uploaded | "No documents on file. Click Upload Document to add." |
| No assets assigned | "No assets assigned to this employee." |
| No skills recorded | "No skills recorded. Add via the Skills tab or through L&D." |

---

## Toast Messages

| Action | Toast | Type |
|---|---|---|
| Employee created | "[Name] added to Employee Directory (EF-XXXX)." | Green |
| Employee updated | "[Name]'s record updated." | Green |
| Document uploaded | "[Doc type] uploaded for [Name]." | Green |
| Asset assigned | "[Asset] assigned to [Name]." | Green |
| Asset returned | "[Asset] marked as returned from [Name]." | Green |
| Export requested | "Export started — download will begin shortly." | Blue |
| PAN/Aadhaar edit blocked | "Contact HR Manager to update identity documents." | Amber (warning) |

---

## Authorization

**Route guard:** `@division_o_required(allowed_roles=[79, 80, 81, 105, 106, 107])` applied to `EmployeeDirectoryView`.

| Scenario | Behaviour |
|---|---|
| Payroll Exec (#105) accessing PAN/Aadhaar tab | Blocked — 403 inline for that tab |
| L&D Coordinator (#107) accessing Documents tab | Tab not rendered server-side |
| HTMX drawer for non-permitted fields | Fields omitted from HTML response |
| Export CSV by non-HR-Manager role | 403 |
| Edit action by Recruiter (#80) | [Edit] button not rendered |
