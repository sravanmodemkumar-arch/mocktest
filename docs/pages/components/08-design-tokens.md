# Component: Design Tokens — Colors, Typography, Spacing

> Single source of truth for all visual design decisions.
> All page specs use token names, not raw hex values.
> Updating a token here updates it everywhere.

---

## Color Tokens — Per Portal

### Portal Primary Colors

| Portal | Primary | On Primary | Container | Label |
|---|---|---|---|---|
| Platform Admin | `#1A237E` | `#FFFFFF` | `#E8EAF6` | Deep Indigo |
| School | `#1565C0` | `#FFFFFF` | `#E3F2FD` | Institutional Blue |
| College | `#283593` | `#FFFFFF` | `#E8EAF6` | College Indigo |
| Coaching | `#B71C1C` | `#FFFFFF` | `#FFEBEE` | Coaching Red |
| SSC Domain | `#1B5E20` | `#FFFFFF` | `#E8F5E9` | Government Green |
| RRB Domain | `#E65100` | `#FFFFFF` | `#FFF3E0` | Railway Orange |
| UPSC Domain | `#4A148C` | `#FFFFFF` | `#F3E5F5` | UPSC Purple |
| Banking Domain | `#004D40` | `#FFFFFF` | `#E0F2F1` | Banking Teal |
| Parent Portal | `#4A148C` | `#FFFFFF` | `#F3E5F5` | Purple |
| Student Portal | `#006064` | `#FFFFFF` | `#E0F2F1` | Teal |
| B2B Partner | `#263238` | `#FFFFFF` | `#ECEFF1` | Dark Slate |
| TSP (default) | Operator-defined | Operator | Operator | Custom |

### Semantic Color Tokens (All Portals)

```css
/* Surface */
--surface:              #FFFFFF
--surface-variant:      #F5F5F5
--surface-container:    #FAFAFA
--on-surface:           #1C1B1F
--on-surface-variant:   #49454F
--outline:              #79747E
--outline-variant:      #CAC4D0

/* Status */
--error:                #C62828
--error-container:      #FFEBEE
--on-error:             #FFFFFF
--warning:              #E65100
--warning-container:    #FFF3E0
--success:              #2E7D32
--success-container:    #E8F5E9
--info:                 #1565C0
--info-container:       #E3F2FD

/* Text */
--text-primary:         #212121
--text-secondary:       #757575
--text-disabled:        #BDBDBD
--text-hint:            #9E9E9E

/* WhatsApp (used in OTP button) */
--whatsapp:             #25D366
--whatsapp-dark:        #128C7E
```

---

## Typography

### Font Family
- **Primary:** `Inter` (Latin, weights: 400, 500, 600, 700)
- **Telugu:** `Noto Sans Telugu` (regional language support)
- **Hindi:** `Noto Sans Devanagari`
- **Monospace:** `JetBrains Mono` (for code, exam keys, OTP display)
- Fallback: `system-ui, -apple-system, sans-serif`

### Type Scale

| Token | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| `--display-lg` | 48px | 700 | 1.2 | Hero headlines, landing |
| `--display-md` | 36px | 700 | 1.2 | Section heroes |
| `--display-sm` | 28px | 700 | 1.3 | Page titles |
| `--headline-lg` | 24px | 600 | 1.3 | Card headings, drawer titles |
| `--headline-md` | 20px | 600 | 1.4 | Section headings |
| `--headline-sm` | 18px | 600 | 1.4 | Modal titles, form sections |
| `--title-lg` | 16px | 600 | 1.5 | Table headers, nav items |
| `--title-md` | 14px | 600 | 1.5 | Labels, sub-headers |
| `--title-sm` | 12px | 600 | 1.5 | Small labels, breadcrumbs |
| `--body-lg` | 16px | 400 | 1.6 | Primary body text |
| `--body-md` | 14px | 400 | 1.6 | Secondary body, table cells |
| `--body-sm` | 12px | 400 | 1.6 | Helper text, captions |
| `--label-lg` | 14px | 500 | 1.4 | Button text, input labels |
| `--label-md` | 12px | 500 | 1.4 | Badges, chips |
| `--label-sm` | 11px | 500 | 1.4 | Tiny badges, timestamps |

---

## Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-0` | 0px | |
| `--space-1` | 4px | Icon padding, tight gaps |
| `--space-2` | 8px | Inner card padding (compact) |
| `--space-3` | 12px | List item padding, chip padding |
| `--space-4` | 16px | Standard inner padding |
| `--space-5` | 20px | Section gaps |
| `--space-6` | 24px | Card padding |
| `--space-8` | 32px | Section margins |
| `--space-10` | 40px | Large section gaps |
| `--space-12` | 48px | Page-level padding |
| `--space-16` | 64px | Hero padding |

### Component-Specific Spacing

| Component | Padding | Gap |
|---|---|---|
| Page container | `24px` horizontal, `24px` top | — |
| Card | `24px` all sides | — |
| Table row | `16px` vertical | `16px` between columns |
| Input field | `16px` horizontal, `14px` vertical | — |
| Button (md) | `16px` horizontal, `10px` vertical | — |
| Nav item | `12px` vertical, `16px` horizontal | — |
| Badge | `3px` vertical, `8px` horizontal | — |

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-xs` | 4px | Tags, small chips |
| `--radius-sm` | 8px | Input fields, small cards |
| `--radius-md` | 12px | Cards, modals, buttons |
| `--radius-lg` | 16px | Large cards, drawers |
| `--radius-xl` | 24px | Floating action panels |
| `--radius-full` | 9999px | Pills, avatars, toggle switches |

---

## Shadows (Elevation)

| Token | Value | Usage |
|---|---|---|
| `--shadow-0` | none | Flat elements |
| `--shadow-1` | `0 1px 2px rgba(0,0,0,0.08)` | Subtle card border |
| `--shadow-2` | `0 2px 8px rgba(0,0,0,0.12)` | Cards, input focus |
| `--shadow-3` | `0 4px 16px rgba(0,0,0,0.16)` | Dropdowns, date picker |
| `--shadow-4` | `0 8px 24px rgba(0,0,0,0.20)` | Modals, drawers |
| `--shadow-5` | `0 16px 48px rgba(0,0,0,0.28)` | Top-level overlays |

---

## Breakpoints

| Token | Width | Layout |
|---|---|---|
| `--bp-xs` | 0–479px | Mobile portrait — single column |
| `--bp-sm` | 480–767px | Mobile landscape — single column, max 480 |
| `--bp-md` | 768–1023px | Tablet — sidebar hidden, hamburger menu |
| `--bp-lg` | 1024–1279px | Desktop S — sidebar 200px, content fluid |
| `--bp-xl` | 1280–1535px | Desktop M — sidebar 240px |
| `--bp-2xl` | 1536px+ | Desktop L — sidebar 260px, max content 1400px |

### Sidebar Width by Breakpoint

| Breakpoint | Sidebar Width | Mode |
|---|---|---|
| xs / sm | 0px | Hidden (overlay on hamburger) |
| md | 0px (default) | Overlay on hamburger click |
| lg | 200px | Collapsed icon-only default |
| xl | 240px | Expanded text + icon default |
| 2xl | 260px | Expanded, comfortable |

---

## Z-Index Scale

| Layer | Z-Index | Component |
|---|---|---|
| Base | 0 | Normal page flow |
| Raised | 10 | Cards on hover |
| Dropdown | 100 | Select menus, date picker |
| Sticky header | 200 | Table column headers, top nav |
| Sidebar | 300 | Side navigation |
| Drawer | 500 | Side drawer overlay |
| Modal | 1000 | Modal dialogs |
| Toast | 1200 | Toast notifications |
| Critical | 9000 | Exam lockdown overlay, critical security alerts |

---

## Motion / Animation

| Token | Duration | Easing | Usage |
|---|---|---|---|
| `--motion-instant` | 0ms | — | Immediate state changes |
| `--motion-fast` | 100ms | ease-out | Button press, checkbox |
| `--motion-default` | 200ms | ease-out | Default transitions |
| `--motion-medium` | 300ms | ease-in-out | Drawer slide, modal |
| `--motion-slow` | 500ms | ease-in-out | Page transitions |

### Accessibility Override
```css
@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0.01ms !important; }
}
```
