# Component: Navigation — Sidebar, Top Nav, Tabs, Breadcrumb

---

## Portal Layout (Master Template)

### Desktop Layout (≥ 1024px)
```
┌──────────────────────────────────────────────────────────────────┐
│  TOP NAV BAR                                                     │
│  [☰] [Portal Logo + Name]    [🔍 Search]  [🔔] [👤 Profile ▼]  │
├──────────────┬───────────────────────────────────────────────────┤
│              │  PAGE HEADER                                      │
│   SIDEBAR    │  [Breadcrumb]              [Page Action buttons]  │
│   (240px)    │  [Page Title]                                     │
│              │  [Quick filter chips — if applicable]             │
│   [Nav       ├───────────────────────────────────────────────────┤
│    Items]    │                                                   │
│              │  PAGE CONTENT AREA                                │
│              │                                                   │
│              │  (Table / Dashboard / Form etc.)                  │
│              │                                                   │
│              │                                                   │
└──────────────┴───────────────────────────────────────────────────┘
```

### Mobile Layout (< 768px)
```
┌──────────────────────────────────────┐
│  [☰]  Portal Name    [🔔] [👤]      │  ← Top nav (fixed)
├──────────────────────────────────────┤
│  [Breadcrumb]                        │
│  Page Title                          │
├──────────────────────────────────────┤
│                                      │
│  Page Content                        │
│                                      │
└──────────────────────────────────────┘
    [☰ Menu slides in from left as overlay]
```

---

## Top Navigation Bar

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ [☰]  [EduForge Logo] [Portal Name]   [🔍]  [🔔 3] [ℹ] [👤 ▼] │
└─────────────────────────────────────────────────────────────────┘
```

### Elements

| Element | Spec | Behavior |
|---|---|---|
| Hamburger [☰] | 40×40 touch target | Toggles sidebar collapsed/expanded |
| Logo | 32px height, portal-specific | Click = go to home dashboard |
| Portal name | 14px medium, hidden on mobile | Shows institution name |
| Search [🔍] | Expands to full search bar on click | Global search across portal |
| Notifications [🔔] | Badge shows unread count (max 99+) | Opens notification drawer |
| Info [ℹ] | | Opens help / keyboard shortcuts panel |
| Profile [👤] | Avatar (32px) + name (desktop only) [▼] | Dropdown: Profile, Settings, Logout |

### Profile Dropdown
```
┌───────────────────────────────┐
│  [Avatar 48px]                │
│  Ravi Kumar Sharma            │
│  Content Director             │
│  admin.eduforge.in            │
│  ──────────────────────────── │
│  👤  My Profile               │
│  ⚙️  Preferences              │
│  🔒  Security & Sessions      │
│  ──────────────────────────── │
│  🔄  Switch Portal            │  ← Shows if multi-portal user
│  ──────────────────────────── │
│  🚪  Log Out                  │
└───────────────────────────────┘
```

---

## Sidebar Navigation

### Layout (Expanded — 240px)
```
┌──────────────────────────────────────────┐
│                                          │
│  🏠  Dashboard          ← active item   │  ← filled primary bg
│                                          │
│  ─── CONTENT ───────────────────────    │  ← section divider
│  📝  MCQ Bank                            │
│  📋  Notes                               │
│  🎬  Videos                              │
│  ▼ Content sub-menu is open              │
│       All Questions                      │
│       Pending Review                     │
│       Published                          │
│                                          │
│  ─── OPERATIONS ────────────────────    │
│  🏫  Institutions                        │
│  👥  Users                               │
│  📅  Exams                               │
│                                          │
│  ─── REPORTS ───────────────────────    │
│  📊  Analytics                           │
│  💰  Billing                             │
│                                          │
│  ─── ADMIN ─────────────────────────    │
│  ⚙️  Settings                            │
└──────────────────────────────────────────┘
```

### Collapsed Sidebar (64px — icons only)
```
┌────────┐
│  🏠    │  ← tooltip on hover: "Dashboard"
│        │
│  📝    │
│  📋    │
│  🎬    │
│        │
│  🏫    │
│  👥    │
│  📅    │
│        │
│  📊    │
│  💰    │
│        │
│  ⚙️    │
└────────┘
```

### Nav Item States

| State | Background | Text | Icon |
|---|---|---|---|
| Default | Transparent | `--on-surface` dark | Default color |
| Hover | `--surface-variant` | Same | Same |
| Active (current page) | `--primary-container` | `--primary` | `--primary` |
| Active (parent of current) | Light tint | `--primary` | `--primary` |
| Disabled | Transparent | 40% opacity | 40% opacity |

### Sub-menu (Nested nav)
- Indent: 16px from parent
- Expand/collapse: Chevron [▼/▶] on parent item
- Open by default if current page is in this group
- Max 2 levels deep (nav item → sub-item). No 3rd level

### Nav Badges
```
📅  Exams            [3]   ← red badge = pending actions
👥  BGV              [15]  ← warning badge = action required
```

---

## Breadcrumb

### Layout
```
Dashboard  /  Institutions  /  XYZ School  /  Students  /  Ravi Kumar
```

### Behavior

| Property | Spec |
|---|---|
| Separator | `/` in `--on-surface-variant` |
| Last item | Not a link. Current page. Bold. `--on-surface` |
| All others | Links. `--primary` color. Underline on hover |
| Overflow | On mobile: show only last 2 items. First item = `…` with dropdown |
| Max length | Each segment max 24 chars. Truncate with tooltip |
| Dynamic | Auto-generated from URL structure + page title |

---

## Page Tabs

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  [Overview]  [Students]  [Staff]  [Exams]  [Finance]   │
│  ──────────────────────────────────────────             │
│                                            ↑ active tab │
│  Tab content below                                      │
└─────────────────────────────────────────────────────────┘
```

### Behavior

| Property | Spec |
|---|---|
| Active indicator | 2px bottom border in `--primary` color |
| Inactive | No border, `--on-surface-variant` text |
| Hover | `--surface-variant` background, `--on-surface` text |
| Overflow | > 6 tabs → show 5 + "More [▼]" dropdown |
| URL | Tab change reflected in URL: `?tab=students` |
| Keyboard | Left/right arrow keys navigate between tabs |
| Loading | Spinner in tab content area while loading |
| Count badge | Tab can show count: `Students (1,247)` |

### Tab Variants

| Type | Use Case |
|---|---|
| Page tabs | Major sections of a page — always visible |
| Drawer tabs | Sections within a detail drawer |
| Pill tabs | Compact filter-like tabs in cards |

---

## Step Progress (Wizard)

> For multi-step forms: onboarding, exam creation, bulk upload.

### Layout
```
  ●━━━━━━━━●━━━━━━━━○━━━━━━━━○
 Step 1    Step 2   Step 3   Step 4
  Done     Active   Todo     Todo
```

### States

| State | Circle | Line | Label |
|---|---|---|---|
| Completed | Filled primary with ✓ | Solid primary | Dark text |
| Active (current) | Filled primary (no ✓) | — | Bold primary text |
| Upcoming | Empty circle (outlined) | Dashed gray | Gray text |
| Error | Red circle with ✕ | Red solid | Red text |

### Navigation
- Previous/Next buttons below form (not inside step indicator)
- Clicking completed step = navigate back to that step
- Cannot skip ahead to future steps (unless explicitly allowed)
- Browser back button = go to previous step (not leave wizard)

---

## Notification Drawer

> Opens from bell icon [🔔] in top nav.

### Layout
```
┌────────────────────────────────────────────┐
│  Notifications                 [Mark all ✓]│
│  ──────────────────────────────────────── │
│  [Filters: All | Unread | Mentions]        │
│                                            │
│  TODAY                                     │
│  ┌────────────────────────────────────┐   │
│  │ 🔴 [Icon] BGV pending for 3 staff  │   │  ← Unread
│  │         XYZ School · 2 hours ago   │   │
│  └────────────────────────────────────┘   │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │    [Icon] Exam published: JEE Mock │   │  ← Read
│  │         4 hours ago                │   │
│  └────────────────────────────────────┘   │
│                                            │
│  YESTERDAY                                 │
│  ┌────────────────────────────────────┐   │
│  │    [Icon] 1,247 results computed   │   │
│  │         Yesterday 6:42 PM          │   │
│  └────────────────────────────────────┘   │
│                                            │
│  [Load more notifications]                 │
└────────────────────────────────────────────┘
```
