---
name: EduForge Tech Stack
description: Full technology stack, services, ports, database schema design, storage strategy, and CDN architecture for EduForge
type: project
---

All tools are free/open source except AWS and Cloudflare pay-per-use.

**Why:** Cost target of Rs. 0.60/student/year forces every infrastructure choice.
**How to apply:** Never suggest paid alternatives when free options exist. Always check cost implication.

## Services & Ports
| Service | Port | Runtime | Responsibility |
|---|---|---|---|
| identity | 8001 | AWS Lambda + FastAPI + Mangum | Auth, JWT, OTP, Users, Institutions |
| portal | 8002 | ECS Fargate + Django 4.2 + HTMX 1.9 | Staff + student portals, Attendance, Fees |
| exam | 8003 | AWS Lambda + FastAPI | Mock tests, MCQ engine, submissions, ranks |
| notification | 8004 | AWS Lambda + FastAPI | WhatsApp (MSG91), SMS, Email (AWS SES), FCM push |
| billing | 8005 | AWS Lambda + FastAPI | Subscriptions, Razorpay, GST, refunds |
| ai | 8006 | AWS Lambda + FastAPI | MCQ generation, doubt solving, study plans |
| analytics | 8007 | AWS Lambda + FastAPI | Reports, MIS, dashboards |

## Core Stack
- Language: Python 3.12 + uv (package manager)
- API: FastAPI 0.111 + Mangum (Lambda adapter)
- Portal: Django 4.2 + HTMX 1.9 + Tailwind CDN
- Mobile: Flutter 3.x + Riverpod
- ORM: SQLAlchemy 2.0 + Alembic (migrations)
- DB: PostgreSQL 16 + asyncpg + PgBouncer (connection pooling)
- Queue: AWS SQS (no Redis, no Celery broker)
- Storage: Cloudflare R2 (free 10GB, zero egress cost)
- CDN: Cloudflare (free tier)
- Auth: JWT HS256 (python-jose) + passlib/bcrypt (cost 12)
- PDF: WeasyPrint (ONLY for fee invoice + progress report card)
- Validation: Pydantic 2.7
- HTTP client: httpx 0.27
- Linting/formatting: ruff; type check: mypy; testing: pytest + pytest-asyncio
- CI/CD: GitHub Actions (free 2000 min/month)
- Container: Docker + Docker Compose

## Database Design: Schema-per-Service
One PostgreSQL 16 cluster, 7 schemas (identity, portal, exam, notification, billing, ai, analytics).
Each service owns its schema. Cross-schema JOINs possible via views. Row-level security for isolation.

## Storage Strategy
- PostgreSQL DB: user activity only (attendance, fees, marks, sessions, credentials)
- Cloudflare R2 → CDN: all content (notes, MCQs, timetables, results, announcements, branding)
- IndexedDB (device): user/personal photos, offline exam questions, offline content
- PDF: ONLY fee invoice + progress report card

## CDN Page Loading Pattern (Option C)
Every page = 1 CDN call (shared content JSON/HTML) + 1 API call (personal live data).
- Flutter reads CDN JSON directly
- HTMX fetches CDN HTML partial directly (zero Django compute at read time)
- Celery pre-renders HTML from same JSON data, stores on R2/CDN
- Personal data: single FastAPI endpoint returns JSON (Flutter) or HTML fragment (HTMX) based on Accept header

## Key Architecture Decisions
- Cloudflare R2 over AWS S3: zero egress cost (saves Rs. 56+ lakh/year at 1L users)
- No Redis: saves Rs. 16,800/year; PostgreSQL OTPs table replaces Redis for OTP storage
- Stateless JWT: no network call to validate — 1 Lambda call saved per request
- ECS Fargate only for portal (HTMX needs always-on container); everything else is Lambda
- SQS for async: batch 100 writes into 1 DB call, reduces DB load at peak

## UI Conventions (portal)
- Dark theme: bg-base #040810, surface-1 #08101E, accent #6366F1
- All datetime: IST (UTC+5:30), displayed as "DD MMM YYYY HH:MM IST"
- Drawers: right-anchored
- Sensitive values: absent from DOM entirely (not CSS-hidden)
- Confirmation for destructive actions: type "DELETE" / "END" / confirm modal
