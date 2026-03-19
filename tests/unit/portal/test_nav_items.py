"""Unit tests for home view nav item generation."""

import pytest

pytestmark = pytest.mark.unit


class TestGetNavItems:
    """Test _get_nav_items covers all portal groups and role branches."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from apps.home.views import _get_nav_items

        self.get_nav = _get_nav_items

    def test_platform_admin_group(self):
        items = self.get_nav(1, "platform_admin")
        labels = [i["label"] for i in items]
        assert "Home" in labels
        assert "Institutions" in labels
        assert "Audit Logs" in labels

    def test_chain_admin_group(self):
        items = self.get_nav(2, "chain_admin")
        labels = [i["label"] for i in items]
        assert "Branches" in labels
        assert "Fee Collection" in labels

    def test_school_principal(self):
        items = self.get_nav(3, "principal")
        labels = [i["label"] for i in items]
        assert "Students" in labels
        assert "Staff" in labels
        assert "Fees" in labels

    def test_school_teacher(self):
        items = self.get_nav(3, "teacher")
        labels = [i["label"] for i in items]
        assert "My Classes" in labels
        assert "Marks" in labels

    def test_school_parent(self):
        items = self.get_nav(3, "parent")
        labels = [i["label"] for i in items]
        assert "My Ward" in labels
        assert "Messages" in labels

    def test_school_student(self):
        items = self.get_nav(3, "student")
        labels = [i["label"] for i in items]
        assert "My Schedule" in labels
        assert "Results" in labels

    def test_college_group(self):
        items = self.get_nav(4, "student")
        labels = [i["label"] for i in items]
        assert "My Schedule" in labels

    def test_coaching_group(self):
        items = self.get_nav(5, "admin")
        labels = [i["label"] for i in items]
        assert "Students" in labels

    def test_exam_domain_group(self):
        items = self.get_nav(6, "student")
        labels = [i["label"] for i in items]
        assert "Test Series" in labels
        assert "AI Study Plan" in labels

    def test_tsp_group(self):
        items = self.get_nav(7, "admin")
        labels = [i["label"] for i in items]
        assert "Clients" in labels
        assert "API Keys" in labels

    def test_b2b_partner_group(self):
        items = self.get_nav(9, "partner")
        labels = [i["label"] for i in items]
        assert "Content" in labels
        assert "Payouts" in labels

    def test_student_unified_group(self):
        items = self.get_nav(10, "student")
        labels = [i["label"] for i in items]
        assert "My Institutions" in labels
        assert "Deadlines" in labels

    def test_unknown_group_fallback(self):
        items = self.get_nav(999, "student")
        labels = [i["label"] for i in items]
        assert "Home" in labels
        assert "Reports" in labels
        assert "Settings" in labels

    def test_all_items_have_required_keys(self):
        for group in [1, 2, 3, 4, 5, 6, 7, 9, 10]:
            items = self.get_nav(group, "student")
            for item in items:
                assert "label" in item
                assert "url" in item
                assert "icon" in item
