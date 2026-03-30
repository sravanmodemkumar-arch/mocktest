---
name: EduForge Core Project Context
description: Platform name, scale target, cost target, institution types, compliance requirements, and architecture philosophy for EduForge
type: project
---

EduForge is a multi-tenant EdTech SaaS platform for India covering schools, colleges, coaching institutes, and competitive exam domains (SSC, RRB, UPSC, Banking, State Boards).

**Why:** Building from scratch to serve 5 crore (50 million) students at Rs. 0.60/student/year cost.
**How to apply:** Every design decision must be evaluated for scale (50M users, 74,000 peak concurrent exam submissions) and cost efficiency first.

## Scale & Cost Targets
- Students: 5 crore (50,000,000)
- Peak concurrent exam submissions: 74,000
- Cost target: Rs. 0.60/student/year
- DB cost reference: Rs. 4,500/month (db.t4g.medium) handles 5 lakh students

## Institution Types Supported (16 types)
Pre-Primary, Primary, Upper Primary, Secondary, Senior Secondary, K-12, Intermediate College, Degree College, Engineering College, Medical College, Management College, Law College, ITI, Polytechnic, Professional Coaching, Institution Group

## Indian Compliance Requirements (always in scope)
- GST: SAC 9993 education services; coaching = 18% GST; school/college = exempt
- DPDPA 2023: student PII stored in ap-south-1 (Mumbai) only; 72-hour Data Protection Board notice
- CERT-In: 6-hour breach reporting
- CBSE / UGC / AICTE / State Board regulations
- POCSO clearance for staff
- RTE §12 free-seat enforcement
- State Fee Regulatory Authority (FRA) ceiling checks
- 7-year audit trail retention for financial records

## Architecture Philosophy
- CDN-first: 99% of reads served from Cloudflare at Rs. 0
- No Redis: PostgreSQL handles OTP + rate limits; Memcached only if ORM cannot be optimised
- Only 2 PDFs ever generated: fee invoice + progress report card. Everything else = in-app view
- No file uploads from device storage: all content creation is in-app (camera capture is the only exception)
- IndexedDB for exam engine: 98% fewer Lambda calls during exam (2 Lambda calls total for 100-question exam)
- SQS for async between services (no Redis, no Celery broker)
- Every record tagged to tenant_id and academic_year_id

## Multi-Tenant Model
- Shopify model: each institution gets own subdomain (e.g., dps-delhi.eduforge.in), own branding, own modules enabled
- Custom domain (paid): portal.dpsedu.in
- Shard tiers: Small (<500 students, shared shard), Medium (500–50K, shared), Large (50K–3L, dedicated), Enterprise (3L+, multiple dedicated)
- No self-signup: all institution onboarding initiated by EduForge team only
