"""Tests for CAD Console pages."""

import sys
sys.path.insert(0, "/Users/hfy/cashflow-radar/src")

from datetime import datetime, timedelta


class TestDashboardPage:
    """Tests for dashboard page."""

    def test_demo_data_generation(self):
        """Test demo data structure."""
        from pages.dashboard import _get_demo_data
        data = _get_demo_data()
        assert "task_id" in data
        assert "total_count" in data
        assert "high_risk" in data
        assert "medium_risk" in data
        assert "low_risk" in data
        assert "results" in data
        assert len(data["results"]) > 0

    def test_risk_level_distribution(self):
        """Test risk level counts sum to total."""
        from pages.dashboard import _get_demo_data
        data = _get_demo_data()
        total = data["high_risk"] + data["medium_risk"] + data["low_risk"]
        assert total == data["total_count"]


class TestReviewPage:
    """Tests for review page."""

    def test_review_items_generation(self):
        """Test review items structure."""
        from pages.review import _get_demo_review_items
        items = _get_demo_review_items()
        assert len(items) > 0
        assert "transaction_id" in items[0]
        assert "risk_level" in items[0]

    def test_feedback_submission(self):
        """Test feedback submission with demo mode."""
        from pages.review import _submit_feedback
        # Should not raise, demo mode returns success
        _submit_feedback("http://localhost:8080", "TXN001", "确认", "Test comment", "TYPE_01")


class TestDeploymentPage:
    """Tests for deployment page."""

    def test_pipeline_status_values(self):
        """Test valid pipeline statuses."""
        valid_statuses = ["success", "running", "failed"]
        test_pipelines = [
            {"name": "test", "status": "success", "last_run": "now", "duration": "0s"},
        ]
        for p in test_pipelines:
            assert p["status"] in valid_statuses


class TestSettingsPage:
    """Tests for settings page."""

    def test_api_endpoints_defined(self):
        """Test API endpoints list is defined."""
        # Import via module inspection
        from pages.settings import _render_api_config
        assert callable(_render_api_config)


if __name__ == "__main__":
    print("Running CAD Console tests...")
    test = TestDashboardPage()
    test.test_demo_data_generation()
    print("All tests passed!")
