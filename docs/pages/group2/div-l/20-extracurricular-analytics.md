# 20 — Extra-Curricular Analytics

> **URL:** `/group/extracurricular/analytics/`
> **File:** `20-extracurricular-analytics.md`
> **Template:** `portal_base.html` (light theme)
> **Priority:** P2
> **Roles:** Sports Director G3 (sports section) · Cultural Activities Head G3 (cultural section) · NSS/NCC Coordinator G3 (NSS/NCC section) · Library Head G2 (library section)

---

## 1. Purpose

Cross-division analytics dashboard aggregating key metrics across all Sports & Extra-Curricular domains — sports tournaments, cultural events, NSS/NCC activities, library usage, and student achievements. Provides group-level leadership (Group Chairman, Group Principal) with a single view of extra-curricular health across branches. Each Division L role sees their own domain sections in full; the group leadership sees all sections read-only.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Sports Director | G3 | Full view — sports + achievements sections · View-only other sections | |
| Cultural Activities Head | G3 | Full view — cultural + achievements sections · View-only other sections | |
| NSS/NCC Coordinator | G3 | Full view — NSS/NCC + achievements sections · View-only other sections | |
| Library Head | G2 | Full view — library section · View-only other sections | |
| Group Chairman / Principal | G4 | View-only — all sections | No edit capability |
| All others | — | — | No access |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Sports & Extra-Curricular  ›  Extra-Curricular Analytics
```

### 3.2 Page Header
```
Extra-Curricular Analytics
AY [academic year]  ·  [N] Total Achievements  ·  [N] Branches Active  ·  [Export All ↓]
```

**AY Selector:** Dropdown to switch academic year (current + 2 prior). Changes all sections simultaneously.

---

## 4. Sections

```
Overview  |  Sports  |  Cultural  |  NSS / NCC  |  Library  |  Achievements
```

---

## 5. Section: Overview

High-level cross-domain summary for group leadership.

### 5.1 KPI Grid (12 cards, 4 per row)

| Card | Metric |
|---|---|
| Total Tournaments | Inter-branch tournaments this AY |
| Total Cultural Events | All cultural events including branch-level |
| NSS Students (240 hrs) | Students who completed NSS programme |
| NCC Certificates Issued | A + B + C certificates this AY |
| Student Achievements | All achievements registered |
| National / State Level | Achievements at state/national level |
| Active Branches | Branches with ≥ 1 extra-curricular entry |
| Library Resources | Active resources in catalogue |
| Total Downloads | Library downloads this AY |
| Civic Programmes | Civic activities conducted |
| Volunteer Hours | Total NSS/civic volunteer hours |
| Competitions | Cultural competitions this AY |

### 5.2 Chart: Branch Participation Heatmap
- **Type:** Grid heatmap (branches × domain)
- **Rows:** Branches
- **Columns:** Sports / Cultural / NSS / NCC / Library
- **Cell value:** Activity count (deeper colour = more active)
- **Export:** PNG

### 5.3 Chart: Achievements by Level (current AY)
- **Type:** Stacked bar (horizontal)
- **Y-axis:** Domains
- **Stacks:** Branch / Group / District / State / National / International
- **Export:** PNG

---

## 6. Section: Sports

### 6.1 KPI Row (5 cards)
| Card | Metric |
|---|---|
| Tournaments | This AY |
| Teams Registered | Across all sports |
| Students Participated | In tournaments |
| Sports Achievements | State/national level |
| Equipment Requests Pending | Open requests |

### 6.2 Chart: Tournament Participation by Branch
- **Type:** Horizontal grouped bar
- **Data:** Teams registered vs teams that competed per branch
- **Export:** PNG

### 6.3 Chart: Sport-wise Participation Trend
- **Type:** Line chart (monthly)
- **Data:** Cumulative student-sport participation events over the AY
- **Export:** PNG

### 6.4 Table: Branch Sports Performance Summary
| Column | Notes |
|---|---|
| Branch | |
| Tournaments Entered | |
| Wins | |
| Runners-up | |
| Achievements (State+) | |
| Equipment Coverage | Good / Fair / Poor based on inventory |

---

## 7. Section: Cultural

### 7.1 KPI Row (5 cards)
| Card | Metric |
|---|---|
| Events Conducted | All events this AY |
| Competitions | Scored competitions |
| Students Participated | |
| Certificates Generated | |
| Reports Pending | Events without post-event report |

### 7.2 Chart: Cultural Events by Type
- **Type:** Donut
- **Segments:** Annual Day / Debate / Quiz / Music / Dance / Drama / Literary / Other
- **Centre text:** Total events
- **Export:** PNG

### 7.3 Chart: Branch Cultural Engagement
- **Type:** Horizontal bar
- **Data:** Events per branch, stacked by type
- **Export:** PNG

### 7.4 Table: Cultural Competition Results Summary
| Column | Notes |
|---|---|
| Branch | |
| Competitions Entered | |
| 1st Place | |
| 2nd Place | |
| 3rd Place | |
| Total Awards | |

---

## 8. Section: NSS / NCC

### 8.1 KPI Row (6 cards)
| Card | Metric |
|---|---|
| NSS Units | Across all branches |
| NSS Enrolled | Students this AY |
| NSS Completed 240 hrs | N (%) |
| NCC Cadets | Total enrolled |
| NCC Camps | This AY |
| Certificates (A/B/C) | Issued this AY |

### 8.2 Chart: NSS 240-Hour Completion by Branch
- **Type:** Horizontal bar
- **Data:** % of enrolled students completing 240 hrs per branch
- **Target line:** 100%
- **Export:** PNG

### 8.3 Chart: NCC Certificate Level Distribution
- **Type:** Donut
- **Segments:** A / B / C / None
- **Export:** PNG

### 8.4 Chart: Civic Volunteer Hours Trend
- **Type:** Line chart (monthly)
- **Data:** Total volunteer hours logged per month
- **Export:** PNG

### 8.5 Table: NSS/NCC Branch Compliance
| Column | Notes |
|---|---|
| Branch | |
| NSS Officer | Name |
| NSS Students (240 hrs) | N / Total enrolled (%) |
| NCC Officer | Name |
| NCC Camps Attended | N |
| Certificates Issued | N |
| Civic Programmes | N |

---

## 9. Section: Library

### 9.1 KPI Row (4 cards)
| Card | Metric |
|---|---|
| Active Resources | In catalogue |
| Downloads This Month | |
| Active Packages | Distributed |
| Branches with Access | |

### 9.2 Chart: Downloads by Subject (current month)
- **Type:** Horizontal bar
- **Data:** Download count per subject
- **Export:** PNG

### 9.3 Chart: Monthly Downloads Trend (current AY)
- **Type:** Line chart
- **Data:** Total downloads per month
- **Export:** PNG

### 9.4 Table: Branch Library Engagement
| Column | Notes |
|---|---|
| Branch | |
| Packages Assigned | |
| Resources Available | |
| Downloads This Month | |
| Last Access | Date |

---

## 10. Section: Achievements

Cross-domain achievements leaderboard and analytics.

### 10.1 KPI Row (4 cards)
| Card | Metric |
|---|---|
| Total Achievements | All domains this AY |
| State Level + | High-prestige achievements |
| Students Recognised | Unique students with ≥ 1 achievement |
| Certificates Generated | |

### 10.2 Chart: Achievements by Domain (Donut)
- Sports / Cultural / NSS / NCC / Academic / Other
- Centre text: Total achievements
- Export: PNG

### 10.3 Chart: Top 10 Achieving Branches
- **Type:** Horizontal bar (top 10)
- **Data:** Total achievements per branch
- **Export:** PNG

### 10.4 Table: Top Student Achievers (current AY)
| Column | Notes |
|---|---|
| Student Name | |
| Class | |
| Branch | |
| Achievements | Count |
| Highest Level | State / National / etc. |
| Domain | Primary domain |

Default: top 20 by achievement count. [View All] link → Achievement Register (page 19).

---

## 11. Export

**[Export All ↓]** — Downloads a multi-sheet XLSX report covering all sections. Sheet per domain.

Individual section export buttons (PNG for charts, XLSX for tables) available within each section.

---

## 12. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| AY changed | "Showing data for AY [YYYY-YY]." | Info | 3s |
| Export started | "Generating full analytics report…" | Info | 3s |
| Export ready | "Your export is ready. [Download]" | Success | 8s |

---

## 13. Empty States

| Section | Condition | Heading | Description |
|---|---|---|---|
| Overview heatmap | No activity data | "No activity data yet" | "Extra-curricular activity across domains will appear here" |
| Sports section | No tournaments | "No sports data this AY" | "Tournaments and team data will appear once recorded" |
| Cultural section | No events | "No cultural data this AY" | "Events and competitions will appear once recorded" |
| NSS/NCC section | No units | "No NSS/NCC data this AY" | "Programme data will appear once units are registered" |
| Library section | No downloads | "No library activity this AY" | "Download activity will appear once branches access resources" |
| Achievements | No achievements | "No achievements recorded" | "Achievement data will appear once records are added" |

---

## 14. Loader States

| Trigger | Loader Type |
|---|---|
| Section initial load | Skeleton: KPI cards + chart placeholders + table skeleton |
| AY switch | Full section re-render skeleton |
| Individual chart | Skeleton rectangle (animated pulse) |
| Export generation | Full-page overlay spinner "Generating report…" |

---

## 15. Role-Based UI Visibility

| Element | Sports Dir | Cultural Head | NSS/NCC Coord | Library Head |
|---|---|---|---|---|
| Overview section | ✅ | ✅ | ✅ | ✅ |
| Sports section (full) | ✅ | View-only | View-only | View-only |
| Cultural section (full) | View-only | ✅ | View-only | View-only |
| NSS/NCC section (full) | View-only | View-only | ✅ | View-only |
| Library section (full) | View-only | View-only | View-only | ✅ |
| Achievements section | ✅ (sports) | ✅ (cultural) | ✅ (NSS/NCC) | View-only |
| [Export All] | ✅ | ✅ | ✅ | ✅ |

---

## 16. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{id}/analytics/extracurricular/overview/?ay=` | JWT (G3+) | Overview KPI + heatmap data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/sports/?ay=` | JWT (G3+) | Sports analytics data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/cultural/?ay=` | JWT (G3+) | Cultural analytics data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/nss/?ay=` | JWT (G3+) | NSS/NCC analytics data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/library/?ay=` | JWT (G2+) | Library analytics data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/achievements/?ay=` | JWT (G3+) | Achievements analytics data |
| GET | `/api/v1/group/{id}/analytics/extracurricular/export/?ay=&format=` | JWT (G3+) | Full XLSX export |

---

## 17. HTMX Patterns

| Interaction | hx-trigger | hx-method + URL | hx-target | hx-swap |
|---|---|---|---|---|
| Section tab switch | `click` | GET `.../analytics/extracurricular/?section={s}&ay={ay}` | `#analytics-section-content` | `innerHTML` |
| AY selector change | `change` | GET `.../analytics/extracurricular/?ay={ay}&section={current}` | `#analytics-section-content` | `innerHTML` |
| Page load (overview) | `load` | GET `.../analytics/extracurricular/overview/` | `#overview-section` | `innerHTML` |
| KPI card load | `load` | GET `.../analytics/extracurricular/{section}/kpi/` | `#kpi-{section}` | `innerHTML` |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
