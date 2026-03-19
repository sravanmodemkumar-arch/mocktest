# Component: Alerts, Toasts, Banners, Empty States

---

## Toast Notification

> Temporary message. Auto-dismisses. Does not block interaction.

### Position
Top-right corner on desktop. Top-center on mobile. Z-index: 1200.

### Layout
```
┌────────────────────────────────────────┐
│  [✅ Icon]  Message text here   [✕]   │
│             Optional sub-text          │
└────────────────────────────────────────┘
```

### Variants

| Type | Icon | Color | Auto-dismiss |
|---|---|---|---|
| `success` | ✅ | Green `#2E7D32` | 4 seconds |
| `error` | ❌ | Red `#C62828` | 8 seconds (longer — needs reading) |
| `warning` | ⚠️ | Amber `#F57F17` | 6 seconds |
| `info` | ℹ️ | Blue `#1565C0` | 4 seconds |
| `loading` | ⏳ spinner | Gray | Never auto-dismisses — removed by code |

### Behavior

| Property | Spec |
|---|---|
| Stack | Max 3 toasts visible. 4th pushes oldest off. |
| Hover pause | Mouse hover pauses auto-dismiss timer |
| Dismiss | [✕] button always present. Click = immediate dismiss |
| Action | Optional action link inside toast: "Undo", "View", "Retry" |
| Animation | Slide in from right (desktop) / top (mobile), 200ms |
| Queue | Rapid triggers queue — each waits for previous to dismiss |

### Usage
```markdown
→ Toast: success — "Student enrolled successfully"
→ Toast: error — "Failed to send OTP. Retry?" [Retry action]
→ Toast: loading — "Exporting 1,247 records..."
```

---

## Alert Banner

> Persistent, inline. Does not auto-dismiss. Requires user action or stays until condition resolves.

### When to Use
- Form validation summary (multiple errors)
- Page-level warnings (subscription expiring, BGV pending)
- Informational notices (exam in progress, maintenance window)

### Layout
```
┌────────────────────────────────────────────────────────────────┐
│ [⚠️]  15 staff members have pending BGV verification.          │
│        Complete before 31 March or access will be suspended.   │
│                         [Review Now]           [Dismiss] [✕]  │
└────────────────────────────────────────────────────────────────┘
```

### Variants

| Type | Left border color | Background | Icon |
|---|---|---|---|
| `error` | `#C62828` | `#FFEBEE` | ❌ |
| `warning` | `#E65100` | `#FFF3E0` | ⚠️ |
| `info` | `#1565C0` | `#E3F2FD` | ℹ️ |
| `success` | `#2E7D32` | `#E8F5E9` | ✅ |
| `neutral` | `#455A64` | `#ECEFF1` | 📋 |

### Placement
- **Page-level:** Below page header, above page content. Full-width.
- **Section-level:** Inside a card or form section. Scoped width.
- **Form inline:** Below the specific field with error. Not full-width.

---

## Confirm Dialog

> Blocking modal. User MUST respond before continuing.
> See also [02-modal-drawer.md](02-modal-drawer.md) for modal specs.

### Variants

| Type | Icon | Primary button | Use Case |
|---|---|---|---|
| `confirm` | ❓ | Blue "Confirm" | Non-destructive — change role, send notification |
| `danger` | ⚠️ | Red "Delete" / "Suspend" | Destructive — irreversible actions |
| `typed-confirm` | ⚠️ | Red, disabled until typed | Highly destructive — permanent delete, data wipe |

### Typed Confirm Pattern (Destructive)
```
┌────────────────────────────────────────────┐
│  ⚠️  Permanently delete XYZ School?        │
│                                            │
│  This will delete 1,247 students,          │
│  all exam records, and fee history.        │
│  This action CANNOT be undone.             │
│                                            │
│  Type the institution name to confirm:     │
│  ┌──────────────────────────────────────┐  │
│  │  XYZ School                          │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  [Cancel]          [Delete — IRREVERSIBLE] │
│                    (red, enabled only when │
│                     text matches exactly)  │
└────────────────────────────────────────────┘
```

---

## Empty State

> Shown when a list/table has no data.

### Layout
```
┌────────────────────────────────────────────────────┐
│                                                    │
│          [Context-appropriate illustration]        │
│                                                    │
│          No [entity] found                         │
│                                                    │
│     [Contextual message — why it's empty]          │
│     e.g. "No students match your current filters"  │
│                                                    │
│     [Primary CTA]          [Secondary CTA]         │
│     e.g. "Add Student"     "Clear Filters"         │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Empty State Types

| Scenario | Heading | Primary CTA |
|---|---|---|
| No data at all (fresh) | "No [items] yet" | "Add first [item]" |
| Filtered with no results | "No results for '[query]'" | "Clear filters" |
| No permission to view | "You don't have access to this" | "Request access" |
| Error loading | "Failed to load [items]" | "Retry" |
| Feature not enabled | "[Feature] is not enabled" | "Contact admin" |
| Search no results | "No results for '[search term]'" | "Try different keywords" |

---

## Usage in Page Specs

```markdown
→ Alert: warning — "3 staff members have no BGV. Required by POCSO Act."
   Action: [Review BGV List]
   Placement: Page-level banner, below header

→ Toast: success — "Attendance saved for 124 students"
→ Toast: error — "Failed to save. Check your connection." [Retry]

→ Empty state: No students match filter
   Heading: "No students found"
   Message: "No Class 12 students match 'Fee Defaulter' status."
   CTA: [Clear Filters]
```
