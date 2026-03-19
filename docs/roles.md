# EduForge — Roles & Permissions

Total: **87 distinct roles** across 6 groups.

---

## Group 1 — Platform Level (5 roles)

| Role | Access |
|---|---|
| Platform Owner | Full access to everything |
| Platform Admin | All tenants, billing, support |
| Platform Support | Read-only across tenants |
| Content Admin | MCQ bank, notes, videos |
| DevOps Admin | Infrastructure only |

---

## Group 2 — Institution Group Level (7 roles)

| Role | Scope |
|---|---|
| Group Chairman | All colleges/schools in group |
| Group CEO / Director | Operations across all branches |
| Group Academic Director | Curriculum, exams, results |
| Group Finance Director | Fees, billing, audits |
| Group IT Admin | All portals in group |
| Group HR Manager | Staff across branches |
| Group Audit Officer | Reports, MIS, compliance |

---

## Group 3 — School Roles (31 roles)

### Admin Staff (8 roles)

| Role | Key Permissions |
|---|---|
| School Owner / Chairman | Full school access |
| Principal | Academic + admin |
| Vice Principal | Academic oversight |
| Academic Director | Syllabus, exams |
| Exam Controller | Exams, results, ranks |
| Admission Coordinator | Enrolment, TC |
| Accountant / Finance | Fee collection, reports |
| Administrative Officer | General management |

### Teaching Staff (8 roles)

| Role | Key Permissions |
|---|---|
| HOD | Dept. teachers, syllabus |
| Senior Teacher | Classes, marks, attendance |
| Class Teacher | Attendance, behaviour, welfare |
| Subject Teacher | Lesson plans, marks |
| Lab Instructor | Practical schedules |
| Sports Coach | Physical, sports records |
| Librarian | Books, library records |
| Counsellor | Student welfare events |

### Support Staff (4 roles)

| Role | Key Permissions |
|---|---|
| Hostel Warden | Hosteler management |
| Hostel Matron | Daily welfare check |
| Transport Coordinator | Routes, vehicles |
| Security Staff | Gate entry logs |

### Student Types — School (9 roles)

| Type | Description |
|---|---|
| Day Scholar — Regular | Standard day student |
| Day Scholar — Scholarship | Fee concession tracking |
| Day Scholar — RTE | Right to Education quota |
| Hosteler — AC | Premium hostel |
| Hosteler — Non-AC | Standard hostel |
| Hosteler — Scholarship | Subsidised hostel |
| Special Needs | IEP tracking, welfare |
| NRI / Foreign National | Separate fee structure |
| TC Received | Transfer certificate in |

### Parent / Guardian Types — School (5 roles)

| Type | Access Level |
|---|---|
| Father | Full parent portal |
| Mother | Full parent portal |
| Guardian | Full parent portal |
| Emergency Contact | View only, notifications |
| Court-appointed Guardian | Restricted, POCSO-aware |

---

## Group 4 — College Roles (20 roles)

### Admin Staff (8 roles)

| Role |
|---|
| College Principal |
| Vice Principal |
| Dean of Academics |
| Examination Branch Head |
| Admission Officer |
| Student Affairs Officer |
| Placement Officer |
| Finance Officer |

### Faculty (6 roles)

| Role |
|---|
| Head of Department |
| Senior Lecturer |
| Lecturer |
| Guest Lecturer |
| Lab Instructor |
| NSS / NCC / Sports Coordinator |

### Student Types — College (6 roles)

| Type |
|---|
| Regular Student |
| Lateral Entry |
| Scholarship — Merit |
| Scholarship — Government |
| Hosteler |
| Fee Defaulter (restricted access) |

---

## Group 5 — Coaching Centre Roles (16 roles)

### Management (6 roles)

| Role |
|---|
| Institute Owner / Director |
| Branch Manager |
| Academic Coordinator |
| Sales / Admission Counsellor |
| Fee Collection Staff |
| Back Office / Data Entry |

### Faculty (4 roles)

| Role |
|---|
| Senior Faculty |
| Faculty |
| Demo / Guest Faculty |
| Online Faculty (recorded content) |

### Student Types — Coaching (6 roles)

| Type | Description |
|---|---|
| Regular Batch | Full-time classroom |
| Weekend Batch | Saturday/Sunday only |
| Online Batch | Live classes only |
| Correspondence | Material + tests only |
| Crash Course | Short duration |
| B2B (via institution tie-up) | Billed to institution |

---

## Group 6 — Online Mock Test Domain Roles (8 roles)

| Role | Description |
|---|---|
| Domain Admin | Manages one exam domain (SSC, RRB, etc.) |
| Content Creator | Writes and uploads MCQs |
| Question Reviewer | Reviews quality before publish |
| Question Approver | Final approval + publish |
| Student — Free | Limited tests/month |
| Student — Premium | Unlimited tests |
| Student — B2B | Via coaching institution subscription |
| Topper / Ranker | Special badge, leaderboard visibility |

---

## Permission Matrix

| Permission | Platform Admin | Group Director | Principal | HOD | Teacher | Student | Parent |
|---|---|---|---|---|---|---|---|
| View all tenants | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage institution | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage staff | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage students | ✅ | ✅ | ✅ | ❌ | partial | ❌ | ❌ |
| Take exam | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| View own child | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Upload notes | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Create MCQs | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| Approve MCQs | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ✅ | ✅ | partial | own only | own child |
| Manage billing | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Manage hostel | ✅ | ✅ | ✅ | ❌ | warden only | ❌ | ❌ |
| View results | ✅ | ✅ | ✅ | ✅ | own class | own only | own child |
