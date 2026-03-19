"""
Unit tests — Tenant service: first-party domain resolution,
static asset loading, cache header generation.
"""
import pytest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "services"))

pytestmark = pytest.mark.unit


class TestFirstPartyDomains:
    @pytest.mark.parametrize(
        "domain,expected_group,expected_slug",
        [
            ("admin.eduforge.in", 1, "platform-admin"),
            ("app.eduforge.in", 2, "chain-admin"),
            ("ssc.eduforge.in", 6, "ssc-domain"),
            ("rrb.eduforge.in", 6, "rrb-domain"),
            ("upsc.eduforge.in", 6, "upsc-domain"),
            ("banking.eduforge.in", 6, "banking-domain"),
            ("ap.eduforge.in", 6, "ap-board"),
            ("ts.eduforge.in", 6, "ts-board"),
            ("partners.eduforge.in", 9, "partner-portal"),
            ("student.eduforge.in", 10, "student-unified"),
            ("parent.eduforge.in", 8, "parent-portal"),
            ("localhost", 1, "default"),
            ("127.0.0.1", 1, "default"),
        ],
    )
    def test_first_party_domain_resolves(self, domain, expected_group, expected_slug):
        from tenant.main import FIRST_PARTY_DOMAINS
        assert domain in FIRST_PARTY_DOMAINS
        cfg = FIRST_PARTY_DOMAINS[domain]
        assert cfg["group"] == expected_group
        assert cfg["slug"] == expected_slug

    def test_all_first_party_domains_have_name(self):
        from tenant.main import FIRST_PARTY_DOMAINS
        for domain, cfg in FIRST_PARTY_DOMAINS.items():
            assert "name" in cfg, f"{domain} missing 'name'"
            assert len(cfg["name"]) > 0

    def test_all_first_party_domains_have_slug(self):
        from tenant.main import FIRST_PARTY_DOMAINS
        for domain, cfg in FIRST_PARTY_DOMAINS.items():
            assert "slug" in cfg
            # slug must be lowercase, no spaces
            assert cfg["slug"] == cfg["slug"].lower()
            assert " " not in cfg["slug"]


class TestStaticAssets:
    def test_static_assets_returns_dict(self):
        from tenant.main import static_assets
        result = static_assets("default")
        assert isinstance(result, dict)

    def test_static_assets_has_required_keys(self):
        from tenant.main import static_assets
        result = static_assets("default")
        required = ["primary", "logo", "logo_dark", "favicon", "og_image"]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_static_assets_logo_is_cdn_url(self):
        from tenant.main import static_assets
        result = static_assets("some-school")
        assert "some-school" in result["logo"]

    def test_static_assets_fallback_to_default(self):
        """Non-existent tenant slug uses default brand.json."""
        from tenant.main import static_assets
        result = static_assets("nonexistent-tenant-xyz")
        assert result["primary"]  # has some color
        assert result["logo"]

    def test_static_assets_reads_brand_json(self, tmp_path):
        """If brand.json exists for tenant, its values are used."""
        from tenant import main as tenant_module

        slug = "test-brand-tenant"
        tenant_dir = tmp_path / slug
        tenant_dir.mkdir()
        brand = {
            "colors": {
                "primary": "#FF0000",
                "primary_dark": "#CC0000",
                "accent": "#00FF00",
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "text": "#000000",
                "text_muted": "#666666",
                "success": "#00CC00",
                "warning": "#FFAA00",
                "error": "#CC0000",
            },
            "font": {"family": "Roboto"},
        }
        (tenant_dir / "brand.json").write_text(json.dumps(brand))

        # Temporarily patch STATIC_DIR
        original = tenant_module.STATIC_DIR
        tenant_module.STATIC_DIR = str(tmp_path)
        try:
            result = tenant_module.static_assets(slug)
            assert result["primary"] == "#FF0000"
            assert result["font_family"] == "Roboto"
        finally:
            tenant_module.STATIC_DIR = original


class TestTenantCacheHeaders:
    @pytest.mark.asyncio
    async def test_first_party_domain_returns_200(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/tenant/config", params={"domain": "ssc.eduforge.in"}
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "ssc-domain"
        assert data["portal_group"] == 6

    @pytest.mark.asyncio
    async def test_first_party_web_has_cdn_cache_headers(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/tenant/config", params={"domain": "ssc.eduforge.in"}
            )

        cc = resp.headers.get("Cache-Control", "")
        assert "s-maxage=3600" in cc
        assert "public" in cc

    @pytest.mark.asyncio
    async def test_first_party_mobile_has_private_cache(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/tenant/config",
                params={"domain": "ssc.eduforge.in"},
                headers={"X-Client-Type": "mobile_ios"},
            )

        cc = resp.headers.get("Cache-Control", "")
        assert "private" in cc
        assert "max-age=86400" in cc

    @pytest.mark.asyncio
    async def test_unknown_domain_returns_404(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/tenant/config",
                params={"domain": "unknown-domain-xyz.com"},
            )

        assert resp.status_code in (404, 503)  # 503 if no DB configured

    @pytest.mark.asyncio
    async def test_response_includes_branding(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get(
                "/api/v1/tenant/config", params={"domain": "localhost"}
            )

        data = resp.json()
        assert "branding" in data
        assert "primary" in data["branding"]
        assert "logo" in data["branding"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        from tenant.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")

        assert resp.status_code == 200
        assert resp.json()["service"] == "tenant"
