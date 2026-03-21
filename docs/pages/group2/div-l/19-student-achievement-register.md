# 19 — Student Achievement Register

> **URL:** `/group/extracurricular/achievements/`
> **File:** `19-student-achievement-register.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P2
> **Roles:** Sports Director G3 (sports achievements) · Cultural Activities Head G3 (cultural achievements) · NSS/NCC Coordinator G3 (NSS/NCC achievements) · Branch Staff G2 (view own branch achievements)

---

## 1. Purpose

Group-wide cross-division register of individual student achievements across sports, cultural, NSS/NCC, and extra-curricular domains. Serves as the definitive record for achievement certificates, scholarship eligibility, college recommendation letters, and school-level recognition. Aggregates wins from tournaments (Division L pages 7–8), competition results (pages 12–13), NSS certificates (page 14), NCC certificates (page 15), and manually recorded achievements (state/national awards).

This is a read-aggregation and manual-entry page — records flow in automatically from linked domain pages but can also be added manually for achievements from external events not tracked elsewhere in the portal.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Sports Director | G3 | Full for sports achievements — add, edit, approve | |
| Cultural Activities Head | G3 | Full for cultural achievements | |
| NSS/NCC Coordinator | G3 | Full for NSS/NCC achievements | |
| Branch Staff (Teachers) | Branch G2 | View own branch student achievements | No edit access |
| Branch Principal | Branch G3 | View and export own branch achievements | |
| All others | — | — | No access |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Student Achievement Register
```

### 3.2 Page Header
```
Student Achievement Register                       [+ Add Achievement]  [Export ↓]
AY [academic year]  ·  [N] Achievements  ·  [N] Students  ·  [N] Branches
```

### 3.3 Summary Stats Bar

| Stat | Value |
|---|---|
| Total Achievements This AY | N |
| Sports | N |
| Cultural | N |
| NSS / NCC | N |
| Other | N |
| Students with ≥ 1 Achievement | N |
| Group/State/National Level | N |

---

## 4. Achievements Table

**Search:** Student name, achievement, event, branch. Debounce 300ms.

**Advanced Filters:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Domain | Multi-select | Sports · Cultural · NSS · NCC · Academic · Other |
| Level | Multi-select | Branch · Group · Zonal · District · State · National · International |
| Position | Multi-select | 1st · 2nd · 3rd · Participation · Certificate · Special Award |
| Class / Grade | Multi-select | Class 1–12 |
| Gender | Multi-select | Boys · Girls |
| Date Range | Date range | |
| Source | Multi-select | Auto-imported · Manually Added |

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Student Name | Text | ✅ | |
| Class | Text | ✅ | |
| Branch | Text | ✅ | |
| Achievement | Text | ✅ | e.g. "1st Place — State Debate Championship" |
| Domain | Badge | ✅ | Sports / Cultural / NSS / NCC / Other |
| Level | Badge | ✅ | Colour-coded by prestige |
| Position | Badge | ✅ | |
| Event / Programme | Text | ✅ | |
| Date | Date | ✅ | |
| Source | Badge | ✅ | Auto · Manual |
| Certificate | Badge | ✅ | ✅ Generated · ❌ Pending |
| Actions | — | ❌ | View · Edit · Generate Certificate (domain heads only) |

**Default sort:** Date descending.

**Pagination:** 25/page.

---

## 5. Drawers & Modals

### 5.1 Drawer: `achievement-add`
- **Width:** 560px

**Fields:**

| Field | Type | Required | Validation |
|---|---|---|---|
| Student | Search + select | ✅ | From group student list |
| Domain | Select | ✅ | Sports · Cultural · NSS · NCC · Academic · Other |
| Achievement Title | Text | ✅ | Min 5, max 300 |
| Event / Competition Name | Text | ✅ | |
| Level | Select | ✅ | Branch · Group · Zonal · District · State · National · International |
| Position / Award | Select | ✅ | 1st · 2nd · 3rd · Participation · Certificate · Special Award |
| Date | Date | ✅ | Not future |
| Organising Body | Text | ❌ | e.g. "CBSE", "State Sports Authority" |
| Description | Textarea | ❌ | Max 300 chars |
| Supporting Document | File upload | ❌ | PDF/JPG max 10MB |
| Photo | File upload | ❌ | JPG/PNG max 5MB |

**Buttons:** [Save Achievement] + [Cancel]

### 5.2 Drawer: `achievement-detail`
- **Width:** 640px
- **Tabs:** Overview · Documents · Certificate

#### Tab: Overview
Full achievement details. [Edit] button (domain heads only for their domain).

Student summary card: Name · Class · Branch · Photo · Total achievements count.

#### Tab: Documents
Uploaded supporting documents (certificates, news clips, photos). [Upload Document] button (domain heads).

#### Tab: Certificate
- If achievement qualifies: [Generate Achievement Certificate PDF] button
- Preview: Student name, achievement, event, position, date, group seal
- Download after generation
- Re-generate option if name/details need correction

### 5.3 Modal: `delete-achievement`
- **Width:** 400px
- **Content:** "Delete this achievement record? This cannot be undone."
- **Fields:** Reason (required, min 10 chars)
- **Buttons:** [Delete] (danger) + [Cancel]

---

## 6. Charts

### 6.1 Achievements by Domain and Level (current AY)
- **Type:** Stacked horizontal bar
- **Y-axis:** Domains (Sports / Cultural / NSS / NCC / Other)
- **Stacks:** Branch / Group / District / State / National
- **Export:** PNG

### 6.2 Top Achieving Branches (current AY)
- **Type:** Horizontal bar
- **Data:** Total achievement count per branch (all domains)
- **Export:** PNG

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Achievement added | "Achievement recorded for [Student Name]." | Success | 4s |
| Achievement updated | "Achievement updated." | Success | 4s |
| Certificate generated | "Achievement certificate generated for [Student Name]." | Success | 4s |
| Achievement deleted | "Achievement record deleted." | Warning | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No achievements this AY | "No achievements recorded" | "Add achievements from sports, cultural, and NSS/NCC activities" | [+ Add Achievement] |
| No results for filters | "No achievements match your filters" | | [Clear Filters] |
| No certificates generated | "Certificates not yet generated" | "Generate certificates for qualifying achievements" | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: stats bar + table (8 rows) + charts |
| Filter/search | Inline skeleton rows |
| Certificate generation | Spinner in button |
| Document upload | Progress bar |
| Drawer open | Spinner in drawer |

---

## 10. Role-Based UI Visibility

| Element | Domain Head G3 (own domain) | Branch Staff G2 (view) |
|---|---|---|
| [+ Add Achievement] | ✅ (own domain) | ❌ |
| [Edit Achievement] | ✅ (own domain) | ❌ |
| [Delete Achievement] | ✅ (own domain) | ❌ |
| [Generate Certificate] | ✅ (own domain) | ❌ |
| View all branches | ✅ | Own branch only |
| [Export] | ✅ | ✅ (own branch data) |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/achievements/` | JWT (G3) | Achievements list |
| POST | `/api/v1/group/{id}/achievements/` | JWT (G3 Domain) | Add achievement |
| GET | `/api/v1/group/{id}/achievements/{aid}/` | JWT (G3) | Achievement detail |
| PUT | `/api/v1/group/{id}/achievements/{aid}/` | JWT (G3 Domain) | Update achievement |
| DELETE | `/api/v1/group/{id}/achievements/{aid}/` | JWT (G3 Domain) | Delete achievement |
| POST | `/api/v1/group/{id}/achievements/{aid}/certificate/` | JWT (G3 Domain) | Generate certificate |
| POST | `/api/v1/group/{id}/achievements/{aid}/documents/` | JWT (G3 Domain) | Upload supporting document |

---

## 12. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Table search | `input delay:300ms` | GET `.../achievements/?q=` | `#achievement-table-body` | `innerHTML` |
| Filter apply | `click` | GET `.../achievements/?filters=` | `#achievement-table-section` | `innerHTML` |
| Open achievement detail | `click` | GET `.../achievements/{id}/` | `#drawer-body` | `innerHTML` |
| Drawer tab switch | `click` | GET `.../achievements/{id}/{tab}/` | `#drawer-tab-content` | `innerHTML` |
| Submit add form | `submit` | POST `.../achievements/` | `#drawer-body` | `innerHTML` |
| Pagination | `click` | GET `.../achievements/?page=` | `#achievement-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
