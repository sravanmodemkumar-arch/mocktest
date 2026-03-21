# 21 — Transport Fee Collection

> **URL:** `/group/transport/fees/collection/`
> **File:** `21-transport-fee-collection.md`
> **Template:** `portal_base.html`
> **Priority:** P0
> **Role:** Group Transport Fee Manager (primary) · CFO (view) · Transport Director (view)

---

## 1. Purpose

Tracks all transport fee payments across every branch — receipts, collection rates, branch-wise breakdown, and monthly reconciliation. Shows the fee manager which branches are collecting well and which are lagging, with the ability to drill into student-level payment records.

This page is the financial operations view. The Fee Structure (Page 20) defines what is charged; this page tracks what has been collected.

---

## 2. Role Access

| Role | Level | Access | Notes |
|---|---|---|---|
| Group Transport Fee Manager | G3 | Full | Primary owner |
| Group CFO | G1 | Read-only — revenue reporting | View only |
| Group Transport Director | G3 | View — collection health | Read only |
| Branch Accountant | Branch role | View own branch only | Scoped |

---

## 3. Page Layout

### 3.1 Breadcrumb
```
Group HQ  ›  Transport Management  ›  Transport Fee Collection
```

### 3.2 Page Header
- **Title:** `Transport Fee Collection`
- **Subtitle:** `AY [current] · [Month] · Collection Rate: [N]%`
- **Right controls:** `Record Payment` · `Export` · `Advanced Filters`

### 3.3 Alert Banner

| Condition | Banner Text | Severity |
|---|---|---|
| Branch collection < 60% | "[Branch] transport fee collection is only [N]% this month." | Red |
| Collection < 75% overall | "Overall transport fee collection is [N]% — below target of 85%." | Amber |

---

## 4. KPI Summary Bar

| Card | Metric | Colour Rule |
|---|---|---|
| Total Billed (Month) | ₹ | Blue |
| Total Collected (Month) | ₹ | Blue |
| Collection Rate | % | Green ≥ 85% · Yellow 65–85% · Red < 65% |
| Total Outstanding | ₹ | Yellow > 0 |
| Payments Received Today | Count | Blue |
| Refunds Processed (Month) | ₹ | Blue |

---

## 5. Sections

### 5.1 Branch Collection Table

**Filters:**
| Filter | Type | Options |
|---|---|---|
| Branch | Multi-select | All |
| Month | Month picker | Current / previous months |
| Collection Rate | Radio | All / ≥ 85% / 65–85% / < 65% |

**Columns:** Branch · Students on Transport · Billed (₹) · Collected (₹) · Collection % · Outstanding (₹) · Defaulters (30d+) · Last Reminder · Actions (View · Send Reminder)

**Default sort:** Collection % ascending.

---

### 5.2 Payment Records Table

> All individual payment transactions — search by student, receipt, date.

**Filters:** Branch · Student name/roll · Date range · Payment mode (Cash / Online / Cheque / DD) · Term

**Columns:** Receipt No · Student Name · Branch · Route · Amount (₹) · Payment Mode · Date · Term · Recorded By · [View Receipt]

**Pagination:** Server-side · 25/page.

---

### 5.3 Monthly Collection Trend (Chart)

**Chart — 12-month bar chart:** Billed vs Collected per month. Line overlay: Collection %.

---

## 6. Drawers

### 6.1 Drawer: `record-payment`
- **Width:** 520px
- **Fields:** Branch · Student (searchable) · Amount (₹) · Payment Mode (Cash / Online / Cheque / DD) · Transaction/Cheque Reference · Date · Term · Notes
- **On save:** Receipt generated; student fee status updated; audit log entry

### 6.2 Drawer: `payment-detail`
- **Width:** 480px
- Receipt details, student name, route, fee plan, payment mode, recorded by, timestamp
- [Download Receipt PDF]

---

## 7. Toast Messages

| Action | Toast | Type | Duration |
|---|---|---|---|
| Payment recorded | "Payment of ₹[N] recorded for [Name]. Receipt [No] generated." | Success | 4s |
| Reminder sent | "Fee reminders sent to [N] defaulters at [Branch]." | Info | 4s |
| Export ready | "Collection report export ready. Download below." | Info | 4s |

---

## 8. Empty States

| Condition | Heading | Description | CTA |
|---|---|---|---|
| No payments this month | "No Payments Recorded" | "Record the first payment for this month." | [Record Payment] |
| 100% collection | "Full Collection Achieved" | "All transport fees collected for this month." | — |

---

## 9. Loader States

| Trigger | Loader Type |
|---|---|
| Page load | Skeleton: 6 KPI cards + branch table + payment table + chart |
| Filter/search | Table body skeleton |
| Record payment drawer | 520px skeleton |

---

## 10. Role-Based UI Visibility

| Element | Fee Manager G3 | CFO G1 | Transport Director G3 |
|---|---|---|---|
| Record Payment | ✅ | ❌ | ❌ |
| Send Reminder | ✅ | ❌ | ✅ |
| View All Branches | ✅ | ✅ | ✅ |
| Export | ✅ | ✅ | ✅ |

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/group/{group_id}/transport/fees/collection/` | JWT (G3+) | Collection overview |
| GET | `/api/v1/group/{group_id}/transport/fees/collection/payments/` | JWT (G3+) | Payment records |
| POST | `/api/v1/group/{group_id}/transport/fees/collection/payments/` | JWT (G3+) | Record payment |
| GET | `/api/v1/group/{group_id}/transport/fees/collection/payments/{id}/` | JWT (G3+) | Payment detail |
| GET | `/api/v1/group/{group_id}/transport/fees/collection/trends/` | JWT (G3+) | 12-month chart data |
| POST | `/api/v1/group/{group_id}/transport/fees/collection/reminders/bulk/` | JWT (G3+) | Send reminders |
| GET | `/api/v1/group/{group_id}/transport/fees/collection/export/` | JWT (G3+) | Export |

---

*Page spec version: 1.0 · Last updated: 2026-03-21*
