# 10 — Sports Equipment Inventory

> **URL:** `/group/sports/equipment/`
> **File:** `10-sports-equipment-inventory.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P2
> **Roles:** Sports Coordinator G3 (Role 98, full — manage inventory and approve branch requests) · Sports Director G3 (Role 97, view + approve large purchases)

---

## 1. Purpose

Group-wide inventory of sports equipment across all branches. Every branch maintains its own physical equipment — balls, bats, nets, protective gear, track and field apparatus, mats, and more — but the Sports Coordinator at group level oversees stock levels, condition grades, audit compliance, and procurement requests flowing up from branches. When a branch raises an equipment request, it goes to the Sports Coordinator for review and recommendation, who then forwards approved requests to the Group Procurement function. The Sports Director holds a view role on day-to-day inventory but must be looped in for large-value or urgent procurement decisions. Scale: 20–200 equipment types per branch × up to 50 branches = up to 10,000 equipment line items group-wide, making search, pagination, and branch-level filtering critical for usability. Last audit dates older than 180 days are flagged red to prompt branch-level re-auditing before tournaments.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Sports Coordinator | G3, Role 98 | Full — create inventory items, log maintenance, approve or decline branch requests, recommend procurement | Primary operator of this page |
| Sports Director | G3, Role 97 | View inventory + approve large purchase requests | Cannot create items or log maintenance; can approve procurement requests flagged as Urgent |
| Group Cultural Activities Head | G3, Role 99 | No access | 403 on direct URL |
| All other roles | — | No access | 403 on direct URL |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Sports Equipment Inventory
```

### 3.2 Page Header
```
Sports Equipment Inventory                    [+ Add Inventory Item]  [Export ↓]
[N] Item Types  ·  [N] Pending Requests  ·  [N] Items Due for Replacement
```

`[+ Add Inventory Item]` — opens `inventory-item-create` drawer (Role 98 only).
`[Export ↓]` — exports filtered inventory to XLSX/PDF; available to Roles 97 and 98.

**Subtitle bar:** Branch selector (multi-select; default = All Branches). Changing selection reloads Section 5.1 via HTMX. Sports Coordinator sees all branches; no restriction.

### 3.3 Alert Banners

Stacked above the KPI bar. Each banner individually dismissible for the session.

| Condition | Banner Text | Severity |
|---|---|---|
| Items with Condemned condition | "[N] item(s) across [B] branch(es) are condemned and should be removed from active stock." | Red |
| Items not audited in > 180 days | "[N] item(s) have not been audited in more than 180 days. Schedule a branch audit." | Amber |
| Pending procurement requests > 7 days old | "[N] procurement request(s) have been pending for more than 7 days without a decision." | Amber |
| Branches with zero equipment logged | "[N] branch(es) have no equipment items logged in the inventory." | Amber |
| No inventory items in system | "No equipment has been logged in the inventory. Add the first item to begin." | Blue |

---

## 4. KPI Summary Bar

Five cards displayed horizontally below the alert banners. Auto-refresh every 5 minutes via HTMX polling (`hx-trigger="every 5m"`).

| Card | Metric | Colour Rule | Drill-down |
|---|---|---|---|
| Total Item Types | Count of distinct equipment line items across all branches | Blue (neutral) | Filters Section 5.1 table to all items |
| Items Due for Replacement | Count of items where Condition = Poor or Condemned | Red if > 0; Green if 0 | Filters table to Condition = Poor or Condemned |
| Pending Requests | Count of branch procurement requests in Pending status | Red if > 5; Amber if 1–5; Green if 0 | Scrolls to Section 5.2 Pending Requests table |
| Branches with Zero Equipment Logged | Count of branches with no inventory records | Red if > 0; Green if 0 | Opens branch coverage modal (list of branches) |
| Items Under Maintenance | Count of items with an open maintenance log (not yet resolved) | Amber if > 0; Green if 0 | Filters table to items in maintenance state |

---

## 5. Sections

### 5.1 Equipment Inventory

**Display note:** Main inventory table below the KPI bar. Shows all equipment items for the branches selected in the subtitle bar selector. Row selection enabled for bulk export.

**Search:** Item name, sport name, branch name. Debounce 300 ms. Cleared with × icon.

**Filters:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches in group |
| Sport | Multi-select | All sports (dynamic from sport master) |
| Category | Multi-select | Ball Equipment · Protective Gear · Track & Field · Net · Goal · Mat · Other |
| Condition | Multi-select | Good · Fair · Poor · Condemned |
| Stock Level | Select | All · Normal · Low (< 50% of standard quantity) · Critical (≤ 2 units) |

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Item Name | Text + link | Yes | Opens `inventory-item-detail` modal (read-only view) |
| Sport | Badge (colour-coded) | Yes | |
| Category | Text | Yes | |
| Branch | Text + link | Yes | Links to branch detail page |
| Quantity Total | Number | Yes | Total items logged |
| Quantity Available | Number | Yes | Total minus items in maintenance or condemned |
| Condition | Badge | Yes | Good (green) · Fair (yellow) · Poor (orange) · Condemned (red) |
| Last Audit Date | Date | Yes | Red text if > 180 days ago; "Never" if no audit logged |
| Actions | Button group | No | View · Edit · Log Maintenance · Request Procurement |

**Action notes:**
- View — always visible to Roles 97 and 98; opens 480 px item detail modal (read-only)
- Edit — Role 98 only; opens `inventory-item-create` drawer in edit mode
- Log Maintenance — Role 98 only; opens `maintenance-log` modal pre-filled with item details
- Request Procurement — Role 98 only; opens `equipment-request` drawer pre-filled with item details

**Default sort:** Condition ascending (Condemned first, then Poor, then Fair, then Good) so worst-condition items surface first.

**Pagination:** Server-side · 25 rows per page.

---

### 5.2 Pending Equipment Requests

**Display note:** Separate table section below Section 5.1. Header: "Branch Equipment Requests — [N] Pending". Shows all branch-originated procurement requests awaiting Coordinator decision. Always visible when Pending count > 0; collapsible when count = 0.

**Search:** Item name, branch name. Debounce 300 ms.

**Filters:**

| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All branches |
| Priority | Multi-select | Urgent · Normal |
| Sport | Multi-select | All sports |

**Columns:**

| Column | Type | Sortable | Notes |
|---|---|---|---|
| Request ID | Text | No | Auto-generated reference (e.g. REQ-2026-0041) |
| Branch | Text | Yes | |
| Item Requested | Text | Yes | |
| Sport | Badge | Yes | |
| Quantity | Number | Yes | |
| Justification | Text (truncated) | No | First 80 characters; [More] expands inline |
| Priority | Badge | Yes | Urgent (red) · Normal (grey) |
| Submitted By | Text | Yes | Staff name |
| Days Pending | Number | Yes | Red if > 7 days |
| Actions | Button group | No | Approve · Decline · View |

**Action notes:**
- Approve — Role 98 (normal requests); Role 97 and 98 (Urgent requests) — opens `approve-request` modal (420 px): Request summary, Recommended Supplier (text, optional), Notes (textarea, optional), [Confirm Approval] (green) / [Cancel]
- Decline — Role 98 — opens `decline-request` modal (420 px): Decline Reason (textarea, required, min 20 characters), [Confirm Decline] (red danger) / [Cancel]
- View — always; opens full request detail in 480 px modal including all justification text and any uploaded files

**Default sort:** Days Pending descending (longest-pending first).

**Pagination:** Server-side · 25 rows per page.

---

## 6. Drawers & Modals

### Drawer: `equipment-request`
- **Trigger:** [Request Procurement] row action in Section 5.1, or standalone request from branch staff
- **Width:** 480 px
- **Tabs:** Item · Quantity · Branch · Justification

#### Tab: Item
| Field | Type | Required | Validation |
|---|---|---|---|
| Item Name | Text | Yes | Min 3, max 150 characters |
| Sport | Select | Yes | From sport master |
| Category | Select | Yes | Ball Equipment · Protective Gear · Track & Field · Net · Goal · Mat · Other |
| Unit | Select | Yes | Piece · Set · Pair · Kit |

#### Tab: Quantity
| Field | Type | Required | Validation |
|---|---|---|---|
| Quantity Requested | Number | Yes | Integer ≥ 1 |
| Estimated Unit Cost | Currency (INR) | No | Positive decimal; used for procurement budgeting |
| Preferred Brand | Text | No | Max 100 characters |

#### Tab: Branch
| Field | Type | Required | Validation |
|---|---|---|---|
| Branch | Select | Yes | Pre-filled if request originated from a branch item row; otherwise required select |
| Delivery Address | Textarea | No | Max 300 characters |

#### Tab: Justification
| Field | Type | Required | Validation |
|---|---|---|---|
| Reason for Request | Textarea | Yes | Min 30, max 500 characters |
| Priority | Select | Yes | Urgent · Normal |
| Supporting Evidence | File upload | No | PDF or image (JPG/PNG); max 5 MB |

---

### Drawer: `inventory-item-create`
- **Trigger:** `[+ Add Inventory Item]` header button, or [Edit] row action
- **Width:** 480 px
- **Tabs:** None (single-page form)

| Field | Type | Required | Validation |
|---|---|---|---|
| Item Name | Text | Yes | Min 3, max 150 characters |
| Sport | Select | Yes | From sport master |
| Category | Select | Yes | Ball Equipment · Protective Gear · Track & Field · Net · Goal · Mat · Other |
| Branch | Select | Yes | From group branch list |
| Quantity | Number | Yes | Integer ≥ 1 |
| Condition | Select | Yes | Good · Fair · Poor · Condemned |
| Purchase Date | Date | No | Must not be in the future |
| Supplier | Text | No | Max 150 characters |
| Cost Per Unit | Currency (INR) | No | Positive decimal |
| Location / Storage | Text | No | Max 100 characters (e.g. "Sports Store Room B2") |
| Notes | Textarea | No | Max 300 characters |

**Buttons:** [Save Item] (primary) · [Cancel] (ghost). Inline validation on all required fields before submit.

---

### Modal: `maintenance-log`
- **Width:** 420 px
- **Item details pre-filled:** Item Name, Branch, Sport, Current Condition — displayed read-only at top of modal.

| Field | Type | Required | Validation |
|---|---|---|---|
| Issue Description | Textarea | Yes | Min 20, max 500 characters |
| Action Taken | Select | Yes | Repaired · Replaced · Condemned · Cleaned |
| Date | Date | Yes | Must not be in the future |
| Cost | Currency (INR) | No | Positive decimal |
| Next Service Date | Date | No | Must be after Date field |

**Buttons:** [Save Log] (primary) · [Cancel] (ghost).

On save: If Action Taken = Condemned, the item's Condition in inventory is updated to Condemned automatically. A confirmation note is shown: "This item will be marked as Condemned in the inventory."

---

## 7. Charts

No charts for this page. This is a P2 operations management page where table-driven search and action efficiency takes precedence over analytics visualisation. Chart.js charts for equipment analytics are available on the Sports Director Dashboard (page 01).

---

## 8. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Inventory item created | "[Item Name] added to inventory for [Branch]." | Success | 4 s |
| Inventory item updated | "[Item Name] updated." | Success | 4 s |
| Maintenance log saved | "Maintenance log saved for [Item Name] at [Branch]." | Info | 4 s |
| Item condemned via maintenance | "[Item Name] has been marked as Condemned." | Warning | 6 s |
| Procurement request submitted | "Equipment request submitted for [Item Name] — [Branch]." | Success | 4 s |
| Request approved | "Request [REQ-ID] approved. Branch notified." | Success | 4 s |
| Request declined | "Request [REQ-ID] declined. Branch notified with reason." | Info | 4 s |
| Validation error | "Please correct the highlighted fields before saving." | Error | 5 s |

---

## 9. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No inventory items in system | "No equipment logged" | "Add sports equipment items to begin tracking inventory across branches." | [+ Add Inventory Item] |
| No items match filters | "No items found" | "Try adjusting the branch, sport, category, or condition filters." | [Clear Filters] |
| No pending requests (Section 5.2) | "No pending requests" | "All branch equipment requests have been actioned." | — |
| Branch has zero items | "No equipment logged for this branch" | "Log the first inventory item for [Branch] or ask the branch to submit a procurement request." | [+ Add Inventory Item] |

---

## 10. Loader States

| Trigger | Loader Type |
|---|---|
| Page initial load | Skeleton: KPI bar (5 cards) + alert banners + Section 5.1 table (10 rows) + Section 5.2 table (5 rows) |
| Table filter or search change (Section 5.1) | Inline skeleton rows replacing Section 5.1 table body |
| Table filter or search change (Section 5.2) | Inline skeleton rows replacing Section 5.2 table body |
| KPI auto-refresh (every 5 min) | Spinner icon on each KPI card |
| Branch selector change | Spinner over Section 5.1 table while data reloads |
| Inventory item drawer open | Spinner centred in drawer body |
| Maintenance log modal open | Spinner in modal body while item data pre-fills |
| Request approve/decline submit | Spinner inside modal action button; button disabled during submit |
| File upload in equipment-request | Progress bar below file upload field |

---

## 11. Role-Based UI Visibility

| Element | Sports Director G3 (97) | Sports Coordinator G3 (98) |
|---|---|---|
| [+ Add Inventory Item] | Hidden | Visible |
| [Export ↓] | Visible | Visible |
| [Edit] row action (Section 5.1) | Hidden | Visible |
| [Log Maintenance] row action | Hidden | Visible |
| [Request Procurement] row action | Hidden | Visible |
| [Approve] in Section 5.2 (Urgent requests) | Visible | Visible |
| [Approve] in Section 5.2 (Normal requests) | Hidden | Visible |
| [Decline] in Section 5.2 | Hidden | Visible |
| [View] in Section 5.2 | Visible | Visible |
| KPI drill-down links | Visible | Visible |
| Branch selector subtitle bar | Visible (read/filter) | Visible (read/filter) |

---

## 12. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{gid}/sports/equipment/` | JWT (Role 97, 98) | Paginated equipment inventory with filters |
| POST | `/api/v1/group/{gid}/sports/equipment/` | JWT (Role 98) | Create inventory item |
| GET | `/api/v1/group/{gid}/sports/equipment/{eid}/` | JWT (Role 97, 98) | Item detail |
| PUT | `/api/v1/group/{gid}/sports/equipment/{eid}/` | JWT (Role 98) | Update inventory item |
| DELETE | `/api/v1/group/{gid}/sports/equipment/{eid}/` | JWT (Role 98) | Delete item (only if no maintenance history) |
| POST | `/api/v1/group/{gid}/sports/equipment/{eid}/maintenance/` | JWT (Role 98) | Log maintenance entry |
| GET | `/api/v1/group/{gid}/sports/equipment/{eid}/maintenance/` | JWT (Role 97, 98) | Maintenance history for item |
| GET | `/api/v1/group/{gid}/sports/equipment/requests/` | JWT (Role 97, 98) | Paginated procurement requests with filters |
| POST | `/api/v1/group/{gid}/sports/equipment/requests/` | JWT (Role 98) | Submit procurement request |
| GET | `/api/v1/group/{gid}/sports/equipment/requests/{rid}/` | JWT (Role 97, 98) | Request detail |
| POST | `/api/v1/group/{gid}/sports/equipment/requests/{rid}/approve/` | JWT (Role 97, 98) | Approve request |
| POST | `/api/v1/group/{gid}/sports/equipment/requests/{rid}/decline/` | JWT (Role 98) | Decline request with reason |
| GET | `/api/v1/group/{gid}/sports/equipment/kpi/` | JWT (Role 97, 98) | KPI card values |

---

## 13. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Item name/sport/branch search (Section 5.1) | `input delay:300ms` | GET `/group/{gid}/sports/equipment/?q={val}` | `#inventory-table-body` | `innerHTML` |
| Filter apply (Section 5.1) | `change` | GET `/group/{gid}/sports/equipment/?filters={encoded}` | `#inventory-table-section` | `innerHTML` |
| Branch selector change | `change` | GET `/group/{gid}/sports/equipment/?branches={encoded}` | `#inventory-table-section` | `innerHTML` |
| Search (Section 5.2 requests) | `input delay:300ms` | GET `/group/{gid}/sports/equipment/requests/?q={val}` | `#requests-table-body` | `innerHTML` |
| Filter apply (Section 5.2) | `change` | GET `/group/{gid}/sports/equipment/requests/?filters={encoded}` | `#requests-table-section` | `innerHTML` |
| KPI auto-refresh | `every 5m` | GET `/group/{gid}/sports/equipment/kpi/` | `#kpi-bar` | `innerHTML` |
| Open inventory item drawer | `click` | GET `/group/{gid}/sports/equipment/{eid}/drawer/` | `#drawer-body` | `innerHTML` |
| Approve request inline | `click` | POST `/group/{gid}/sports/equipment/requests/{rid}/approve/` | `#request-row-{rid}` | `outerHTML` |
| Pagination (Section 5.1) | `click` | GET `/group/{gid}/sports/equipment/?page={n}` | `#inventory-table-section` | `innerHTML` |
| Pagination (Section 5.2) | `click` | GET `/group/{gid}/sports/equipment/requests/?page={n}` | `#requests-table-section` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
