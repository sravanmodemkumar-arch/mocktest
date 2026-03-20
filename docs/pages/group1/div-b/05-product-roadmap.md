# 05 — Product Roadmap

## 1. Platform Scale Reference

| Dimension | Value |
|---|---|
| Total institutions tracked for roadmap input | 2,050 |
| Feature requests from institutions (annual) | ~400–600 requests |
| Roadmap epics (active) | ~12–18 per quarter |
| Features per epic | 3–10 |
| Product team members | 3 PMs across 3 domains |
| Engineering capacity (sprints/quarter) | ~6 sprints × 2-week cycles |
| Releases per quarter | 6–8 |
| Quarterly OKRs tracked | 4–6 objectives |

**Why this page matters at scale:** With 3 PMs owning 26 pages of product surface across 2,050 institutions and 6 exam domains, prioritisation discipline is critical. Without a shared roadmap, each PM independently queues work and Engineering gets conflicting priorities. This page is the contract between Product and Engineering — what ships when, in which release, and why. Institution CSMs (Division J) use the roadmap to set client expectations. Executives (Division A) use it to track OKR delivery.

---

## 2. Page Metadata

| Field | Value |
|---|---|
| Page title | Product Roadmap |
| Route | `/product/roadmap/` |
| Django view class | `ProductRoadmapView` |
| Template | `product/roadmap.html` |
| Permission — view | `portal.view_roadmap` (all div-b roles + read access for div-a executives) |
| Permission — manage | `portal.manage_roadmap` (PM Platform · PM Exam Domains · PM Institution Portal) |
| 2FA required | No |
| HTMX poll | None (on-demand) |
| Nav group | Product |
| Nav icon | `map` |
| Priority | P2 |

---

## 3. Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Product Roadmap     [+ New Epic]  [Kanban ⇄ Timeline]  [Filter ▾]  [Share] │
├────────┬────────┬────────┬────────┬────────┬──────────────────────────────────────┤
│ Epics  │ Feature│ In     │ Done   │ OKR    │ Capacity Used                        │
│  18    │  s: 94 │ Progress│ Q1: 42 │Score  │ Q1: ████████████████░░  82%          │
│        │        │   12   │        │ 74/100 │                                      │
├────────┴────────┴────────┴────────┴────────┴──────────────────────────────────────┤
│ TABS: [Kanban Board] [Timeline (Gantt)] [Backlog] [OKRs] [Institution Requests]   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ VIEW TOGGLE: [Q1 2026] [Q2 2026] [Q3 2026] [All]      [Domain: All ▾] [PM: All ▾]│
├─────────────────────────────────────────────────────────────────────────────────────┤
│ KANBAN:  Backlog │ Planned │ In Development │ In Review │ Done                     │
│          [8]    │  [12]   │     [6]        │   [3]     │ [42]                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Sections — Deep Specification

### 4.1 KPI Strip

| # | Card | Value | Detail |
|---|---|---|---|
| 1 | Active Epics | `18` | Across all 3 PM domains |
| 2 | Total Features | `94` | Across all active epics |
| 3 | In Progress | `12` | Currently in dev |
| 4 | Done (Q1) | `42` | Completed this quarter |
| 5 | OKR Score | `74/100` | Composite OKR health score |
| 6 | Capacity Used | `82%` | Engineering sprint capacity this quarter |

---

### 4.2 Tab Bar

| Tab | Description |
|---|---|
| Kanban Board | Feature cards in Backlog/Planned/In Dev/In Review/Done columns |
| Timeline (Gantt) | Horizontal Gantt chart — epics as rows, quarters as X-axis |
| Backlog | Prioritised list of all unplanned features with scoring |
| OKRs | Q1/Q2 Objectives and Key Results with progress tracking |
| Institution Requests | Feature requests submitted by institutions, linked to roadmap items |

---

### 4.3 View Controls

**Quarter selector:** `[Q1 2026] [Q2 2026] [Q3 2026] [All]`
Active quarter: `bg-[#6366F1] text-white rounded px-3 py-1`

**Domain filter:** `[All ▾]` dropdown
Options: All · PM Platform · PM Exam Domains · PM Institution Portal

**PM filter:** `[All ▾]`
Options: All · individual PM names

**[Share]** button: generates a read-only public link with token (for stakeholders outside div-b)

---

### 4.4 Tab: Kanban Board

**Layout:** `grid grid-cols-5 gap-4 p-4`

**Columns:**

| Column | Status | Max WIP | Header colour |
|---|---|---|---|
| Backlog | `backlog` | Unlimited | `text-[#475569]` |
| Planned | `planned` | 20 | `text-[#94A3B8]` |
| In Development | `development` | 10 | `text-[#F59E0B]` |
| In Review | `review` | 5 | `text-[#6366F1]` |
| Done | `done` | Unlimited | `text-[#10B981]` |

**WIP limit warning:** If column exceeds max WIP, header turns amber with count badge `⚠ 11/10`

#### 4.4.1 Feature Card

`bg-[#0D1526] rounded-xl border border-[#1E2D4A] p-3 mb-2 cursor-pointer hover:border-[#6366F1]`

**Card layout:**
```
[Epic badge]                          [Priority badge]
Feature title (2 lines max)
[Domain badge]  [PM avatar]           [Story points]
[Release badge]
[Progress bar if In Dev]
[Linked institution requests: N]
```

**Epic badge:** `text-[10px] bg-[#312E81] text-[#A5B4FC] px-1.5 py-0.5 rounded`

**Priority badges:**
- P0 Critical: `bg-[#EF4444] text-white animate-pulse text-[10px]`
- P1 High: `bg-[#450A0A] text-[#F87171] text-[10px]`
- P2 Medium: `bg-[#451A03] text-[#FCD34D] text-[10px]`
- P3 Low: `bg-[#1E2D4A] text-[#94A3B8] text-[10px]`

**Domain badge:**
- PM Platform: `bg-[#0C4A6E] text-[#7DD3FC]`
- PM Exam Domains: `bg-[#064E3B] text-[#6EE7B7]`
- PM Institution Portal: `bg-[#3B1764] text-[#D8B4FE]`

**Story points:** Fibonacci scale `1 · 2 · 3 · 5 · 8 · 13 · 21`
`text-xs bg-[#1E2D4A] text-[#94A3B8] px-1.5 py-0.5 rounded`

**Release badge:** `text-[10px] font-mono bg-[#131F38] text-[#94A3B8]` — e.g., `v2.4.1`

**Progress bar** (In Development only):
`bg-[#1E2D4A] rounded-full h-1 mt-2`
Fill: `bg-[#6366F1]` · percentage from sub-tasks

**Institution requests count:** `text-[10px] text-[#94A3B8]` `📊 12 institutions requested`

**Card click:** opens Feature Detail Drawer (560px)

**Drag-and-drop:** `draggable="true"` · visual drop zone per column · `hx-post="?action=move_feature"`

---

### 4.5 Tab: Timeline (Gantt)

**Layout:** `overflow-x-auto`

**Y-axis (rows):** Epics grouped by domain
**X-axis (columns):** Weeks/months across selected quarters
**Time scale toggle:** [Weeks] [Months] [Quarters]

**Epic row:**
`bg-[#0D1526] border-b border-[#1E2D4A]`
- Epic name (fixed 240px left)
- Epic bar: `bg-[#312E81] rounded h-6 relative`
  - Width = duration in time units
  - Hover tooltip: Epic name · Start · End · Feature count · Owner
  - Click: expands epic row to show individual feature bars below

**Feature bar (inside epic):**
`bg-[#6366F1]/60 rounded h-4`
Status overlay colours:
- Done: `bg-[#10B981]`
- In Dev: `bg-[#6366F1]`
- Planned: `bg-[#6366F1]/40`
- Blocked: `bg-[#EF4444]/60` with `⚠` indicator

**Today line:** `border-l-2 border-[#EF4444] border-dashed` vertical line

**Quarter dividers:** `border-l border-[#1E2D4A]` with quarter label at top

**Milestone markers:** diamond shapes `◆` on timeline for release dates (from Release Manager)

**Zoom controls:** [−] [+] · `min-width: 800px`

---

### 4.6 Tab: Backlog

**Purpose:** Prioritised queue of all unplanned features with RICE scoring.

#### 4.6.1 RICE Score Display

Each feature has an auto-computed RICE score:
```
RICE = (Reach × Impact × Confidence) / Effort

Reach:      how many institutions benefit (0–2,050)
Impact:     1=minimal · 2=low · 3=medium · 4=high · 5=massive
Confidence: 0–100% (how certain are we)
Effort:     story points (1–21)
```

**Score display:** `text-sm font-mono text-[#6366F1]` · sorted by score descending by default

#### 4.6.2 Backlog Table

| Column | Detail |
|---|---|
| # | Priority rank (by RICE score) |
| Feature | Title + epic badge + domain badge |
| RICE Score | Computed value `text-[#6366F1] font-mono` |
| Reach | Institution count |
| Impact | 1–5 scale with label |
| Confidence | % value |
| Effort | Story points |
| Requested By | Institution count linked |
| Quarter Target | Dropdown (editable) |
| Actions ⋯ | Edit · Move to Planned · Archive |

**Sort:** RICE score desc by default · click column header to change sort
**Filter:** Domain · Priority · Quarter target · Story points range

**[Prioritise with AI]** button (PM Platform only):
`hx-post="?action=ai_prioritise"` — calls internal scoring model, re-ranks backlog, shows diff preview before confirming

---

### 4.7 Tab: OKRs

**Purpose:** Track quarterly Objectives and Key Results against roadmap delivery.

#### 4.7.1 OKR Summary

Current quarter OKRs: 4 objectives

Each objective card:
`bg-[#0D1526] rounded-xl border border-[#1E2D4A] p-4 mb-4`

**Objective header:**
- Objective title: `text-base font-semibold text-[#F1F5F9]`
- Owner: PM name badge
- Overall progress: percentage + semicircle arc gauge (SVG)
  - Green ≥ 80% · Amber 50–79% · Red < 50%

**Key Results (under each objective):**

| KR | Target | Current | Progress |
|---|---|---|---|
| Ship AI MCQ feature to 100% Pro+ institutions | 100% rollout | 10% | `██░░░░░░░░ 10%` |
| Reduce exam submission error rate to < 0.1% | < 0.1% | 0.23% | `████████░░ 78%` |
| Onboard 50 new coaching centres | 50 | 38 | `████████░░ 76%` |

**KR row:** progress bar `bg-[#1E2D4A] h-2 rounded-full` · fill colour by progress %
**KR linked features:** `text-xs text-[#94A3B8]` "Linked to 3 roadmap features" — expandable

**[Add OKR]** · **[Edit OKR]** buttons (PM Platform only)

---

### 4.8 Tab: Institution Requests

**Purpose:** Feature requests submitted by institutions (via support tickets or in-app feedback), prioritised and linked to roadmap items.

#### 4.8.1 Filters

| Control | Options |
|---|---|
| Status | All · New · Under Review · Planned · Shipped · Declined |
| Institution Type | All · School · College · Coaching · Group |
| Plan Tier | All · Starter · Standard · Professional · Enterprise |
| Domain | All · Exam · Content · Analytics · Communication · etc. |
| Votes | Sort by votes (most to least) |

#### 4.8.2 Requests Table

| Column | Detail |
|---|---|
| # | Request ID |
| Request Title | Short description |
| Requested By | Institution name + type + plan |
| Votes | Count (how many institutions upvoted this request) |
| ARR at Stake | Combined ARR of requesting institutions |
| Domain | Which PM domain owns this |
| Status | Badge: New · Under Review · Planned · Shipped · Declined |
| Linked Feature | Roadmap feature linked (if planned) |
| Requested On | Date |
| Actions ⋯ | Review · Link to Feature · Mark Shipped · Decline |

**Votes column:** `text-[#6366F1] font-semibold` — sorted by votes desc by default
**ARR at Stake column:** highlights high-ARR requests: > ₹10L = amber · > ₹50L = red (cannot ignore)

**[Link to Feature]:** opens mini modal to search and link a roadmap feature
**[Decline]:** requires reason (displayed to institution CSM)

---

## 5. Drawers

### 5.1 Feature Detail Drawer (560px)

**Trigger:** Feature card click (Kanban) or row click (Backlog/Timeline)
**Header:** Feature title + Priority badge + Domain badge + `[×]`

**Section A — Details:**
- Epic: dropdown (editable)
- Owner PM: dropdown
- Description: textarea (markdown supported)
- Acceptance criteria: textarea (checklist format)
- Story points: select (Fibonacci)
- Target release: dropdown (from Release Manager)
- Domain: read-only badge

**Section B — RICE Score:**
Editable fields: Reach (number) · Impact (1–5) · Confidence (%) · Effort (story points)
Auto-computed score shown in real-time as fields change

**Section C — Progress (if In Development):**
Sub-tasks checklist:
`[ ]` Design complete
`[ ]` Backend API built
`[ ]` Frontend HTMX template
`[ ]` Tests written
`[ ]` QA sign-off
Progress bar auto-computed from checked items

**Section D — Linked Institution Requests:**
Table: Request · Institution · Votes
[Unlink] per row

**Section E — Comments:**
Chronological comment thread
Each comment: avatar + name + timestamp + text
[Add Comment] text area + [Post]

**Footer:**
- Left: [Delete Feature] (backlog only)
- Right: [Move Stage ▾] dropdown · [Save] `bg-[#6366F1]`

---

### 5.2 Epic Detail Drawer (640px)

**Trigger:** Epic badge click anywhere on roadmap
**Header:** Epic name + Domain badge + Status badge + `[×]`

**Tab A — Overview:**
- Epic description
- Start date / End date
- Owner PM
- Linked OKR
- Feature count: X features · Y story points total

**Tab B — Features:**
Table of all features in this epic with status bars

**Tab C — Timeline:**
Mini Gantt scoped to this epic's features only

**Footer:** [Edit Epic] · [Close]

---

## 6. Modals

### 6.1 New Epic Modal

**Width:** 560px

| Field | Type |
|---|---|
| Epic Title | Text · required |
| Domain | Select: PM Platform / PM Exam Domains / PM Institution Portal |
| Owner PM | User select |
| Description | Textarea |
| Target Quarter | Select: Q1/Q2/Q3/Q4 + year |
| Linked OKR | Select from active OKRs |
| Priority | P0–P3 |

---

### 6.2 New Feature Modal

**Width:** 520px

| Field | Type |
|---|---|
| Feature Title | Text · required |
| Epic | Select |
| Domain | Auto from epic or override |
| Description | Textarea |
| Acceptance Criteria | Textarea |
| Priority | P0–P3 |
| Story Points | Select (Fibonacci) |
| Target Release | Select from Release Manager |
| Initial Status | Select: Backlog · Planned |

---

## 7. Django View

```python
class ProductRoadmapView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "portal.view_roadmap"

    def get(self, request):
        ctx = self._build_context(request)
        if _is_htmx(request):
            part = request.GET.get("part", "")
            templates = {
                "kpi":           "product/partials/roadmap_kpi.html",
                "kanban":        "product/partials/roadmap_kanban.html",
                "timeline":      "product/partials/roadmap_timeline.html",
                "backlog":       "product/partials/roadmap_backlog.html",
                "okrs":          "product/partials/roadmap_okrs.html",
                "requests":      "product/partials/roadmap_requests.html",
                "feature_drawer":"product/partials/feature_drawer.html",
                "epic_drawer":   "product/partials/epic_drawer.html",
            }
            if part in templates:
                return render(request, templates[part], ctx)
        return render(request, "product/roadmap.html", ctx)

    def post(self, request):
        if not request.user.has_perm("portal.manage_roadmap"):
            return JsonResponse({"error": "Permission denied"}, status=403)
        action = request.POST.get("action")
        dispatch = {
            "create_epic":         self._create_epic,
            "create_feature":      self._create_feature,
            "move_feature":        self._move_feature,
            "update_feature":      self._update_feature,
            "delete_feature":      self._delete_feature,
            "link_request":        self._link_request,
            "ai_prioritise":       self._ai_prioritise,
        }
        handler = dispatch.get(action)
        if handler:
            return handler(request)
        return JsonResponse({"error": "Unknown action"}, status=400)
```

---

## 8. Empty States

| Section | Copy |
|---|---|
| Kanban — no features | "No features in this column. Drag a feature here or create a new one." |
| Backlog — empty | "Backlog is clear! All features are planned or shipped." |
| OKRs — none | "No OKRs set for this quarter. Add objectives to track your team's goals." |
| Institution Requests — none | "No feature requests from institutions yet." |
| Timeline — no epics | "No active epics for this quarter. Create your first epic to build the timeline." |

---

## 9. Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `E` | New Epic modal |
| `F` | New Feature modal |
| `1–5` | Switch tabs |
| `Q` | Cycle through quarter filters |
| `Esc` | Close drawer / modal |
| `↑↓` | Navigate backlog table |
| `Space` | Expand/collapse epic row in Timeline |
