"""Tests for DegradationManager"""

import pytest
from cad_degradation.manager import DegradationManager


class TestDegradationManager:
    def test_initial_state(self):
        dm = DegradationManager()
        assert dm.level == "full"
        assert len(dm.degraded) == 0

    def test_single_failure_no_degrade(self):
        dm = DegradationManager(fail_threshold=3)
        dm.report_failure("iforest")
        dm.report_failure("iforest")

        assert "iforest" not in dm.degraded
        assert dm.level == "full"

    def test_threshold_reached_degrade(self):
        dm = DegradationManager(fail_threshold=3)
        dm.report_failure("iforest")
        dm.report_failure("iforest")
        dm.report_failure("iforest")  # 触发降级

        assert "iforest" in dm.degraded
        assert dm.level == "partial"

    def test_report_success_resets(self):
        dm = DegradationManager(fail_threshold=3)
        dm.report_failure("iforest")
        dm.report_failure("iforest")
        dm.report_failure("iforest")
        assert "iforest" in dm.degraded

        dm.report_success("iforest")
        assert "iforest" not in dm.degraded
        assert dm.level == "full"

    def test_multiple_models_degraded(self):
        dm = DegradationManager(fail_threshold=2)
        dm.report_failure("iforest")
        dm.report_failure("iforest")
        dm.report_failure("lof")
        dm.report_failure("lof")
        dm.report_failure("graph")
        dm.report_failure("graph")

        assert len(dm.degraded) == 3
        assert dm.level == "rules_only"

    def test_active_models(self):
        dm = DegradationManager(fail_threshold=2)
        dm.report_failure("iforest")
        dm.report_failure("iforest")

        active = dm.active_models()
        assert "lof" in active
        assert "graph" in active
        assert "iforest" not in active

    def test_is_available(self):
        dm = DegradationManager()
        assert dm.is_available() is True

        dm = DegradationManager(fail_threshold=1)
        dm.report_failure("iforest")
        dm.report_failure("lof")
        dm.report_failure("graph")
        assert dm.is_available() is False

    def test_get_state(self):
        dm = DegradationManager(fail_threshold=2)
        dm.report_failure("iforest")
        dm.report_failure("iforest")

        state = dm.get_state()
        assert state["level"] == "partial"
        assert "iforest" in state["degraded"]
        assert state["level_desc"] == "部分降级"
