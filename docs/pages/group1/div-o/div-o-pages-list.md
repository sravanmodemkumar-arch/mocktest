# Division O — HR & Administration: Pages List

> 8 pages · 6 roles (3 original + 3 new: #105, #106, #107)
> All pages live under the internal HR portal (`/hr/`) — no EduForge platform system access.
> Covers: employee lifecycle, talent acquisition, payroll & statutory compliance, leave & attendance, performance management, and learning & development.

---

## Roles

| # | Role | Level | Owns |
|---|---|---|---|
| 79 | HR Manager | 0 | HR strategy, policy, payroll approval, statutory compliance oversight, HR analytics, POSH chair |
| 80 | Recruiter | 0 | Full-cycle talent acquisition, ATS, interview coordination, offer rollout |
| 81 | Office Administrator | 0 | Facilities, asset register, vendor payments, travel, petty cash |
| 105 | Payroll & Compliance Executive | 0 | Monthly payroll run, PF/ESI/PT/TDS filing, Form 16, salary register, F&F settlement |
| 106 | HR Business Partner | 0 | OKRs, performance review cycles, PIPs, culture surveys, exit programme, HRBP for Div C/D/E/F |
| 107 | L&D Coordinator | 0 | Training calendar, LMS, skills matrix, certifications, induction, compliance training |

> **Why #105?** At 100+ employees across multiple states, monthly payroll + multi-state statutory compliance (PF ECR, ESI half-yearly return, state-wise Professional Tax, quarterly TDS 24Q, annual Form 16) is a full-time specialised function. An HR Manager handling strategy, culture, and hiring cannot also manage payroll computation and statutory filings without compliance risk.
>
> **Why #106?** Performance management and culture are strategic HR functions distinct from operational HR. An HRBP embedded with technical divisions (C/D/E/F — 35+ roles at scale) runs quarterly OKR cadences, probation reviews, and manages sensitive PIP conversations — work that requires dedicated capacity and independence from the hiring or payroll function.
>
> **Why #107?** EduForge staff — especially SMEs (Division D), Support (Division I), and CS teams (Division J) — require continuous upskilling as the product evolves. POSH awareness and data privacy training are mandatory compliance obligations. An L&D Coordinator maintains the skills matrix, runs induction for every new joiner, and procures external training — freeing the HRBP to focus on performance, not logistics.

---

## Pages

| Page | Route | Title | Primary Role(s) |
|---|---|---|---|
| O-01 | `GET /hr/` | HR Dashboard | HR Manager (#79) |
| O-02 | `GET /hr/employees/` | Employee Directory | HR Manager (#79), HR Business Partner (#106) |
| O-03 | `GET /hr/recruitment/` | Recruitment Pipeline | Recruiter (#80), HR Manager (#79) |
| O-04 | `GET /hr/onboarding/` | Onboarding & Offboarding | HR Manager (#79), Office Administrator (#81) |
| O-05 | `GET /hr/payroll/` | Payroll & Compliance | Payroll & Compliance Executive (#105), HR Manager (#79) |
| O-06 | `GET /hr/leave/` | Leave & Attendance | HR Manager (#79), all Division O roles (own records) |
| O-07 | `GET /hr/performance/` | Performance Management | HR Business Partner (#106), HR Manager (#79) |
| O-08 | `GET /hr/learning/` | Learning & Development | L&D Coordinator (#107), HR Manager (#79) |

---

## Data Model Summary

| Table | Purpose |
|---|---|
| `hr_employee` | Master employee record — name, employee_id, designation, division, role_id, join_date, employment_type (FULL_TIME/PART_TIME/CONTRACT/INTERN), status (ACTIVE/ON_NOTICE/EXITED/INACTIVE), manager_id, work_location, state_code (for PT computation), pf_uan, esic_ip_number |
| `hr_employee_document` | Documents attached to employee — offer letter, appointment letter, Aadhaar, PAN, Form 16, relieving letter, BGV report. Stored in Cloudflare R2, KMS-encrypted. |
| `hr_department` | Division/team lookup for org chart and reporting |
| `hr_position` | Open and filled positions — JD, required skills, approved headcount, budget, linked division, current_status (OPEN/ON_HOLD/CLOSED/FILLED) |
| `hr_candidate` | Applicant records — source, resume_r2_key, current_stage, applied_position_id |
| `hr_interview` | Interview sessions — stage, interviewer_id, scheduled_at, mode (IN_PERSON/VIDEO/TELEPHONIC), feedback_text, recommendation (STRONG_YES/YES/NO/STRONG_NO) |
| `hr_offer` | Offer letters — ctc_breakup (JSONB), offer_status (DRAFT/SENT/ACCEPTED/DECLINED/LAPSED), expected_join_date, offer_letter_r2_key |
| `hr_onboarding_checklist` | Per-employee joining tasks — task_code, task_type (IT/PAYROLL/BGV/DOCUMENTATION/ORIENTATION), assigned_to_role, due_by_day (day N from join_date), completed_at |
| `hr_offboarding_checklist` | Exit checklist per employee — equipment return, access revocation, F&F computation trigger, experience letter dispatch |
| `hr_payroll_run` | Monthly payroll run record — month_year, status (DRAFT/PROCESSING/LOCKED/APPROVED/DISBURSED), total_gross_paise, total_net_paise, run_by, approved_by, disbursed_at |
| `hr_payroll_slip` | Per-employee per-month payslip — earnings JSONB (basic, HRA, special_allowance, LTA, bonus), deductions JSONB (pf_employee, esic_employee, pt, tds_advance, loan_emi), gross_paise, net_paise, payslip_pdf_r2_key |
| `hr_statutory_filing` | Compliance filing tracker — filing_type (PF_ECR/ESI_RETURN/PT_CHALLAN/TDS_24Q/FORM_16/LWF), period, due_date, filed_at, status (UPCOMING/IN_PROGRESS/FILED/ACKNOWLEDGED/OVERDUE), reference_number, challan_r2_key |
| `hr_leave_type` | Leave type master — code (CL/SL/EL/ML/PL/COMP_OFF/LOP/BL), max_days_per_year, carry_forward_max, encashable, applicable_employment_types |
| `hr_leave_balance` | Per-employee per-year leave balances — opening_balance, accrued, consumed, carried_forward, lapsed |
| `hr_leave_request` | Leave applications — leave_type_id, from_date, to_date, days (fractional for half-days), reason, status (PENDING/APPROVED/REJECTED/CANCELLED/AUTO_APPROVED), approved_by, approved_at |
| `hr_attendance_record` | Daily record per employee — date, mode (OFFICE/WFH/OOO/LEAVE/HOLIDAY/WEEKEND), check_in, check_out, source (MANUAL/BIOMETRIC/WFH_SELF_MARK) |
| `hr_performance_cycle` | Review cycle definition — cycle_type (ANNUAL/MID_YEAR/PROBATION/CONFIRMATION), period, self_assessment_deadline, manager_review_deadline, calibration_deadline, status |
| `hr_performance_review` | Per-employee review — cycle_id, self_assessment JSONB, manager_assessment JSONB, calibration_rating (EXCEPTIONAL/EXCEEDS/MEETS/BELOW/UNSATISFACTORY), final_rating, promotion_recommended (bool), increment_pct |
| `hr_okr_objective` | OKR objective per employee per cycle — title, description, weight_pct, status |
| `hr_okr_key_result` | Key results under each objective — metric, target_value, unit, current_value, confidence (ON_TRACK/AT_RISK/OFF_TRACK), last_checkin_at |
| `hr_pip` | Performance Improvement Plans — employee_id, initiated_by, start_date, end_date, goals JSONB, checkpoints JSONB, final_outcome (IMPROVED/EXTENDED/SEPARATED), status |
| `hr_training_course` | Course catalog — title, description, category (TECHNICAL/DOMAIN/COMPLIANCE/LEADERSHIP/SOFT_SKILLS), delivery_mode (IN_HOUSE/EXTERNAL_VENDOR/ONLINE_LMS), duration_hours, mandatory (bool), applicable_roles (array), vendor_name, cost_per_seat_paise |
| `hr_training_enrollment` | Per-employee enrollment — course_id, enrolled_by, enrolled_at, scheduled_date, completion_status (ENROLLED/IN_PROGRESS/COMPLETED/FAILED/DROPPED), score_pct, certificate_r2_key, completion_date |
| `hr_certification` | Professional certifications — employee_id, cert_name, issuing_body, issued_date, expiry_date, cert_doc_r2_key |
| `hr_skills` | Skills inventory — employee_id, skill_name, category, proficiency (BEGINNER/INTERMEDIATE/ADVANCED/EXPERT), last_assessed_at, assessed_by |
| `hr_survey` | Culture/eNPS surveys — type (ENPS/CULTURE_PULSE/EXIT/MANAGER_EFFECTIVENESS), period, status, anonymous (bool) |
| `hr_survey_response` | Individual survey responses — survey_id, respondent_id (nullable if anonymous), response JSONB, submitted_at |
| `hr_asset` | IT/office assets — asset_type (LAPTOP/MONITOR/ACCESS_CARD/HEADSET/DESK_PHONE), serial_number, assigned_to, assigned_at, condition, status (AVAILABLE/ASSIGNED/IN_REPAIR/RETIRED) |

---

## Background Tasks

| Task | Schedule | Owned By |
|---|---|---|
| O-1 — Payroll Run Reminder | 5th of each month, 09:00 IST | O-05 |
| O-2 — PF Challan Deadline Alert | 12th of each month, 09:00 IST (due by 15th) | O-05 |
| O-3 — ESI Challan Deadline Alert | 12th of each month (due by 15th) | O-05 |
| O-4 — TDS Deposit Reminder | 5th of each month (TDS due by 7th) | O-05 |
| O-5 — Leave Balance Accrual | 1st of each month, 00:01 IST — credit monthly EL accrual | O-06 |
| O-6 — Annual Leave Balance Reset | 1 Jan 00:01 IST — carry forward EL (max 30 days), lapse remainder | O-06 |
| O-7 — Leave Auto-Approval | Every 30 min — auto-approve leave requests pending > 3 working days with no manager action | O-06 |
| O-8 — Probation Review Reminder | Daily 09:00 IST — alert HR Manager + HRBP 14 days before 3-month and 6-month completion | O-07 |
| O-9 — Performance Cycle Deadline Alert | Daily 09:00 IST during active cycle — alert reviewers 7 days and 1 day before deadlines | O-07 |
| O-10 — OKR Check-in Nudge | Every Monday 09:00 IST — nudge employees with OKR check-in overdue > 14 days | O-07 |
| O-11 — L&D Completion Reminder | Daily 09:00 IST — remind employees enrolled in mandatory courses with deadline within 7 days | O-08 |
| O-12 — Certification Expiry Scanner | Daily 09:00 IST — flag certifications expiring within 30 days | O-08 |
| O-13 — Document Expiry Scanner | Daily 09:00 IST — flag employee documents (work authorisation, medical fitness certs) expiring within 30 days | O-02 |
| O-14 — Work Anniversary Alert | Daily 07:00 IST — alert HR Manager to employees with work anniversaries in next 7 days | O-01 |
| O-15 — Statutory Filing Status Sync | Daily 08:00 IST — check filing due dates, flip UPCOMING → OVERDUE as appropriate | O-05 |

---

## Critical Statutory Obligations (India Labour Law)

| Obligation | Deadline | Consequence |
|---|---|---|
| PF ECR (Employees' Provident Fund Electronic Challan cum Return) | 15th of each month | Interest @12% p.a. + ₹25/day penalty per EPFO |
| ESI Challan (Employees' State Insurance) | 15th of each month | Penalty + prosecution under ESI Act §85 |
| Professional Tax (state-wise — AP/Telangana/Karnataka) | 10th of each month (challan); annual return by 31 March | State-wise penalties; varies ₹500–₹5,000 per default |
| TDS on Salaries (Form 24Q quarterly + TDS deposit) | TDS deposit by 7th of next month; quarterly return by 31st of next month after quarter end | Interest @1–1.5% per month + ₹200/day late filing fee under §234E |
| Form 16 (TDS certificate to employees) | By 15 June each year | Penalty ₹100/day per Form 16 under §272A |
| POSH Annual Report | By 31 January each year (filing with District Officer) | Penalty up to ₹50,000; loss of licence to operate |
| Shops & Establishment Act registration renewal | Annual (date varies by state) | Penalty + prosecution; may affect contract validity |
| Labour Welfare Fund contribution | Half-yearly (June 15 + December 15 in most states) | State-wise penalties |

---

## Role Cross-Reference with Other Divisions

| Division O Role | Interacts With |
|---|---|
| HR Manager (#79) | CEO (#1) — headcount approvals; Finance Manager (#69) — payroll budget; Legal Officer (#75) — POSH legal escalations; BGV Manager (#39) — employee BGV coordination |
| Recruiter (#80) | Hiring manager in each division (technical screen); Platform Admin (#10) — system access after join; Finance Manager (#69) — budget sign-off for new hires |
| Office Administrator (#81) | DevOps/SRE Engineer (#14) — IT asset coordination (laptops, VPN tokens); Finance Manager (#69) — vendor payment approvals; BGV Manager (#39) — physical access card management |
| Payroll & Compliance Executive (#105) | Finance Manager (#69) — TDS reconciliation, P&L impact; GST/Tax Consultant (#72) — TDS 194J for contractors vs salary; Data Engineer (#43) — payroll data integration for analytics |
| HR Business Partner (#106) | Division heads C/D/E/F — OKR alignment; Legal Officer (#75) — PIP legal review before formal initiation; CEO (#1) — senior-level calibration |
| L&D Coordinator (#107) | Division D SMEs (#19–#27) — subject-matter training delivery; Data Analyst (#44) — L&D ROI and completion metrics; HR Business Partner (#106) — training needs from performance reviews |
