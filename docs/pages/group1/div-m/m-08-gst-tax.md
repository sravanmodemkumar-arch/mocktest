# M-08 — GST & Tax

**Route:** `GET /finance/gst/`
**Method:** Django `TemplateView` + HTMX part-loads
**Primary role:** GST / Tax Consultant (#72)
**Also sees:** Finance Manager (#69) read-only + filing sign-off; Finance Analyst (#101) read-only

---

## Purpose

GST compliance workspace for EduForge's education technology platform. EduForge supplies "online examination and assessment services" to educational institutions — classified under SAC 9993 (Education Services). GST rate: 18% (CGST 9% + SGST 9% for intra-state; IGST 18% for inter-state). At 2,050 institutions across India, invoices generate both intra-state (Telangana) and inter-state transactions requiring correct CGST/SGST vs IGST split.

GST Consultant uses this page to: (1) reconcile monthly invoice data for GSTR-1 B2B filing (all invoices to registered businesses), (2) compute and file GSTR-3B (summary return with tax payment), (3) track TDS (194J — professional services) and TCS (Razorpay 194-O), and (4) prepare the annual GSTR-9. Finance Manager signs off on each filing before submission. Finance Analyst uses the data for investor reporting of net revenue (revenue after GST liability).

---

## Data Sources

| Section | Source | Cache TTL |
|---|---|---|
| Compliance KPI strip | `finance_gst_return` + `finance_invoice` GST fields for current period | 5 min |
| Filing calendar | `finance_gst_return` ORDER BY due_date ASC | 60 min |
| B2B invoice table (GSTR-1) | `finance_invoice` WHERE status IN ('PAID','PARTIALLY_PAID','OVERDUE') JOIN `institution` (GSTIN) for selected period | 5 min |
| HSN/SAC summary | `finance_invoice` GROUP BY period: SUM(subtotal, cgst, sgst, igst) | 15 min |
| TDS tracker | `finance_payment` WHERE tds_deducted_paise > 0 (manual entry by GST Consultant) | 5 min |
| TCS tracker | `finance_razorpay_settlement` SUM(tcs_paise) GROUP BY month | 15 min |

---

## URL Parameters

| Param | Values | Default | Effect |
|---|---|---|---|
| `?return_type` | `GSTR1`, `GSTR3B`, `GSTR9` | — | Pre-filters to that return type |
| `?period` | `YYYY-MM` (for GSTR1/3B) or `YYYY` (for GSTR9) | current month | Reporting period |
| `?tab` | `calendar`, `b2b_invoices`, `hsn_summary`, `tds_tcs` | `calendar` | Active tab |
| `?q` | string | — | ILIKE on institution_name, GSTIN (in B2B invoice tab) |
| `?gstin_status` | `registered`, `unregistered`, `composite` | — | Filter institutions by GST registration type |
| `?export` | `csv`, `json` | — | Export for GSTN upload |

---

## HTMX Part-Load Routes

| Part | Route | Trigger | Target ID |
|---|---|---|---|
| Compliance KPI strip | `?part=kpi` | Page load | `#gst-kpi` |
| Filing calendar | `?part=calendar` | Tab: calendar | `#gst-calendar` |
| B2B invoice table | `?part=b2b_table` | Tab: b2b_invoices + filter | `#gst-b2b` |
| HSN summary | `?part=hsn` | Tab: hsn_summary | `#gst-hsn` |
| TDS/TCS tracker | `?part=tds_tcs` | Tab: tds_tcs | `#gst-tds` |
| File return modal | `?part=file_modal&id={id}` | [Mark as Filed] | `#modal-container` |

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  GST & Tax Compliance   Period: [Mar 2026 ▼]                        │
├─────────────────────────────────────────────────────────────────────┤
│  COMPLIANCE KPI STRIP (5 tiles)                                     │
├─────────────────────────────────────────────────────────────────────┤
│  [Filing Calendar] [B2B Invoices (GSTR-1)] [HSN Summary] [TDS/TCS] │
├─────────────────────────────────────────────────────────────────────┤
│  [Active tab content]                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Compliance KPI Strip (5 tiles)

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ ₹6.84L   │ │ ₹3.42L   │ │ ₹3.42L   │ │ ₹0       │ │ 2        │
│ Total GST│ │ CGST     │ │ SGST     │ │ IGST     │ │ Returns  │
│ Liability│ │ Liability│ │ Liability│ │ Liability│ │ Due Soon │
│ (Mar 26) │ │          │ │          │ │ (0 inter │ │ GSTR-1:  │
│          │ │          │ │          │ │ -state)  │ │ 11 Apr ⚠ │
└──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
```

- **Tile 1 (Total GST Liability):** SUM(cgst + sgst + igst) for PAID invoices in the selected period. This is the amount EduForge owes to the GST authority for that period.
- **Tiles 2–4 (CGST/SGST/IGST):** Individual component sums. CGST = SGST for intra-state; IGST = 0 if all institutions are in Telangana. These should balance: CGST=SGST and IGST can be 0 to non-zero depending on inter-state transactions.
- **Tile 5 (Returns Due Soon):** Count of `finance_gst_return` WHERE status='UPCOMING' AND due_date ≤ today+14d. Amber if > 0; red if any is due ≤ 3 days.

---

## Tab: Filing Calendar

Full-year GST return schedule with status of each filing.

```
┌────────────────────────────────────────────────────────────────────────┐
│  GST Filing Calendar — FY 2025-26                                      │
├──────────────────────────────────────────────────────────────────────  │
│  Return  Period      Due Date      Status       ARN / Notes            │
│  ─────   ─────────  ──────────    ──────────   ─────────────────────── │
│  GSTR-1  Jan 2026   11 Feb 2026   ✓ FILED      AA12345678901234        │
│  GSTR-3B Jan 2026   20 Feb 2026   ✓ FILED      AA98765432101234        │
│  GSTR-1  Feb 2026   11 Mar 2026   ✓ FILED      AA11122233301234        │
│  GSTR-3B Feb 2026   20 Mar 2026   ✓ FILED      AA44455566601234        │
│  GSTR-1  Mar 2026   11 Apr 2026   UPCOMING ⚠   (in 21 days)           │
│  GSTR-3B Mar 2026   20 Apr 2026   UPCOMING     (in 30 days)            │
│  GSTR-9  FY 2024-25 31 Dec 2025   OVERDUE ⛔   MISSED — penalty accruing│
└────────────────────────────────────────────────────────────────────────┘
```

Colour coding:
- FILED (green): `bg-green-900/50 text-green-400` + ARN shown
- UPCOMING ≤ 7 days (amber): `bg-amber-900/50 text-amber-300` + days countdown
- UPCOMING ≤ 3 days (red): pulsing dot
- OVERDUE (dark red): `bg-red-900/50 text-red-400` + warning icon + "penalty accruing" sub-label
- FILED_WITH_PENALTY (amber): shows penalty amount in notes

Actions per row:
- [Mark as Filed] (GST Consultant #72): opens filing modal to record ARN + filing date + tax paid amounts
- [View Invoices for Period] (→ B2B Invoices tab filtered to that period)
- [Export for GSTN] → CSV/JSON in GSTN-compatible format

---

## [Mark as Filed] Modal (480px)

```
  Mark GSTR-1 as Filed — Mar 2026
  ──────────────────────────────────────────────────────
  Filing Date*  [11 Apr 2026]
  ARN*          [AA                                   ]
  (Acknowledgement Reference Number from GSTN portal)
  Total taxable turnover (₹)*  [38,00,000]
  CGST paid (₹)*              [3,42,000]
  SGST paid (₹)*              [3,42,000]
  IGST paid (₹)*              [0]
  Notes  [Filed on time; no amendments required      ]
  ──────────────────────────────────────────────────────
  FM sign-off required: ☑  (Finance Manager #69 must confirm)
  ──────────────────────────────────────────────────────
  [Cancel]                        [Submit for FM Review]
```

**Two-step process:**
1. GST Consultant (#72) fills in ARN + amounts → status → 'FILED_PENDING_FM'. FM (#69) receives in-app notification.
2. FM (#69) reviews and confirms (or rejects with notes). On confirmation: status → 'FILED'; `filed_by_id`, `filing_date`, `arn` set.

**Validation:**
- ARN: required; regex `^[A-Z]{2}[0-9]{14}$` (GSTN ARN format)
- Filing Date: required; ≤ today
- Tax amounts: required; must be ≥ 0; CGST must equal SGST (invariant for EduForge — dual rate enforcement)
- FM sign-off: always required (hardcoded; not configurable)

---

## Tab: B2B Invoices (GSTR-1 Preparation)

Invoice list for B2B supplies (institution GST-registered customers) for the selected period.

> GSTR-1 requires reporting every B2B invoice (invoices to GST-registered institutions) with the institution's GSTIN, invoice number, value, tax amounts, and place of supply.

**Filter row:**

```
Period: [Mar 2026 ▼]   GSTIN Status: [All ▼]   Type: [All ▼]
[🔍 Search institution, GSTIN...]
Showing 1,842 invoices (B2B: 1,756 · Unregistered: 86)
[Export for GSTN Upload (JSON)]  [Export CSV]
```

**B2B Invoice Table** (sortable, 25 rows/page):

| Column | Description |
|---|---|
| Invoice # | `INV-YYYY-NNNNN` monospace |
| Invoice Date | `finance_invoice.issue_date` |
| Institution Name | Truncated name |
| GSTIN | Institution's GSTIN from `institution.gstin`; "Unregistered" badge if NULL |
| Place of Supply | State code (2-digit); determines CGST+SGST vs IGST |
| Taxable Value (₹) | `finance_invoice.subtotal_paise` |
| CGST (₹) | `finance_invoice.cgst_paise`; only if intra-state |
| SGST (₹) | `finance_invoice.sgst_paise`; only if intra-state |
| IGST (₹) | `finance_invoice.igst_paise`; only if inter-state |
| Total Invoice Value (₹) | `finance_invoice.total_paise` |
| Status | Invoice payment status (for GSTR-1 only PAID invoices are mandatory; SENT/OVERDUE can also be reported) |

**GSTIN validation:** If `institution.gstin` is present, shows a ✓ or ✗ icon based on GSTN format validation (regex: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`). Invalid GSTINs shown in red — GST Consultant must correct before filing.

**Place of Supply logic:** If institution.state == 'Telangana' (EduForge's state): CGST+SGST. All other states: IGST. This should be consistent with the CGst/SGST columns in the invoice.

**Unregistered supplies:** Institutions without a GSTIN are "B2C" supplies. GSTR-1 reports these aggregated (not per-invoice) if each invoice < ₹2.5L. Over ₹2.5L: must be reported per-invoice even for B2C.

**[Export for GSTN Upload (JSON)]:** Generates a GSTN-compatible JSON file for the selected period in the format required by the GSTN offline utility. Available to GST Consultant (#72) only.

---

## Tab: HSN / SAC Summary

Summary table for HSN/SAC code reporting (GSTR-1 Table 12 and GSTR-9 Table 17).

```
  HSN/SAC Summary — Mar 2026
  ─────────────────────────────────────────────────────────────────
  SAC Code  Description                   Qty   Taxable    GST
  9993      Education & Exam Services   2,050  ₹38,00,000  ₹6,84,000
  ─────────────────────────────────────────────────────────────────
  Total                                 2,050  ₹38,00,000  ₹6,84,000
```

EduForge has a single SAC code (9993) for all its services. The GST Consultant verifies this table matches the GSTR-1 totals.

Below: Breakdowns:
- By intra-state / inter-state split (for the IGST table in GSTR-1)
- By tax rate (18% only — EduForge does not supply exempt services)
- Monthly trend: bar chart of taxable value × 12 months

---

## Tab: TDS / TCS Tracker

Two sub-sections: TDS received from customers; TCS deducted by Razorpay.

### TDS Received (Section 194J — Professional Services)

Some government institutions (central and state universities, PSUs) deduct TDS at 10% before paying invoices. GST Consultant tracks these to claim TDS credit in advance tax computations.

| Column | Description |
|---|---|
| Institution | Name |
| Invoice # | Original invoice |
| Invoice Amount (₹) | Gross |
| TDS Deducted (₹) | Usually 10% of invoice value |
| Amount Received (₹) | Invoice - TDS |
| TDS Certificate # | Form 16B reference |
| Quarter | Q1/Q2/Q3/Q4 of FY |

[+ Log TDS Entry]: manual form to record a TDS deduction from an institution. Fields: institution, invoice, amount, TDS rate, certificate number, date. POST `/finance/gst/tds/`. GST Consultant only.

### TCS from Razorpay (Section 194-O)

Razorpay deducts TCS (Tax Collected at Source) at 1% on all payments collected via their platform, as per IT Act Section 194-O. This TCS is claimable by EduForge as advance income tax.

```
  TCS from Razorpay
  Month      Gross Payments   TCS (1%)   Settlement ID
  Jan 2026   ₹3,84,200        ₹3,842     setl_Ixxxx
  Feb 2026   ₹4,12,800        ₹4,128     setl_Ixxxx
  Mar 2026   ₹3,91,500        ₹3,915     setl_Ixxxx
  ────────────────────────────────────────────────────
  YTD Total  ₹11,88,500       ₹11,885
```

Data sourced from `finance_razorpay_settlement.tcs_paise`. Read-only (populated by Task M-3 sync). [Export TCS Report]: CSV for Form 27C filing. GST Consultant + FM only.

---

## Empty States

| Condition | Message |
|---|---|
| No invoices for selected period | "No invoices found for [period]. Invoices are generated on the 1st of each month by Task M-2." |
| All returns filed | "All GST returns filed for FY 2025-26. Next return: GSTR-1 for Apr 2026 due 11 May 2026." |
| No TDS entries logged | "No TDS deductions logged for this period. [+ Log TDS Entry] if institutions have deducted TDS." |
| TCS from Razorpay: no data | "No Razorpay settlements in this period. Run settlement sync in M-06 first." |

---

## Toast Messages

| Action | Toast | Type |
|---|---|---|
| GSTR-1 marked as filed (pending FM) | "GSTR-1 for [period] submitted for Finance Manager review." | Amber |
| FM confirmed filing | "GSTR-1 for [period] confirmed as FILED. ARN recorded." | Green |
| FM rejected filing (needs correction) | "Filing rejected: [FM notes]. Please correct and resubmit." | Red |
| GSTR-3B marked as filed | "GSTR-3B for [period] filed. Tax liability booked." | Green |
| GSTN JSON exported | "GSTR-1 data exported for GSTN upload." | Green |
| TDS entry logged | "TDS entry logged: ₹[amount] from [institution]." | Green |
| Invalid GSTIN detected | "Warning: [institution] has an invalid GSTIN format. Correct before filing." | Amber |

---

## Authorization

**Route guard:** `@division_m_required(allowed_roles=[69, 72, 101])`.

| Scenario | Behaviour |
|---|---|
| GST Consultant (#72) | Full page access; [Mark as Filed] + [Export for GSTN] + [Log TDS]; FM sign-off actions hidden (FM-only) |
| Finance Manager (#69) | Confirm/reject filings; read-only on all tabs; no export of GSTN JSON (GST Consultant's tool) |
| Finance Analyst (#101) | Read-only across all tabs; export CSV; GSTN JSON export not allowed |
| Other Finance roles (#70, #71, #73, #74, #102) | 403 — no access |

---

## Role-Based UI Visibility Summary

| Element | 69 FM | 72 GST Consultant | 101 Analyst |
|---|---|---|---|
| Compliance KPI strip | Yes | Yes | Yes (read) |
| Filing Calendar | Full read + confirm/reject | Full read + [Mark as Filed] | Read only |
| [Mark as Filed] | No (FM signs off, not files) | Yes | No |
| FM Confirm/Reject Filing | Yes (exclusive) | No | No |
| B2B Invoice Table | Read | Full + GSTN export | Read + CSV export |
| GSTN JSON Export | No | Yes | No |
| HSN/SAC Summary | Read | Full | Read |
| TDS Tracker: Log Entry | No | Yes | No |
| TDS Tracker: Read | Yes | Yes | Yes |
| TCS Tracker | Yes (read) | Yes (full + export) | Yes (read) |
| Export TCS Report | Yes | Yes | No |

---

## Performance Requirements

| Metric | Target | Notes |
|---|---|---|
| Initial page load (SSR) | < 2s P95 | Compliance KPI strip + filing calendar from cache |
| Compliance KPI strip | < 500ms P95 (cache hit) | 15-min TTL; `finance_gst_return` aggregation |
| Filing Calendar (12 rows) | < 400ms P95 (cache hit) | 15-min TTL |
| B2B invoice table (25 rows) | < 500ms P95 (cache hit) | 10-min TTL; `finance_invoice` WHERE gstin IS NOT NULL |
| HSN/SAC summary | < 600ms P95 (cache hit) | 30-min TTL; aggregated by SAC code |
| TDS tracker table | < 400ms P95 (cache hit) | 15-min TTL |
| GSTN JSON export generation | < 5s for ≤ 1,000 invoices | Server-side; JSON formatted to GSTN offline utility schema |
| CSV export | < 3s for ≤ 2,000 rows | Streaming response |

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `g` `g` | Go to GST & Tax (M-08) |
| `1`–`4` | Switch tab: Filing Calendar / B2B Invoices / HSN Summary / TDS-TCS |
| `e` | Export CSV (GST Consultant, FM) |
| `j` | Export GSTN JSON (GST Consultant only) |
| `Esc` | Close open modal |
| `?` | Show keyboard shortcut help overlay |

