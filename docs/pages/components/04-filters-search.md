# Component: Search, Filters, Advanced Filter Panel

---

## Search Bar

### Layout
```
┌──────────────────────────────────────────────────────┐
│  [🔍]  Search students, roll no, mobile...      [✕] │
└──────────────────────────────────────────────────────┘
```

### Behavior

| Property | Spec |
|---|---|
| Debounce | 300ms after last keystroke before API call |
| Min characters | 2 characters minimum before search triggers |
| Clear | [✕] appears when input has text. Click = clear + refocus |
| Keyboard | `/` shortcut focuses search from anywhere on page |
| Placeholder | Context-specific: "Search students...", "Search staff..." |
| Loading | Spinner inside field while searching |
| History | Last 5 searches shown in dropdown on focus (session only) |
| Highlight | Matching text highlighted in results (bold or yellow bg) |

### Search Scope Selector (Multi-entity pages)
```
┌──────────────────────────────────────────────────────────┐
│  [All ▼]  [🔍]  Search...                               │
│  ┌──────┐                                                │
│  │ All  │                                                │
│  │ Name │                                                │
│  │ Mobile│                                               │
│  │ Email│                                                │
│  │ Roll#│                                                │
│  └──────┘                                                │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Filter Bar

> Inline chips/buttons for most-used filter combinations.
> Below search bar, above table.

### Layout
```
┌────────────────────────────────────────────────────────────────┐
│  [All] [Active] [Fee Defaulters] [BGV Pending] [Suspended]     │
│  [Class 12 ▼] [MPC ▼] [Hostel ▼]           [⚙ More Filters]  │
└────────────────────────────────────────────────────────────────┘
```

### Chip Behavior

| Property | Spec |
|---|---|
| Single-select chips | Like "All / Active / Suspended" — radio behavior |
| Multi-select chips | Like tags — toggle on/off |
| Dropdown chips | Chips with [▼] open inline dropdown (single or multi-select) |
| Active state | Filled primary color background, white text |
| Count badge | Active chip shows count: "Fee Defaulters (34)" |
| Clear all | "Clear filters" link appears when any filter active |
| Persistence | Filter state in URL params. Share/bookmark = same filtered view |

---

## Advanced Filter Panel (Side Drawer)

> Opens from "⚙ More Filters" button. Slides in from right.
> For complex multi-field filtering.

### Layout
```
┌────────────────────────────────────────┐
│  Advanced Filters              [Reset] │
│  ──────────────────────────────────── │
│  Class                                 │
│  [Class 11 ▼]  [Class 12 ▼]           │
│                                        │
│  Stream                                │
│  [☑] MPC  [☑] BiPC  [☐] CEC  [☐] MEC │
│                                        │
│  Hostel Status                         │
│  [◉ All]  [○ Hosteler]  [○ Day Scholar]│
│                                        │
│  Fee Status                            │
│  [☐ Paid]  [☐ Partial]  [☑ Defaulter] │
│                                        │
│  Attendance Range                      │
│  Min: [60]%   Max: [100]%             │
│  ████████████░░░░  slider             │
│                                        │
│  Last Login                            │
│  [Within last ▼]  [30 days ▼]         │
│                                        │
│  Date Range (custom)                   │
│  From: [01/01/2024]  To: [31/03/2024] │
│  [📅 Date Picker]                      │
│                                        │
│  ──────────────────────────────────── │
│  Showing 247 of 1,247 results          │
│  [Cancel]          [Apply Filters]    │
└────────────────────────────────────────┘
```

### Filter Field Types

| Field Type | Component | Example |
|---|---|---|
| Single select | Dropdown `[▼]` | Class, Stream |
| Multi-select | Checkbox group | Subjects, Status |
| Radio group | `[◉]` buttons | Hostel: All/Hosteler/Day Scholar |
| Range slider | Dual handle slider | Attendance %, Fee amount |
| Date picker | Calendar popup | Date of birth, Enrollment date |
| Date range | Two calendar pickers | From → To |
| Toggle | Switch | Active only, Has photo |
| Number range | Two number inputs | Age from/to, Score range |
| Text search | Input | Notes contains, Address contains |

### Filter Count Indicator
```
[⚙ More Filters  3]   ← Number badge shows active advanced filter count
```

### Saved Filters (Advanced)
> For power users — admin/manager roles.

```
┌────────────────────────────────────────┐
│  Advanced Filters              [Reset] │
│                                        │
│  Saved Filters:                        │
│  [Class 12 Defaulters ★] [Hostel Only]│
│  [My Batches ★]         [+ Save this] │
│                                        │
│  ──────────────────────────────────── │
│  [filter fields...]                    │
└────────────────────────────────────────┘
```

- "★" saved filters appear in quick filter bar as chips
- Up to 10 saved filters per user
- Saved filters are private per user (not shared)
- Team filters: Admin can push shared filters to team (future phase)

---

## Date Picker

### Layout (Inline popup)
```
┌──────────────────────────────────┐
│  ◁  March 2024  ▷                │
│  Mo  Tu  We  Th  Fr  Sa  Su      │
│                   1   2   3      │
│   4   5   6   7   8   9  10      │
│  11  12  13  14  15  16  17      │
│  18  19  20 [21] 22  23  24      │
│  25  26  27  28  29  30  31      │
│                                  │
│  [Today]           [Clear]       │
└──────────────────────────────────┘
```

| State | Visual |
|---|---|
| Today | Underline |
| Selected | Filled primary circle |
| Range start/end | Filled circle |
| Range in-between | Tinted background |
| Disabled (future) | 40% opacity |
| Hover | Light circle ring |

---

## Usage in Page Specs

```markdown
### Student List — Filters
→ Search: [Search by name, roll number, mobile...]
→ Quick filters: [All] [Active] [Fee Defaulter] [Absent Today] [Hostel]
→ Dropdown chips: [Class ▼] [Stream ▼] [Batch ▼]
→ Advanced Filter Panel fields:
   - Class: multi-select (6–12)
   - Stream: checkbox (MPC, BiPC, CEC, MEC)
   - Fee Status: checkbox (Paid, Partial, Defaulter)
   - Attendance: range slider (0–100%)
   - Enrollment date: date range
   - Hostel: radio (All, Hosteler, Day Scholar)
```
