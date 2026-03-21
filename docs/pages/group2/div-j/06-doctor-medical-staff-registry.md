# 06 — Doctor & Medical Staff Registry

> **URL:** `/group/health/medical-staff/`
> **File:** `06-doctor-medical-staff-registry.md`
> **Template:** `portal_base.html`
> **Priority:** P1
> **Role:** Group Medical Coordinator (primary) · School Medical Officer

---

## 1. Purpose

Comprehensive registry of all medical and paramedical staff assigned across every branch — visiting doctors, on-campus nurses, paramedics, and pharmacists. Each record captures the individual's qualifications, professional registration details (MCI/Nursing Council), specialization, assigned branch(es), visit schedule, background verification (BGV) status, and contact information.

This registry is the authoritative personnel database for the group's health function. The Medical Coordinator uses it to ensure every branch has appropriate doctor and nursing coverage, monitor professional registration expiry dates (MCI for doctors, NNC/SNRC for nurses), manage BGV compliance, and coordinate specialist visits. Expired registrations have direct regulatory and medico-legal implications — a doctor operating with a lapsed MCI registration exposes the group to significant liability.

Scale: 2–10 medical staff per branch × 20–50 branches = 40–500 staff records. Doctor registrations must be verified annually; nursing council registrations every 3–5 years.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Medical Coordinator | G3 | Full CRUD — all staff, all branches | Primary registry owner |
| Group School Medical Officer | G3 | Edit schedule + view all records | Cannot create/deactivate staff profiles |
| Group Emergency Response Officer | G3 | Read only — for first responder identification | No clinical detail access |
| Branch Principal | Branch G3 | Read — own branch staff only | Aggregate view, no credentials |
| All other roles | — | — | No access |

> **Access enforcement:** Django view decorator `@require_role('medical_coordinator', 'school_medical_officer', 'emergency_response_officer')`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Health & Medical  ›  Doctor & Medical Staff Registry
```

### 3.2 Page Header
- **Title:** `Doctor & Medical Staff Registry`
- **Subtitle:** `[N] Total Staff · [N] Visiting Doctors · [N] On-Campus Nurses · [N] Branches Without Nurse`
- **Right controls:** `+ Add Staff Member` · `Advanced Filters` · `Export`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| MCI registration expired | "[N] doctors have expired MCI registrations. They cannot legally practice." | Red |
| Branch with no doctor assigned | "[N] branches have no visiting doctor assigned. Health coverage gap." | Red |
| Nurse absence with no backup | "Nurse at [Branch] is absent today. No backup assigned — medical room unstaffed." | Red |
| Staff BGV pending > 30 days | "[N] staff members have BGV pending for more than 30 days." | Amber |
| Registration expiring within 30 days | "[N] registrations (MCI/Nursing) expire within 30 days. Renewal action required." | Amber |
| Staff record incomplete | "[N] staff records are missing required fields (qualification docs, registration no, or contact)." | Amber |

---

## 4. KPI Summary Bar (5 cards)

| Card | Metric | Colour Rule |
|---|---|---|
| Total Medical Staff | All active staff records | Blue always |
| Active Visiting Doctors | Doctors with active status and assigned branches | Blue always |
| Nurses On-Site | Nurses with Operational status assigned to medical rooms | Green = all branches covered · Yellow = 1–3 gaps · Red > 3 gaps |
| MCI / Registration Expiring (30 days) | Staff with registration expiry within 30 days | Green = 0 · Yellow 1–3 · Red > 3 |
| Branches Without Nurse | Branches with no active nurse assignment | Green = 0 · Red > 0 |

---

## 5. Main Table — Medical Staff Registry

**Search:** Staff name, registration number, branch. 300ms debounce.

**Advanced Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Staff Type | Checkbox | Visiting Doctor / On-Campus Nurse / Paramedic / Pharmacist |
| BGV Status | Radio | All / Verified / Pending / Failed |
| Active | Radio | All / Active Only / Inactive Only |
| Reg Expiry | Radio | All / Expiring in 30d / Expiring in 60d / Expiring in 90d / Already Expired |
| Specialization | Multi-select | General Physician / Paediatrics / Orthopaedics / Gynaecology / Psychiatry / Other |

**Columns:**
| Column | Sortable | Notes |
|---|---|---|
| Staff Name | ✅ | Link → `staff-detail` drawer |
| Type | ✅ | Visiting Doctor / On-Campus Nurse / Paramedic / Pharmacist |
| Branch | ✅ | Primary branch; "+ N more" if multi-branch |
| Specialization | ✅ | For doctors; — for nurses/paramedics |
| MCI / NNC Reg No | ✅ | Registration number |
| Reg Expiry | ✅ | Date; colour: Green > 90d · Yellow 30–90d · Red ≤ 30d · Red strikethrough if expired |
| BGV Status | ✅ | Verified ✅ / Pending ⚠ / Failed ❌ |
| Active | ✅ | Active (Green) / Inactive (Grey) |
| Actions | ❌ | View · Edit · Schedule |

**Default sort:** Reg Expiry ascending (most urgent first), then Type.
**Pagination:** Server-side · 25/page.

---

## 6. Drawers

### 6.1 Drawer: `staff-detail` — Full Staff Profile
- **Trigger:** Staff Name link or Actions → View
- **Width:** 680px
- **Tabs:** Profile · Qualifications · Schedule · BGV · Visit History

**Profile tab:**
| Field | Notes |
|---|---|
| Staff ID | System-generated |
| Full Name | |
| Type | Visiting Doctor / On-Campus Nurse / Paramedic / Pharmacist |
| Gender | |
| Date of Birth | |
| Qualification | MBBS / MD / MS / BDS / BNSc / GNM / B.Pharm etc. |
| Specialization | (Doctors only) |
| MCI / NNC / Pharmacy Reg No | Professional registration number |
| Registration Body | MCI / State Medical Council / Indian Nursing Council / State NRC |
| Registration Expiry | Date; coloured as per expiry rules |
| Mobile | |
| Email | |
| Emergency Contact | Name + number |
| Assigned Branch(es) | List of branches; with primary flagged |
| Status | Active / Inactive / On Leave |
| Joined Date | |
| Notes | |

**Qualifications tab:**
| Field | Notes |
|---|---|
| Degree | Name of qualification |
| Specialization (if PG) | |
| University / Institute | |
| Year of Passing | |
| Certificate | Upload (PDF/image) — view/download link once uploaded |

Multiple qualifications can be added (repeat form).

**Schedule tab:**
- Recurring visit/duty schedule per assigned branch
- Display: table with Branch · Day(s) · From Time · To Time · Recurrence (Weekly/Fortnightly) · Notes
- "Add Schedule Slot" button — opens inline form row
- "Edit Schedule" toggles row to editable state
- School Medical Officer can edit schedules directly

**BGV tab:**
| Field | Notes |
|---|---|
| BGV Status | Verified / Pending / Failed |
| BGV Agency | Name of verification agency |
| Verification Date | Date |
| Verified By (internal) | HR/Admin name |
| BGV Report | Upload (PDF) — view link once uploaded |
| Notes | Any exceptions or flags |
| Re-verification Due | Date (typically 3–5 years) |

**Visit History tab:**
- Last 20 visits/duty days logged against this staff member
- Columns: date, branch, start time, end time, patients seen / services provided, status (Attended / Absent / Cancelled), notes
- "Export Visit History" → CSV download

---

### 6.2 Drawer: `staff-create` — Add New Staff Member
- **Trigger:** `+ Add Staff Member` (Medical Coordinator only)
- **Width:** 640px

**Fields (grouped by section):**

*Identity & Credentials:*
| Field | Type | Validation |
|---|---|---|
| Full Name | Text | Required |
| Type | Select | Required |
| Gender | Radio | Required |
| Date of Birth | Date | Required |
| Qualification | Text | Required |
| Specialization | Text | Required for Visiting Doctor |
| MCI / NNC / Reg No | Text | Required; unique in system |
| Registration Body | Select | Required |
| Registration Expiry | Date | Required |

*Contact:*
| Field | Type |
|---|---|
| Mobile | Text (with country code) |
| Email | Email |
| Emergency Contact Name | Text |
| Emergency Contact Phone | Text |

*Assignment:*
| Field | Type |
|---|---|
| Primary Branch | Select |
| Additional Branches | Multi-select |
| Status | Select (default: Active) |
| Joined Date | Date |

*Initial Schedule:* (optional at creation)
- Inline repeating fields: Branch, Day(s), From Time, To Time

**Validation:** MCI/NNC registration number must be unique across the group. Visiting Doctor requires MCI Reg No and Expiry. Nurse requires NNC Reg No.

---

### 6.3 Drawer: `staff-edit` — Edit Staff Profile
- **Trigger:** Actions → Edit
- **Width:** 640px (same layout as create, pre-populated)
- **Read-only after creation:** Staff ID, Date of Birth, MCI / NNC Reg No (change requires Coordinator confirmation modal)
- **Available to:** Medical Coordinator (all fields) · School Medical Officer (Schedule tab fields only — accessed via Actions → Schedule)

---

### 6.4 Modal: `assign-branch` — Assign to Additional Branch
- **Trigger:** Actions → Schedule · or within staff-detail Profile tab "Assign Branch +"
- **Width:** 480px
- **Fields:** Staff member (pre-selected from context) · Additional Branch (select from unassigned branches) · Schedule: days + times for that branch · Notes
- **Validation:** Cannot assign same branch twice. Cannot schedule overlapping times at different branches on the same day.

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Staff member added | "[Name] added to medical staff registry." | Success | 4s |
| Staff profile updated | "[Name]'s profile updated." | Success | 4s |
| Schedule updated | "Schedule updated for [Name] at [Branch]." | Success | 4s |
| Branch assigned | "[Name] assigned to [Branch]." | Success | 4s |
| BGV verified | "BGV verified for [Name]." | Success | 4s |
| Staff deactivated | "[Name] marked inactive. All schedules removed." | Warning | 5s |
| Registration expiry alert | "Renewal reminder: [Name]'s [MCI/NNC] registration expires on [date]." | Warning | 6s |
| Export prepared | "Staff registry export ready. Download now." | Info | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No staff registered | "No Medical Staff Registered" | "Add doctors, nurses, and support staff to build the medical team registry." | [+ Add Staff Member] |
| No results for filters | "No Staff Match Filters" | "Try adjusting branch, type, BGV status, or expiry filters." | [Clear Filters] |
| No registration expiry alerts | "All Registrations Valid" | "No staff have registrations expiring within 30 days." | — |
| No BGV pending | "All BGVs Complete" | "All active staff have completed background verification." | — |
| Visit history empty | "No Visits Recorded" | "No visit history has been logged for this staff member yet." | — |
| Schedule empty | "No Schedule Set" | "No duty schedule has been configured for this staff member." | [Add Schedule] |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 5 KPI cards + table skeleton (15 rows × 9 columns) + alerts |
| Filter/search | Table body skeleton (10 rows) |
| Staff detail drawer | 680px drawer skeleton; each tab loads lazily on click |
| Profile tab | Field skeleton (label + value pairs, 12 rows) |
| Qualifications tab | Card skeleton (2 qualification cards) |
| Schedule tab | Table skeleton (5 rows × 6 columns) |
| BGV tab | Form field skeleton (6 fields) |
| Visit History tab | Table skeleton (8 rows × 7 columns) |
| Document upload | Progress bar |
| Create/Edit drawer | 640px form skeleton |

---

## 10. Role-Based UI Visibility

| Element | Medical Coordinator G3 | School Medical Officer G3 | Emergency Response Officer G3 |
|---|---|---|---|
| Add Staff | ✅ | ❌ | ❌ |
| Edit Full Profile | ✅ | ❌ | ❌ |
| Edit Schedule | ✅ | ✅ | ❌ |
| View Qualifications & Reg Docs | ✅ | ✅ | ❌ |
| View BGV Details | ✅ | ✅ | ❌ |
| Deactivate Staff | ✅ | ❌ | ❌ |
| Assign Branch | ✅ | ❌ | ❌ |
| View Visit History | ✅ | ✅ | ✅ (limited: name, branch, date only) |
| Export Registry | ✅ | ✅ | ❌ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/health/medical-staff/` | JWT (G3+) | Paginated, filtered staff list |
| GET | `/api/v1/group/{group_id}/health/medical-staff/{id}/` | JWT (G3+) | Full staff profile (all tab data) |
| POST | `/api/v1/group/{group_id}/health/medical-staff/` | JWT (Role 85) | Create new staff record |
| PATCH | `/api/v1/group/{group_id}/health/medical-staff/{id}/` | JWT (Role 85, 86) | Update staff profile |
| GET | `/api/v1/group/{group_id}/health/medical-staff/kpis/` | JWT (G3+) | KPI card values |
| GET | `/api/v1/group/{group_id}/health/medical-staff/{id}/schedule/` | JWT (G3+) | Staff schedule |
| PATCH | `/api/v1/group/{group_id}/health/medical-staff/{id}/schedule/` | JWT (Role 85, 86) | Update schedule |
| POST | `/api/v1/group/{group_id}/health/medical-staff/{id}/assign-branch/` | JWT (Role 85) | Assign to additional branch |
| GET | `/api/v1/group/{group_id}/health/medical-staff/{id}/visit-history/` | JWT (G3+) | Visit history for staff |
| POST | `/api/v1/group/{group_id}/health/medical-staff/{id}/deactivate/` | JWT (Role 85) | Deactivate staff record |
| GET | `/api/v1/group/{group_id}/health/medical-staff/export/` | JWT (Role 85, 86) | Async CSV/XLSX export |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-get/post | hx-target | hx-swap |
|---|---|---|---|---|
| Search | `input delay:300ms` | GET `.../medical-staff/?q={val}` | `#staff-table-body` | `innerHTML` |
| Filter apply | `click` | GET `.../medical-staff/?{filters}` | `#staff-table-section` | `innerHTML` |
| Pagination | `click` | GET `.../medical-staff/?page={n}` | `#staff-table-section` | `innerHTML` |
| Sort by column | `click` on header | GET `.../medical-staff/?sort={col}&dir={asc/desc}` | `#staff-table-section` | `innerHTML` |
| Open staff drawer | `click` on Staff Name | GET `.../medical-staff/{id}/` | `#drawer-body` | `innerHTML` |
| Drawer tab switch | `click` | GET `.../medical-staff/{id}/?tab={name}` | `#drawer-tab-content` | `innerHTML` |
| Submit create | `click` | POST `.../medical-staff/` | `#staff-table-section` | `innerHTML` |
| Submit edit | `click` | PATCH `.../medical-staff/{id}/` | `#staff-row-{id}` | `outerHTML` |
| Inline schedule edit | `click` Edit on schedule row | GET `.../medical-staff/{id}/schedule/?edit={row}` | `#schedule-row-{row}` | `outerHTML` |
| Save schedule row | `click` Save | PATCH `.../medical-staff/{id}/schedule/` | `#schedule-row-{row}` | `outerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
