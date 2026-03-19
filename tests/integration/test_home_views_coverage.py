"""
Integration tests — home views coverage.
Covers nav_links, _get_nav_items, profile_menu, notifications,
and home_data edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


class TestNavLinks:
    """Test nav link generation for different portal groups and roles."""

    def _get_nav(self, client, token, portal_group, role="student"):
        user_data = {"id": 1, "role": role, "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            client.cookies["ef_token"] = token
            request = client.get("/home/nav/")
        return request

    def test_nav_links_platform_admin(self, client, make_access_token):
        token = make_access_token(user_id=1, role="platform_admin")
        client.cookies["ef_token"] = token
        user_data = {"id": 1, "role": "platform_admin", "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.get("/home/nav/")
        assert resp.status_code == 200

    def test_nav_links_chain_admin(self, client, make_access_token):
        token = make_access_token(user_id=1, role="chain_admin")
        client.cookies["ef_token"] = token
        user_data = {"id": 1, "role": "chain_admin", "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = client.get("/home/nav/")
        assert resp.status_code == 200

    def test_nav_links_student(self, authed_portal_client):
        user_data = {"id": 1, "role": "student", "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = authed_portal_client.get("/home/nav/")
        assert resp.status_code == 200


class TestProfileMenu:
    def test_profile_menu_renders(self, authed_portal_client):
        user_data = {"id": 1, "role": "student", "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = authed_portal_client.get("/home/profile-menu/")
        assert resp.status_code == 200


class TestNotifications:
    def test_notifications_renders(self, authed_portal_client):
        user_data = {"id": 1, "role": "student", "is_active": True}
        with patch("apps.core.middleware.httpx.get") as mock_mw:
            mock_mw.return_value = MagicMock(status_code=200, json=lambda: user_data)
            resp = authed_portal_client.get("/home/notifications/")
        assert resp.status_code == 200


class TestHomeDataEdgeCases:
    def test_home_data_service_down(self, authed_portal_client):
        import httpx as _httpx

        user_data = {"id": 1, "role": "student", "is_active": True}
        auth_resp = MagicMock(status_code=200, json=lambda: user_data)

        def _selective_get(url, **kwargs):
            if "/auth/me" in url:
                return auth_resp
            raise _httpx.ConnectError("down")

        with patch("httpx.get", side_effect=_selective_get):
            resp = authed_portal_client.get("/home/data/")
        assert resp.status_code == 200
