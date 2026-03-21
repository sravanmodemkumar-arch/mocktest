# 16 — Civic Programme Register

> **URL:** `/group/nss/civic/`
> **File:** `16-civic-programme-register.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P2
> **Roles:** NSS/NCC Coordinator G3 (full) · Branch NSS Officer Branch G2 (own branch) · Branch NCC Officer Branch G2 (own branch)

---

## 1. Purpose

Tracks all civic education and community service programmes run across branches — blood donation drives, tree plantation drives, swachh bharat activities, digital literacy camps, voter awareness, health check camps, disaster relief contributions, road safety drives, and other community engagement activities. Serves as the group's official log for civic programme compliance and CSR reporting. Distinct from NSS Programme Tracker (which tracks 240-hour NSS-specific activities) — this covers non-NSS civic activities open to all students.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| NSS/NCC Coordinator | G3 | Full — create, approve, and view all civic programmes | Primary owner |
| Branch NSS Officer | Branch G2 | Create and manage own branch civic programmes | Cannot see other branches |
| Branch NCC Officer | Branch G2 | Create and manage own branch civic programmes | Cannot see other branches |
| Branch Principal | Branch G3 | View own branch programmes | Read-only |
| All others | — | — | No access |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Civic Programme Register
```

### 3.2 Page Header
```
Civic Programme Register                           [+ New Programme]  [Export ↓]
AY [academic year]  ·  [N] Programmes  ·  [N] Branches  ·  [N] Student Volunteers
```

### 3.3 Summary Stats Bar

| Stat | Value |
|---|---|
| Total Programmes This AY | N |
| Completed | N |
| Ongoing / Upcoming | N |
| Branches Participated | N of total |
| Total Student Volunteers | N |
| Total Volunteer Hours | N |

---

## 4. Programmes Table

**Search:** Programme name, branch, type. Debounce 300ms.

**Advanced Filters:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Programme Type | Multi-select | Blood Donation · Tree Plantation · Swachh Bharat · Digital Literacy · Voter Awareness · Health Camp · Disaster Relief · Road Safety · Environment · Other |
| Status | Multi-select | Planning · Approved · Ongoing · Completed · Cancelled |
| Date Range | Date range | |
| Report Submitted | Toggle | Show without reports |

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Programme Name | Text + link | ✅ | Opens programme detail drawer |
| Branch | Text | ✅ | "All Branches" for group-wide |
| Type | Badge | ✅ | |
| Date | Date | ✅ | |
| Venue / Location | Text | ❌ | |
| Volunteers | Number | ✅ | Student volunteers |
| Hours | Number | ✅ | Total volunteer hours |
| Beneficiaries | Number | ✅ | People/community impacted |
| Status | Badge | ✅ | |
| Report | Badge | ✅ | ✅ Submitted · ❌ Pending |
| Actions | — | ❌ | View · Edit · Submit Report · Cancel |

**Default sort:** Date descending.

**Pagination:** 25/page.

---

## 5. Drawers & Modals

### 5.1 Drawer: `civic-programme-create`
- **Width:** 560px
- **Tabs:** Details · Volunteers · Report

#### Tab: Details
| Field | Type | Required | Validation |
|---|---|---|---|
| Programme Name | Text | ✅ | Min 5, max 200 |
| Programme Type | Select | ✅ | All types |
| Branch | Select | ✅ | Own branch for Branch Officer |
| Date | Date | ✅ | |
| End Date | Date | ❌ | For multi-day programmes |
| Time | Time | ❌ | |
| Venue / Location | Text | ✅ | |
| Organising Body | Text | ❌ | e.g. "Red Cross", "Municipal Corporation" |
| Description | Textarea | ✅ | Min 30 chars |
| Target Beneficiaries | Text | ❌ | e.g. "Flood-affected families" |
| Estimated Beneficiary Count | Number | ❌ | |

#### Tab: Volunteers
| Field | Type | Required | Notes |
|---|---|---|---|
| Student Volunteers | Multi-select or Number | ✅ | Can name individuals or enter count |
| Staff Coordinators | Text | ❌ | |
| External Partners | Text | ❌ | NGOs, Govt. departments |
| Equipment / Materials | Textarea | ❌ | |

#### Tab: Report (post-programme)
| Field | Type | Required |
|---|---|---|
| Report Narrative | Textarea (rich text) | ✅ (if Completed) |
| Actual Volunteers | Number | ✅ |
| Actual Beneficiaries | Number | ❌ |
| Volunteer Hours | Number | ✅ |
| Highlights | Textarea | ❌ |
| Issues / Feedback | Textarea | ❌ |
| Photographs | File upload (max 15 × 5MB) | ❌ |
| Press Coverage / Links | Text | ❌ |
| Supporting Documents | File upload | ❌ |

**Buttons:** [Save Programme] + [Cancel]

### 5.2 Drawer: `civic-programme-detail`
- **Width:** 680px
- **Tabs:** Overview · Volunteers · Report

#### Tab: Overview
Full programme metadata. [Edit Programme] button (own branch / Coordinator).

#### Tab: Volunteers
Table: Student Name · Class · Branch · Role (Organiser/Volunteer) · Hours Contributed.
[+ Add Volunteer] · Bulk import CSV.

#### Tab: Report
Post-programme report (read-only view). [Submit Report] button if report not submitted.

### 5.3 Modal: `cancel-programme`
- **Width:** 420px
- **Fields:** Reason (required, min 20 chars) · Notify volunteers (checkbox on)
- **Buttons:** [Cancel Programme] (danger) + [Back]

---

## 6. Charts

### 6.1 Civic Activity by Branch (current AY)
- **Type:** Horizontal bar
- **Data:** Programme count per branch, stacked by type
- **Export:** PNG

### 6.2 Volunteer Hours Trend (current AY)
- **Type:** Line chart (monthly)
- **Data:** Total volunteer hours logged per month across the group
- **Export:** PNG

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Programme created | "Civic programme [Name] created." | Success | 4s |
| Report submitted | "Programme report submitted for [Name]." | Success | 4s |
| Photos uploaded | "[N] photos uploaded for [Name]." | Info | 4s |
| Programme cancelled | "Programme cancelled. Volunteers notified." | Warning | 6s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No programmes this AY | "No civic programmes recorded" | "Create your first civic programme for your branch" | [+ New Programme] |
| No reports pending | "All reports submitted" | "Every completed programme has a report" | — |
| Filters match nothing | "No programmes match your filters" | | [Clear Filters] |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: stats bar + table (8 rows) + charts |
| Filter/search | Inline skeleton rows |
| Report submit | Spinner in submit button |
| Photo upload | Progress bar per file |

---

## 10. Role-Based UI Visibility

| Element | NSS/NCC Coordinator G3 | Branch NSS/NCC Officer (own branch) |
|---|---|---|
| View all branches | ✅ | Own branch only |
| [+ New Programme] | ✅ | ✅ (own branch) |
| [Edit Programme] | ✅ | Own branch only |
| [Submit Report] | ✅ | ✅ (own branch) |
| [Cancel Programme] | ✅ | ❌ |
| [Export] | ✅ | ✅ (own branch data) |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/nss/civic/` | JWT (G3) | Civic programmes list |
| POST | `/api/v1/group/{id}/nss/civic/` | JWT (G3/G2) | Create programme |
| GET | `/api/v1/group/{id}/nss/civic/{pid}/` | JWT (G3/G2) | Programme detail |
| PUT | `/api/v1/group/{id}/nss/civic/{pid}/` | JWT (G3/G2) | Update programme |
| POST | `/api/v1/group/{id}/nss/civic/{pid}/report/` | JWT (G3/G2) | Submit report |
| POST | `/api/v1/group/{id}/nss/civic/{pid}/photos/` | JWT (G3/G2) | Upload photos |
| POST | `/api/v1/group/{id}/nss/civic/{pid}/cancel/` | JWT (G3) | Cancel programme |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Table search | `input delay:300ms` | GET `.../nss/civic/?q=` | `#civic-table-body` | `innerHTML` |
| Filter apply | `click` | GET `.../nss/civic/?filters=` | `#civic-table-section` | `innerHTML` |
| Open programme detail | `click` | GET `.../nss/civic/{id}/` | `#drawer-body` | `innerHTML` |
| Drawer tab switch | `click` | GET `.../nss/civic/{id}/{tab}/` | `#drawer-tab-content` | `innerHTML` |
| Submit report | `submit` | POST `.../nss/civic/{id}/report/` | `#drawer-body` | `innerHTML` |
| Pagination | `click` | GET `.../nss/civic/?page=` | `#civic-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
