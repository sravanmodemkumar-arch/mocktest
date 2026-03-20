# div-a-12 — Incident Manager

## 1. Platform Scale Reference

| Dimension | Value |
|---|---|
| Active incidents at any given time | 0–5 (platform target: < 2) |
| Incidents/month (historical avg) | ~8–15 |
| P0 incidents/quarter | ~1–3 |
| Mean Time to Detect (MTTD) | < 5 min (target) |
| Mean Time to Resolve (MTTR) | P0: < 30 min · P1: < 2h · P2: < 8h |
| Affected institutions per P0 | Up to 2,050 |
| PagerDuty integration | Yes (on-call rotation, auto-escalation) |
| Status page | Public (status.platform.com) |
| Runbooks | Per service in Confluence |

**Why this matters:** During a P0 incident at exam time, 500,000 concurrent students may be blocked. The Incident Manager is the war room page — real-time timeline, affected services, impact assessment, communication log, and resolution tracking. Every second counts; the UI must show current state without a page refresh.

---

## 2. Page Metadata

| Field | Value |
|---|---|
| Page title | Incident Manager |
| Route | `/exec/incidents/` |
| Django view | `IncidentManagerView` |
| Template | `exec/incident_manager.html` |
| Priority | P0 |
| Nav group | Operations |
| Required role | `exec`, `superadmin`, `ops`, `oncall` |
| 2FA required | Creating P0 incident |
| HTMX poll | Active incidents: every 15s |

---

## 3. Wireframe

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Incident Manager                         [+ New Incident] [Runbooks]│
├──────────┬──────────┬──────────┬──────────┬──────────────────────────────── ┤
│  Active  │  P0 Now  │  P1 Now  │ MTTD     │  MTTR (30d avg)                │
│    2     │    1     │    1     │ 3.2 min  │  P0: 28 min · P1: 1h 42m       │
├──────────┴──────────┴──────────┴──────────┴──────────────────────────────── ┤
│ [🔴 P0 ACTIVE: Auth service degraded — 24,000 students affected] (pulsing)  │
├──────────────────────────────────────────────────────────────────────────────┤
│ TABS: [Active] [All Incidents] [Post-Mortems] [Timeline]                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [Severity ▾] [Service ▾] [Status ▾] [Date Range ▾]                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ # │ Title          │ Sev │ Status    │ Service  │ Started │ Duration │ ⋯    │
│ 1 │ Auth degraded  │ P0  │ Ongoing   │ Auth     │ 14:32   │ 18 min   │      │
│ 2 │ Slow queries   │ P1  │ Mitigated │ Database │ 12:05   │ 2h 18m   │      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Sections — Deep Specification

### 4.1 KPI Strip

**Container:** `flex gap-4 p-4` · poll every 15s (no pause — incidents need real-time)

| # | Card | Detail | Alert |
|---|---|---|---|
| 1 | Active Incidents | Current open incidents | > 0 = red pulsing |
| 2 | P0 Now | Active P0 count | > 0 = red border flash |
| 3 | P1 Now | Active P1 count | > 0 = amber |
| 4 | MTTD (30d avg) | Mean time to detect | > 10 min = amber |
| 5 | MTTR P0 (30d) | Mean time to resolve P0 | > 60 min = red |

**P0 active animation:** `animate-pulse` on red border of Active and P0 Now cards

---

### 4.2 Active Incident Banner

Shown when any P0/P1 is active. Auto-hides when all resolved.
`bg-[#450A0A] border border-[#F87171] rounded-xl p-4 mx-4 mb-2`
`flex items-center gap-3`
- Pulsing red dot `w-3 h-3 bg-[#EF4444] rounded-full animate-pulse`
- Text: `🔴 P0 ACTIVE: Auth service degraded — 24,000 students affected · Started 18 min ago`
- [View Incident →] button → opens Incident Detail Drawer for the active P0
**Poll:** `hx-get="?part=active_banner"` `hx-trigger="every 15s"` `hx-swap="outerHTML"`

---

### 4.3 Tab Bar

Tabs: Active · All Incidents · Post-Mortems · Timeline
**Active tab:** count badge on "Active" tab (number of active incidents)
**HTMX:** `hx-get="?part={tab}"` on click · `hx-target="#incident-table"` `hx-swap="innerHTML"`

---

### 4.4 Filter Bar

`id="incident-filters"` · `flex flex-wrap gap-3 p-4`

| Filter | Options |
|---|---|
| Severity | All / P0 / P1 / P2 / P3 |
| Service | Auth / Database / Exam Engine / Proctoring / Billing / CDN / API Gateway / All |
| Status | All / Ongoing / Mitigated / Resolved / Post-mortem pending |
| Date Range | Today / Last 7d / 30d / 90d / Custom |
| Institution affected | Search by institution name |

---

### 4.5 Incident Table

`id="incident-table"` · `hx-get="?part=incidents_table"` · `hx-trigger="load, every 15s[!document.querySelector('.drawer-open,.modal-open')]"`

**Container:** `bg-[#0D1526] rounded-xl border border-[#1E2D4A]`
**Row click:** opens Incident Detail Drawer (div-a-13 pattern)

#### Column Specifications

| Column | Width | Detail |
|---|---|---|
| # | 48px | Incident ID `INC-XXXX` |
| Title | 280px | Truncated · P0 rows: `font-semibold text-[#F87171]` · pulsing dot if Ongoing |
| Severity | 60px | Badge: P0 `bg-[#450A0A] text-[#F87171]` · P1 `bg-[#451A03] text-[#FCD34D]` · P2 `bg-[#1E3A5F] text-[#60A5FA]` · P3 `bg-[#1E293B] text-[#94A3B8]` |
| Status | 110px | Ongoing (red pulse dot) / Mitigated (amber) / Resolved (green) / Post-mortem (blue) |
| Service | 120px | Affected service name |
| Affected | 100px | "2,050 inst" or "N students" |
| Started | 100px | Relative time · tooltip = absolute timestamp |
| Duration | 100px | Elapsed (if ongoing: live counting) or total |
| Resolved By | 120px | Username or `—` |
| Actions ⋯ | 48px | View Detail / Update Status / Assign / Post-mortem / PagerDuty |

**Live duration counter:** for Ongoing incidents · JavaScript: updates every 1s via `setInterval` on cells with `data-incident-start="{iso_timestamp}"`

**P0 row pinning:** P0 Ongoing rows always pinned to top of table, regardless of sort

---

### 4.6 Tab: Post-Mortems

`id="tab-postmortems"` · `hx-get="?part=postmortems"`

| Column | Detail |
|---|---|
| Incident | INC-XXXX + title |
| Severity | Badge |
| Date | Resolved date |
| Duration | Total downtime |
| Root Cause | 1-line summary |
| Action Items | Count (open / closed) |
| Author | Name |
| Status | Draft / In Review / Published |
| Actions ⋯ | View / Edit / Publish |

**[View]:** opens Post-Mortem Drawer (560px) with full post-mortem document inline

---

### 4.7 Tab: Timeline

`id="tab-timeline"` · `hx-get="?part=timeline"`

**Purpose:** Cross-incident timeline. See all incidents on a horizontal time axis.

**Chart:** Gantt-style horizontal bars per incident · Y-axis = incidents · X-axis = time (last 90 days)
**Bar colours by severity:** P0 red · P1 amber · P2 blue · P3 grey
**Bar width:** proportional to duration
**Hover:** tooltip with incident title + duration + affected services
**Click:** opens Incident Detail Drawer

**Below timeline:** Incident frequency histogram (bar per day)

---

## 5. Drawers

### 5.1 Incident Detail Drawer (720 px)

`id="incident-drawer"` · `w-[720px]` · right panel

**Header (80px):**
Incident ID + Severity badge + Status badge + Title `text-lg font-bold text-white`
Sub-line: Started · Duration · Affected: N institutions / N students
[Update Status ▾] [Assign ▾] [PagerDuty →] [×]

**Tab bar (5 tabs):** Overview · Timeline · Affected · Communication · Post-Mortem

**Tab A — Overview:**
- Summary (editable markdown field for ops users)
- Affected services: badge list
- Severity + Status + Priority
- Incident commander: assigned user
- Resolution: text (populated when resolved)
- SLA breach: Yes/No badge

**Tab B — Timeline (real-time):**
Vertical timeline of events:
```
14:32:05  INC-0041 created by PagerDuty auto-detection
14:33:18  Assigned to oncall-engineer
14:35:00  Status: Investigating → Mitigating
14:47:22  Service restart initiated on auth-service-03
14:50:11  Status: Mitigating → Resolved
```
- Each event: timestamp `text-xs text-[#64748B]` + event text `text-sm text-white` + user if applicable
- **[+ Add Update]** button: inline form to post new update (text + status change)
- Poll: `hx-get="?part=incident_timeline&id={id}"` `hx-trigger="every 15s"` `hx-swap="innerHTML"` (timeline auto-refreshes)

**Tab C — Affected:**
- Breakdown: Institutions affected (table: name, type, impact level)
- Students estimated affected: count
- Geographic spread: affected states
- [Send Status Update to Affected Institutions] → communication modal

**Tab D — Communication:**
Log of all notifications sent: email · SMS · PagerDuty · Status page updates
Table: Channel · Sent at · Recipient count · Message preview

**Tab E — Post-Mortem:**
Full post-mortem document (markdown rendered):
- Timeline of events
- Root cause analysis
- Contributing factors
- Impact assessment
- Action items (checklist)
- [Edit Post-Mortem] (for ops/exec roles)

**Footer:** [Update Status] [Add Update] [Close Incident] [Close Drawer]

---

## 6. Modals

### 6.1 New Incident Modal (640 px)

**2FA required for P0.**

| Field | Type | Validation |
|---|---|---|
| Title | Text | Required · min 10 chars |
| Severity | Radio: P0 / P1 / P2 / P3 | Required |
| Affected services | Multi-select checkboxes | Required |
| Status | Select: Investigating / Mitigating | Default: Investigating |
| Summary | Textarea (markdown) | Required |
| Incident commander | User picker | Default: current user |
| PagerDuty alert | Checkbox | Default: checked for P0/P1 |
| Notify affected institutions | Checkbox | Default: checked for P0 |
| Status page update | Checkbox + message textarea | Optional |

**P0 extra confirmation (step 2):**
"This will trigger PagerDuty escalation and notify all 2,050 institutions. Confirm this is a genuine P0 incident."
[I confirm this is P0] [Downgrade to P1]

**Footer:** [Cancel] [Create Incident]

---

### 6.2 Update Status Modal (480 px)

| Field | Type |
|---|---|
| New status | Select: Investigating / Mitigating / Resolved / Monitoring |
| Update message | Textarea |
| Notify affected institutions | Checkbox |
| Send to status page | Checkbox |
| Resolution summary | Textarea (shown if status = Resolved) |

**Footer:** [Cancel] [Update Status]

---

## 7. HTMX Architecture

| Part param | Template | Trigger |
|---|---|---|
| `?part=kpi` | `exec/partials/incident_kpi.html` | Page load · poll 15s |
| `?part=active_banner` | `exec/partials/incident_banner.html` | Poll 15s |
| `?part=incidents_table` | `exec/partials/incidents_table.html` | Tab · filter · poll 15s |
| `?part=postmortems` | `exec/partials/postmortems_table.html` | Tab click |
| `?part=timeline` | `exec/partials/incidents_timeline.html` | Tab click |
| `?part=incident_drawer&id={id}` | `exec/partials/incident_drawer.html` | Row click |
| `?part=incident_timeline&id={id}` | `exec/partials/incident_event_timeline.html` | Drawer Tab B · poll 15s |

**Django view dispatch:**
```python
class IncidentManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "portal.view_incidents"

    def get(self, request):
        ctx = self._build_context(request)
        if _is_htmx(request):
            part = request.GET.get("part", "")
            templates = {
                "kpi": "exec/partials/incident_kpi.html",
                "active_banner": "exec/partials/incident_banner.html",
                "incidents_table": "exec/partials/incidents_table.html",
                "postmortems": "exec/partials/postmortems_table.html",
                "timeline": "exec/partials/incidents_timeline.html",
                "incident_drawer": "exec/partials/incident_drawer.html",
                "incident_timeline": "exec/partials/incident_event_timeline.html",
            }
            if part in templates:
                return render(request, templates[part], ctx)
        return render(request, "exec/incident_manager.html", ctx)

    def post(self, request):
        part = request.GET.get("part", "")
        handlers = {
            "create_incident": self._handle_create,
            "update_status": self._handle_update_status,
            "add_update": self._handle_add_update,
        }
        if part in handlers:
            return handlers[part](request)
        return HttpResponseNotAllowed(["GET"])
```

**KPI poll (no pause — incidents need real-time):**
```html
<div id="incident-kpi"
     hx-get="/exec/incidents/?part=kpi"
     hx-trigger="every 15s"
     hx-swap="innerHTML">
```

---

## 8. Performance Requirements

| Metric | Target | Critical |
|---|---|---|
| KPI strip (hot path) | < 150 ms | > 400 ms |
| Active banner | < 100 ms | > 300 ms |
| Incident table (50 rows) | < 300 ms | > 800 ms |
| Incident drawer | < 250 ms | > 700 ms |
| Timeline tab (drawer) | < 200 ms | > 600 ms |
| Full page initial load | < 800 ms | > 2 s |

---

## 9. States & Edge Cases

| State | Behaviour |
|---|---|
| 0 active incidents | Green "All systems operational" banner replaces active incident banner |
| Multiple simultaneous P0s | Each gets its own banner row; incident table sorted P0 first |
| Incident auto-resolved | Status auto-updated via PagerDuty webhook; table refreshes |
| P0 created outside business hours | PagerDuty escalation fires immediately |
| Post-mortem overdue (> 5 days post-resolution) | Yellow badge "Post-mortem overdue" on incident row |
| Incident affects 0 institutions | Affected = "Platform internal" |
| Create incident: PagerDuty API down | Show warning "Could not alert PagerDuty — alert manually" but allow incident creation |

---

## 10. Keyboard Shortcuts

| Key | Action |
|---|---|
| `N` | New incident |
| `F` | Focus filter |
| `R` | Refresh table |
| `1`–`4` | Switch tabs |
| `↑` / `↓` | Navigate rows |
| `Enter` | Open incident drawer |
| `Esc` | Close drawer/modal |
| `?` | Keyboard shortcuts help |

---

## 11. Template Files

| File | Purpose |
|---|---|
| `exec/incident_manager.html` | Full page shell |
| `exec/partials/incident_kpi.html` | KPI strip |
| `exec/partials/incident_banner.html` | Active P0 banner |
| `exec/partials/incidents_table.html` | Incident table |
| `exec/partials/postmortems_table.html` | Post-mortems table |
| `exec/partials/incidents_timeline.html` | Gantt timeline chart |
| `exec/partials/incident_drawer.html` | Incident detail drawer (5 tabs) |
| `exec/partials/incident_event_timeline.html` | Real-time event timeline (drawer Tab B) |
| `exec/partials/new_incident_modal.html` | Create incident modal |
| `exec/partials/update_status_modal.html` | Update status modal |

---

## 12. Component References

| Component | Used in |
|---|---|
| `KpiCard` | §4.1 |
| `ActiveIncidentBanner` | §4.2 |
| `TabBar` with count badge | §4.3 |
| `IncidentFilterBar` | §4.4 |
| `IncidentTable` | §4.5 |
| `SeverityBadge` | §4.5, §5.1 |
| `LiveDurationCounter` | §4.5 Duration column |
| `GanttTimeline` | §4.7 |
| `DrawerPanel` | §5.1 |
| `EventTimeline` | §5.1 Tab B |
| `MarkdownEditor` | §5.1 Tab A + Tab E |
| `PollableContainer` | KPI · banner · table · drawer timeline |
| `ModalDialog` | §6.1–6.2 |
| `UserPicker` | §6.1 |
