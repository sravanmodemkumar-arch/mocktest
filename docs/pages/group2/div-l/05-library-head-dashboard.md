# 05 — Library & Learning Resources Head Dashboard

> **URL:** `/group/library/head/`
> **File:** `05-library-head-dashboard.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P0
> **Role:** Group Library & Learning Resources Head (Role 101, G2) — exclusive post-login landing

---

## 1. Purpose

Primary post-login landing for the Group Library & Learning Resources Head. Manages the central group-level e-library and all digital learning resources distributed to branches. The Library Head curates and categorizes resources (e-books, video lectures, question banks, reference materials, past papers, revision notes), controls which branches have access to which resources, monitors usage analytics, and processes resource requests from branch librarians.

**Access level G2 (Group Content):** The Library Head can upload and manage shared content across all branches. They cannot configure branch portals, manage users, or access financial/HR data.

Scale: 500–10,000 digital resources in catalogue · 20–50 branches · 50–500 resource access requests per month · 5,000–50,000 student digital resource accesses per month.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Library & Learning Resources Head | G2 | Full — catalogue management, distribution, analytics | Exclusive dashboard |
| Group Academic Director (Div B) | G3 | View catalogue and usage analytics | Read-only |
| Branch Librarian | Branch G2 | View resources assigned to their branch only | Branch-scoped |
| Group Chairman / CEO | G5 / G4 | View via Governance Reports | Not this URL |
| All others | — | — | Redirected |

> **Access enforcement:** `@require_role('library_learning_head')`.

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Library & Learning Resources Head Dashboard
```

### 3.2 Page Header
```
Welcome back, [Head Name]                        [+ Add Resource]  [Export Usage Report ↓]
[Group Name] — Library & Learning Resources Head · Last login: [date time]
[N] Resources in Catalogue  ·  [N] Branches with Access  ·  [N] Downloads This Month
```

### 3.3 Alert Banner (conditional)

| Condition | Banner Text | Severity |
|---|---|---|
| Branch with zero resource access this month | "[N] branch(es) have not accessed any resources this month." | Amber |
| Resource access expiry approaching | "[N] resource distribution assignment(s) expire within 7 days." | Amber |
| Resource request awaiting approval | "[N] new resource requests from branches are pending." | Amber |
| Storage quota above 80% | "Group digital storage is at [N]% capacity. Review and archive unused resources." | Amber |

---

## 4. KPI Summary Bar (6 cards)

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| Total Resources | Active resources in central catalogue | Blue always | → E-Library Catalogue page 17 |
| Branches with Active Access | Branches with at least 1 resource distributed | Green = all · Yellow = 1–3 without access · Red = 4+ | → Content Distribution page 18 |
| Downloads This Month | Total resource download/access events this month | Blue always | → Analytics page 20 |
| Pending Resource Requests | Requests from branch librarians for new resources | Green = 0 · Yellow 1–5 · Red > 5 | → Section 5.3 |
| Resources Added This Month | New resources added to catalogue in current month | Blue always | → E-Library Catalogue page 17 |
| Expiring Assignments (7d) | Distribution assignments expiring within 7 days | Green = 0 · Yellow > 0 | → Content Distribution page 18 |

**HTMX:** `hx-trigger="every 5m"` `hx-get="/api/v1/group/{id}/library/head/kpi/"` `hx-target="#kpi-bar"` `hx-swap="innerHTML"`.

---

## 5. Sections

### 5.1 Recently Added Resources

> New catalogue entries from the last 30 days.

**Display:** Table — max 10 rows, "View All →" to page 17.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Resource Title | Text + link | ✅ | Opens `resource-edit` drawer |
| Type | Badge | ✅ | E-Book · Video Lecture · Question Bank · Past Paper · Reference · Revision Notes · Worksheet |
| Subject | Badge | ✅ | e.g. Mathematics · Physics · English |
| Class | Badge | ✅ | Class 6–12 · Integrated |
| Added On | Date | ✅ | |
| Distributed To | Number | ✅ | Count of branches with access |
| Downloads | Number | ✅ | Total accesses since added |
| Actions | — | ❌ | Edit · Distribute · Archive |

---

### 5.2 Branch Access Overview

> Which branches have access to how many resources.

**Search:** Branch name. Debounce 300ms.

**Filters:** State, Access Level (High/Medium/Low), Resources Count.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Branch | Text + link | ✅ | |
| City | Text | ✅ | |
| Resources Assigned | Number | ✅ | Total resources distributed to branch |
| Downloads (Month) | Number | ✅ | This month's accesses |
| Last Access | Date + relative | ✅ | Red if > 30 days |
| Expiring Soon | Number | ✅ | Assignments expiring in 7 days — badge if > 0 |
| Actions | — | ❌ | View Assigned · Renew Expiring |

**Default sort:** Downloads (Month) ascending (least active first).

**Pagination:** 25/page.

---

### 5.3 Resource Request Queue

> Branch librarians requesting addition of new resources to the catalogue.

**Display:** Table — max 8 rows, "View All" link.

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Request ID | Text | ✅ | e.g. RR-2026-015 |
| Branch | Text | ✅ | |
| Resource Title / Description | Text | ✅ | What the branch needs |
| Type Requested | Badge | ✅ | E-Book · Video · Question Bank · etc. |
| Subject / Class | Text | ❌ | |
| Requested By | Text | ❌ | Branch librarian name |
| Days Pending | Number | ✅ | Red if > 14 |
| Actions | — | ❌ | [Fulfil] [Decline] [View] |

**[Fulfil]:** Opens `resource-create` drawer pre-filled with request details — Library Head can upload matching resource and distribute to requesting branch in one flow.

**[Decline]:** Modal — reason field (min 20 chars) + alternative suggestion (optional).

---

### 5.4 Top Resources by Usage (this month)

**Display:** Compact ranked list — top 8 resources.

**Fields per item:** Rank · Resource title · Type badge · Subject · Downloads this month · Trend vs last month (↑↓).

**"View Full Analytics →"** link to page 20.

---

## 6. Drawers & Modals

### 6.1 Drawer: `resource-create` — Add New Resource
- **Trigger:** [+ Add Resource] header button or [Fulfil] in request queue
- **Width:** 680px
- **Tabs:** Metadata · File · Classification · Access

#### Tab: Metadata
| Field | Type | Required | Validation |
|---|---|---|---|
| Title | Text | ✅ | Min 3, max 200 chars |
| Description | Textarea | ❌ | Max 500 chars |
| Resource Type | Select | ✅ | E-Book · Video Lecture · Question Bank · Past Paper · Reference · Revision Notes · Worksheet · Audio |
| Author / Source | Text | ❌ | Max 150 chars |
| Publisher | Text | ❌ | |
| Publication Year | Year | ❌ | |
| Language | Select | ✅ | Telugu · English · Hindi · Other |
| Tags | Multi-input | ❌ | Freeform tags — comma-separated |

#### Tab: File
| Field | Type | Required | Validation |
|---|---|---|---|
| Upload File | File upload | Conditional | PDF/MP4/DOCX/ZIP — max 500MB per file |
| External URL | URL | Conditional | If hosted externally (YouTube/Drive) — required if no file uploaded |
| Thumbnail | Image upload | ❌ | JPG/PNG, max 2MB, recommended 800×600 |
| File Size (auto) | Read-only | — | Auto-calculated |

> One of File or External URL is required.

#### Tab: Classification
| Field | Type | Required | Validation |
|---|---|---|---|
| Subject | Multi-select | ✅ | Mathematics · Physics · Chemistry · Biology · English · Telugu · Social Studies · Commerce · Computer Science · etc. |
| Class / Grade | Multi-select | ✅ | Class 6 · 7 · 8 · 9 · 10 · 11 · 12 · Integrated |
| Stream | Multi-select | ❌ | MPC · BiPC · MEC · CEC · HEC · IIT Foundation |
| Difficulty Level | Select | ❌ | Beginner · Intermediate · Advanced |
| Curriculum Alignment | Select | ❌ | CBSE · State Board (AP) · State Board (TS) · Both |
| Exam Relevance | Multi-select | ❌ | JEE · NEET · EAMCET · SSC CGL · Board Exam |

#### Tab: Access
| Field | Type | Required | Validation |
|---|---|---|---|
| Access Type | Radio | ✅ | All Branches · Selected Branches Only · Restricted |
| Select Branches | Multi-select | Conditional | If Selected Branches chosen |
| Access Expiry | Date | ❌ | Leave blank = permanent |
| Student Access | Toggle | ✅ | Default On — students can access |
| Staff Only | Toggle | ❌ | Only teachers / faculty can access |

**Submit:** "Add to Catalogue" — disabled until Metadata + File + Classification tabs valid.
**On success:** Resource added to catalogue, access assigned per Tab settings, toast.

### 6.2 Drawer: `resource-edit`
- **Width:** 680px — same 4 tabs, pre-filled
- **Version note in Metadata tab:** "Editing this resource creates a new version. Previous version retained."

### 6.3 Modal: `request-decline`
- **Width:** 420px
- **Fields:** Decline reason (required, min 20 chars) · Alternative resource suggestion (optional, links to catalogue search)
- **Buttons:** [Decline Request] (danger) + [Cancel]

### 6.4 Modal: `resource-archive`
- **Width:** 380px
- **Content:** "Archive [Resource Title]? It will no longer appear in branch access lists."
- **Buttons:** [Archive] (warning yellow) + [Cancel]

---

## 7. Charts

### 7.1 Monthly Download Trend (last 6 months)
- **Type:** Line chart
- **Data:** Total resource download/access events per month
- **X-axis:** Last 6 months
- **Y-axis:** Access count
- **Tooltip:** Month · Total accesses: N · Unique resources: N · Unique branches: N
- **Export:** PNG

### 7.2 Resource Distribution by Type
- **Type:** Donut chart
- **Data:** Resource count by type in catalogue
- **Segments:** E-Book · Video Lecture · Question Bank · Past Paper · Reference · Revision Notes · Other
- **Tooltip:** Type · Resources: N · Downloads this month: N
- **Centre text:** Total resources
- **Export:** PNG

---

## 8. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Resource added | "Resource [Title] added to catalogue. Access assigned to [N] branches." | Success | 4s |
| Resource updated | "Resource [Title] updated. Version [N] saved." | Success | 4s |
| Resource archived | "[Title] archived and removed from branch access." | Warning | 6s |
| Request fulfilled | "Resource request fulfilled. [Branch] notified." | Success | 4s |
| Request declined | "Request declined. Branch notified with reason." | Success | 4s |
| File too large | "File exceeds 500MB limit. Compress or use an external URL." | Warning | 6s |
| Export started | "Usage report generating…" | Info | 4s |

---

## 9. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No resources in catalogue | "Catalogue is empty" | "Add your first digital resource to the central library" | [+ Add Resource] |
| No pending requests | "No resource requests pending" | "Branch requests for new resources will appear here" | — |
| No downloads this month | "No access activity this month" | "Resource download data will appear once branches start accessing the library" | — |

---

## 10. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: 6 KPI cards + resources table (5 rows) + branch table (5 rows) + request table + charts |
| Table filter/search | Inline skeleton rows |
| Resource create drawer open | Spinner in drawer |
| File upload (in drawer) | Progress bar in file upload field |
| Submit resource | Spinner in submit button |
| KPI auto-refresh | Shimmer on card values |

---

## 11. Role-Based UI Visibility

| Element | Library Head G2 | Academic Dir G3 (read) | Others |
|---|---|---|---|
| Page | ✅ | ✅ read-only via own dashboard | ❌ redirect |
| [+ Add Resource] header button | ✅ | ❌ | ❌ |
| [Fulfil] / [Decline] requests | ✅ | ❌ | ❌ |
| [Edit] on catalogue resources | ✅ | ❌ | ❌ |
| [Archive] on resources | ✅ | ❌ | ❌ |
| [Export Usage Report] | ✅ | ✅ | ❌ |
| Branch access table (view) | ✅ | ✅ | ❌ |

> G2 can manage content; cannot access user provisioning, finance, compliance, or HR pages.

---

## 12. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/library/head/dashboard/` | JWT (G2 Library) | Full dashboard |
| GET | `/api/v1/group/{id}/library/head/kpi/` | JWT (G2) | KPI auto-refresh |
| GET | `/api/v1/group/{id}/library/resources/?recent=true&days=30` | JWT (G2) | Recently added resources |
| GET | `/api/v1/group/{id}/library/branches/access/` | JWT (G2) | Branch access overview |
| GET | `/api/v1/group/{id}/library/requests/?status=pending` | JWT (G2) | Resource request queue |
| POST | `/api/v1/group/{id}/library/resources/` | JWT (G2) | Add resource to catalogue |
| PUT | `/api/v1/group/{id}/library/resources/{rid}/` | JWT (G2) | Update resource |
| POST | `/api/v1/group/{id}/library/resources/{rid}/archive/` | JWT (G2) | Archive resource |
| POST | `/api/v1/group/{id}/library/requests/{reqid}/fulfil/` | JWT (G2) | Fulfil resource request |
| POST | `/api/v1/group/{id}/library/requests/{reqid}/decline/` | JWT (G2) | Decline request with reason |
| GET | `/api/v1/group/{id}/library/resources/top-usage/?month=current` | JWT (G2) | Top 8 resources this month |
| GET | `/api/v1/group/{id}/library/analytics/monthly-downloads/` | JWT (G2) | Download trend chart |
| GET | `/api/v1/group/{id}/library/analytics/type-distribution/` | JWT (G2) | Catalogue type distribution |

---

## 13. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Branch access table search | `input delay:300ms` | GET `.../library/branches/access/?q=` | `#branch-table-body` | `innerHTML` |
| Request queue filter | `click` | GET `.../library/requests/?status=pending&filters=` | `#request-table-section` | `innerHTML` |
| Open resource create drawer | `click` | GET `.../library/resources/create-form/` | `#drawer-body` | `innerHTML` |
| Submit resource form | `submit` | POST `.../library/resources/` | `#drawer-body` | `innerHTML` |
| Fulfil request (opens create) | `click` | GET `.../library/requests/{id}/fulfil-form/` | `#drawer-body` | `innerHTML` |
| KPI auto-refresh | `every 5m` | GET `.../library/head/kpi/` | `#kpi-bar` | `innerHTML` |
| Pagination | `click` | GET `.../library/branches/access/?page=` | `#branch-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
