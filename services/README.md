# EduForge Microservices

## Architecture

```
Browser/App
    │
    ▼
CloudFront CDN (edge cache)
    │
    ├── /tenant/config  ──────────────────► Tenant Service (Lambda)
    │   TTL: 1hr                             128MB, 5s timeout
    │   Cached by: domain param              Runs: ~once/hr per domain
    │
    ├── /page/home  ───────────────────────► Home Service (Lambda)
    │   TTL: 30–300s                         512MB, 10s timeout
    │   Cached by: X-Tenant-Slug+X-Role      Runs: once per TTL per role
    │
    └── /auth/*  ──────────────────────────► Auth Service (Lambda)
        NO CACHE                             256MB, 10s timeout
        Runs: every request                  OTP, JWT, sessions
```

## Services

| Service | Path | Cache | Purpose |
|---|---|---|---|
| `auth/` | `/auth/*` | None | OTP send/verify, JWT tokens |
| `home/` | `/page/home` | 30–300s | Aggregated home page data |
| `tenant/` | `/tenant/config` | 1hr | Domain → portal config |

## One Call Per Page Rule

Each page makes exactly ONE API call:

| Page | Call |
|---|---|
| App init (before login) | `GET /tenant/config?domain={hostname}` |
| Home page | `GET /page/home` |
| Login step 1 | `POST /auth/otp/send` |
| Login step 2 | `POST /auth/otp/verify` |

## Local Development

```bash
# Run all services
cd services/auth && uvicorn main:app --port 8001 --reload
cd services/home && uvicorn main:app --port 8002 --reload
cd services/tenant && uvicorn main:app --port 8003 --reload
```

## Deploy

```bash
npm install -g serverless
serverless deploy --stage production --region ap-south-1
```
