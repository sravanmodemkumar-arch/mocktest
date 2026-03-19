# Component: Data Display — Stat Cards, Badges, Avatars, Charts

---

## Stat Card (KPI Card)

### Layout Variants

**Compact (4-column dashboard row):**
```
┌──────────────────────────┐
│  📊  Total Students      │
│                          │
│  1,24,700                │  ← large number
│  ↑ 12% from last month   │  ← trend
└──────────────────────────┘
```

**Detailed (2-column):**
```
┌────────────────────────────────────────────┐
│  Total Students                  [📊 ▼]   │
│                                            │
│  1,24,700           ↑ 12%                 │
│                      vs last month         │
│                                            │
│  ████████████████░░  78% capacity          │
│                                            │
│  Hostelers: 34,200   Day: 90,500          │
└────────────────────────────────────────────┘
```

### Trend Indicator

| Trend | Icon | Color | Text |
|---|---|---|---|
| Up (positive) | ↑ | Green `#2E7D32` | `+12%` |
| Down (negative) | ↓ | Red `#C62828` | `-3%` |
| Down (positive — for bad metrics) | ↓ | Green | `-5% absences` |
| No change | → | Gray | `No change` |
| Not enough data | — | Gray | `—` |

### Skeleton Loading
- Card shape maintained
- Number replaced by shimmer bar (60% width)
- Label replaced by shimmer bar (40% width)
- Trend replaced by shimmer bar (30% width)

---

## Badge / Status Chip

### Layout
```
[● Active]    [● Suspended]   [● Pending]   [● Inactive]
```

### Status Colors

| Status | Color | Background | Use Case |
|---|---|---|---|
| Active | `#2E7D32` | `#E8F5E9` | User active, subscription active |
| Inactive | `#455A64` | `#ECEFF1` | Archived, not enrolled |
| Pending | `#E65100` | `#FFF3E0` | Awaiting action (BGV, fee, approval) |
| Suspended | `#C62828` | `#FFEBEE` | Account suspended |
| Trial | `#7B1FA2` | `#F3E5F5` | Free trial user |
| Premium | `#F57F17` | `#FFF8E1` | Paid subscriber |
| Expired | `#BF360C` | `#FBE9E7` | Subscription expired |
| Verified | `#1565C0` | `#E3F2FD` | BGV verified, email verified |
| Draft | `#546E7A` | `#ECEFF1` | Content draft, unpublished |
| Published | `#2E7D32` | `#E8F5E9` | Content live |

### Size Variants

| Size | Padding | Font | Use Case |
|---|---|---|---|
| `xs` | 2px 6px | 10px | Dense tables |
| `sm` (default) | 3px 8px | 12px | Standard tables, cards |
| `md` | 4px 12px | 13px | Drawer headers, list items |
| `lg` | 6px 16px | 14px | Profile pages, hero sections |

### Role Badge (Access Level)

```
[L0 No Access]  [L1 Read]  [L2 Content]  [L3 Ops]  [L4 Admin]  [L5 Super]
```

Colors: L0 gray → L1 blue-gray → L2 blue → L3 indigo → L4 deep-purple → L5 red-purple

---

## Avatar

### Sizes
| Size | px | Use Case |
|---|---|---|
| `xs` | 24px | Dense list items, table cells |
| `sm` | 32px | Standard table rows, comment threads |
| `md` | 40px | Navigation, notification items |
| `lg` | 64px | Drawer profile headers |
| `xl` | 96px | Full profile page |
| `xxl` | 128px | Profile setup/edit |

### States

```
[Photo]         ← Has photo: circular crop of actual photo
[R K]           ← No photo: initials in colored circle (hashed from name)
[👤]            ← Fallback: generic person icon
[Photo + ✅]   ← With status indicator (bottom-right corner)
```

### Avatar Group (Multiple people)
```
[A] [B] [C] [+12]
```
- Overlapping circles (negative margin)
- Shows first 3 avatars + count for remainder
- Hover on count shows names in tooltip

---

## Progress Bar

### Layout Variants

**Linear:**
```
████████████░░░░░░  67%   Attendance
```

**With label:**
```
Attendance
████████████████░░  82%  ← inline percentage
```

**Segmented (multiple categories):**
```
[████████] [░░░░░] [▓▓▓]
Paid(65%)  Partial(20%) Defaulter(15%)
```

### Color Coding (Progress)

| Range | Color | Semantic |
|---|---|---|
| 0–40% | Red | Critical / Poor |
| 41–60% | Orange | Warning / Below average |
| 61–75% | Yellow | Average |
| 76–90% | Light green | Good |
| 91–100% | Dark green | Excellent |

---

## Chart Components

> All charts use lightweight library (Chart.js or Recharts).
> All charts must have: title, legend, tooltip on hover, export option.

### Line Chart (Performance Trend)
```
Score %
100 |                              ●
 80 |              ●──────────────
 60 |   ●──────────
 40 |
     Jan   Feb   Mar   Apr   May
```
- Smooth curves (bezier)
- Multiple lines (different colors) for comparison
- Hover: vertical tooltip showing all series values at that point

### Bar Chart (Subject-wise, Comparison)
```
Subject Performance
Maths    ████████████ 78%
Physics  ████████░░░░ 62%
Chemistry████████████ 84%
English  ████████████ 91%
```

### Donut / Pie Chart (Distribution)
```
        ╭───╮
       / Fee \
      │ Paid  │
      │  65%  │
       \ 20% /
        ╰───╯
     Partial Defaulter
         15%
```

### Heatmap (Attendance calendar)
```
     Jan
Mo  [░][▓][█][░][▓]
Tu  [█][█][░][▓][█]
...
```
- Color: white = absent, light = low, dark = full attendance

### Chart Common Behaviors

| Feature | Spec |
|---|---|
| Tooltip | Hover over point/bar → show value + label in popup |
| Legend | Click legend item → toggle that series visibility |
| Zoom | Drag to zoom in. Double-click to reset |
| Export | Download as PNG/SVG/CSV via [⋯] menu on chart |
| Responsive | Redraws on container resize |
| Empty | "No data yet" illustration + message |
| Loading | Shimmer overlay matching chart shape |

---

## Data Table Row Extras (Detail cells)

### Progress Cell
```
78%  ████████░░
```

### Trend Cell
```
↑ 12%   (green)
↓ 3%    (red)
```

### Multi-value Cell
```
Maths: 87 | Physics: 76 | Chem: 92
```
(Compact — tooltip shows full breakdown)

### Link Cell
```
[View 3 documents →]
```

### Action Cell
```
[Edit]  [View]  [⋯]
```

---

## Usage in Page Specs

```markdown
### Dashboard — KPI Row
→ Component: [Stat Card](../../components/07-data-display.md)
  4 cards in row:
  1. Total Students — 1,24,700 — trend vs last month
  2. Attendance Today — 94.2% — progress bar
  3. Fee Collection — ₹47.2L — vs monthly target
  4. Active Exams — 3 — badge count

### Student Row — Status
→ Badge: Active/Suspended (see status colors above)
→ Avatar: 32px with initials fallback
→ Attendance: Progress bar 0–100% with color coding
```
