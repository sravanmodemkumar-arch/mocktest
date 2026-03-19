# EduForge — EdTech SaaS Platform

Multi-tenant educational software platform for schools, colleges, coaching institutes, and competitive exam preparation (SSC, RRB, State Boards).

## Platform Overview

| Property | Value |
|---|---|
| **Type** | Multi-tenant SaaS |
| **Portals** | School · College · Coaching · SSC · RRB · State Boards |
| **Users** | Students · Parents · Faculty · Admins |
| **Key Features** | Unlimited Mock Tests · MCQ Engine · Notes · Video Learning |
| **Backend** | FastAPI · Django + HTMX · Python 3.12 |
| **Database** | PostgreSQL 16 (schema-per-service) |
| **Mobile** | Flutter (Android + iOS) |
| **Infrastructure** | AWS Lambda · ECS Fargate · Cloudflare R2 + CDN |

## Services

```
eduforge/
├── identity/       # Auth service — FastAPI (JWT + OTP login)
├── portal/         # Staff portals — Django + HTMX  [next branch]
├── exam/           # Exam engine — FastAPI + IndexedDB [next branch]
├── scripts/        # DB init scripts
└── docker-compose.yml
```

## Features

- **Authentication** — OTP-based login via WhatsApp (no passwords)
- **Mock Tests** — Unlimited tests with real-time results and All India Rank
- **MCQ Engine** — Auto-generate questions by subject, topic, difficulty
- **Notes** — Faculty uploads structured notes (text, PDF) by subject → topic
- **Video Learning** — YouTube videos mapped to subjects and exam categories
- **Multi-domain** — Each exam board (SSC, RRB, State Board) on its own domain
- **Analytics** — Performance dashboard for students and admins

## Getting Started

### Prerequisites

- Python 3.12
- Docker + Docker Compose
- PostgreSQL 16 (via Docker)

### Setup

```bash
# 1. Clone and enter project
git clone https://github.com/sravanmodemkumar-arch/mocktest.git
cd mocktest

# 2. Copy env file
cp .env.example .env
# Edit .env with your values

# 3. Start database
docker-compose up db -d

# 4. Run identity service
cd identity
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### API Docs

Once running, visit: `http://localhost:8001/docs`

**Auth endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/otp/send` | Send OTP to mobile |
| POST | `/api/v1/auth/otp/verify` | Verify OTP → get JWT tokens |
| POST | `/api/v1/auth/token/refresh` | Refresh access token |

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready code |
| `feature/project-setup-auth` | Project setup + authentication ← current |
| `feature/portal-pages` | Staff portal pages (next) |
| `feature/exam-engine` | Mock test + MCQ engine (upcoming) |
| `feature/notes-videos` | Notes and YouTube integration (upcoming) |

## CI/CD

- **CI** — runs on every push (lint, test, Python 3.11 + 3.12)
- **Deploy** — auto-deploys to production on merge to `main`

## Tech Stack

| Layer | Technology |
|---|---|
| Auth API | FastAPI 0.111 + Python 3.12 |
| Staff Portals | Django 4.2 + HTMX 1.9 |
| Mobile | Flutter + Riverpod |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic |
| Queue | AWS SQS |
| Storage | Cloudflare R2 (zero egress cost) |
| CDN | Cloudflare |
| Auth | JWT (HS256) + OTP via WhatsApp |

## License

MIT

