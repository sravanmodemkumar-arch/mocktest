# CDN Cache Policy — EduForge

## Route → Cache TTL Matrix

| Route | CDN TTL | Lambda runs | Cached by |
|---|---|---|---|
| `GET /tenant/config?domain=X` | 3600s (1hr) | Once per domain per hour | domain query param |
| `GET /page/home` | 30–300s | Once per (tenant+role) per TTL | X-Tenant-Slug + X-User-Role |
| `POST /auth/otp/send` | NO CACHE | Every request | — |
| `POST /auth/otp/verify` | NO CACHE | Every request | — |
| `POST /auth/token/refresh` | NO CACHE | Every request | — |
| `POST /auth/logout` | NO CACHE | Every request | — |
| `GET /auth/me` | NO CACHE | Every request | — |
| `GET /health` | 60s | Rarely | — |
| Static assets (`/_next/*`) | 31536000s (1yr) | Never (S3) | filename hash |

## Why CDN-first?

- **Tenant config**: A school's domain config never changes mid-day. Cache for 1hr.
  If 10,000 students open the app at 8AM → 1 Lambda call, CDN serves 9,999.

- **Home page**: Principal sees same KPI bar for 2 minutes. Cache for 120s.
  100 teachers refresh at 9AM → 1 Lambda call, CDN serves 99.

- **Auth**: OTP is unique per user per request. NEVER cache. Always hits Lambda.

## Lambda@Edge — Token → Role Extractor

Runs at CloudFront edge BEFORE checking cache for `/page/home`:
1. Extract JWT from Authorization header
2. Decode payload (no verify — just read role claim)
3. Set `X-User-Role: principal`, `X-Tenant-Slug: xyz-school`, `X-Portal-Group: 3`
4. Remove Authorization header (so CDN can cache without leaking tokens)
5. CloudFront caches the response keyed on X-User-Role + X-Tenant-Slug

This means: 50 principals at same school → 1 Lambda invocation, 49 served from CDN.
