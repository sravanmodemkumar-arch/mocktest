# Tenant Static Assets

Each tenant gets a folder: `static/tenants/{tenant-slug}/`

## Folder Structure

```
static/
  tenants/
    _template/              ← Copy this when onboarding a new tenant
      logo.svg              ← Main logo (SVG preferred, fallback PNG)
      logo-dark.svg         ← Dark mode variant
      favicon.ico           ← Browser tab icon
      favicon-192.png       ← PWA icon
      favicon-512.png       ← PWA splash icon
      brand.json            ← Colors, fonts, portal name
      og-image.png          ← Open Graph image (1200×630) for link previews

    default/                ← EduForge platform default assets
      logo.svg
      logo-dark.svg
      favicon.ico
      brand.json

    xyz-school/             ← Example: XYZ School, Hyderabad
      logo.svg
      favicon.ico
      brand.json

    abc-coaching/           ← Example: ABC JEE Coaching
      logo.svg
      favicon.ico
      brand.json
```

## brand.json Schema

```json
{
  "name": "XYZ School",
  "tagline": "Excellence in Education",
  "portal_group": 3,
  "colors": {
    "primary":     "#1A237E",
    "primary_dark": "#0D1B6E",
    "accent":      "#FF6F00",
    "background":  "#FFFFFF",
    "surface":     "#F5F7FA",
    "text":        "#1A1A2E",
    "text_muted":  "#6B7280"
  },
  "font": {
    "family": "Inter",
    "heading_weight": 700,
    "body_weight": 400
  },
  "logo": {
    "light": "/static/tenants/xyz-school/logo.svg",
    "dark":  "/static/tenants/xyz-school/logo-dark.svg",
    "width": 140,
    "height": 40
  },
  "favicon": "/static/tenants/xyz-school/favicon.ico",
  "og_image": "/static/tenants/xyz-school/og-image.png",
  "contact": {
    "support_email": "support@xyzschool.com",
    "support_phone": "+91-XXXXXXXXXX"
  }
}
```

## CDN Serving

Static assets are served from S3 via CloudFront:

| Path | CDN TTL | Notes |
|---|---|---|
| `logo.svg` | 30 days | Invalidate on logo change |
| `favicon.ico` | 7 days | Rarely changes |
| `brand.json` | 1 hour | Colors can change; CDN invalidated on update |
| `og-image.png` | 7 days | For social sharing |

## How Tenant Config Includes Assets

The `/api/v1/tenant/config` response includes asset URLs:
```json
{
  "slug": "xyz-school",
  "branding": {
    "primary": "#1A237E",
    "logo": "https://cdn.eduforge.in/static/tenants/xyz-school/logo.svg",
    "logo_dark": "https://cdn.eduforge.in/static/tenants/xyz-school/logo-dark.svg",
    "favicon": "https://cdn.eduforge.in/static/tenants/xyz-school/favicon.ico"
  }
}
```

Frontend + Mobile apps use these URLs directly — no hardcoded assets.

## Onboarding a New Tenant

1. Copy `_template/` → `{tenant-slug}/`
2. Replace logo, favicon, og-image with tenant's brand assets
3. Update `brand.json` with correct colors and name
4. Upload to S3: `aws s3 sync static/tenants/{slug}/ s3://eduforge-static/tenants/{slug}/`
5. Invalidate CDN: `aws cloudfront create-invalidation --paths "/static/tenants/{slug}/*"`
6. Update tenant record in DB: `tenants.branding` JSON with CDN URLs
