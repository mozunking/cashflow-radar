"""Tests for FusionEngine"""

import pytest
from cad_fusion_engine.engine import FusionEngine, FusionOutput


class TestFusionEngine:
    def test_algo_score(self):
        engine = FusionEngine(phase="gray")
        scores = {"iforest": 80.0, "lof": 60.0, "graph": 40.0}
        score = engine.algo_score(scores)
        # 0.45*80 + 0.30*60 + 0.25*40 = 36 + 18 + 10 = 64
        assert abs(score - 64.0) < 0.1

    def test_fuse_gray_phase_no_rule_hit(self):
        engine = FusionEngine(phase="gray")
        scores = {"iforest": 80.0, "lof": 60.0, "graph": 40.0}
        result = engine.fuse(False, 0, scores, "TXN001")

        assert result.algo_score == 64.0
        assert result.final_score == 64.0
        assert result.risk_level == "中风险"
        assert result.phase == "gray"

    def test_fuse_rule_hit(self):
        engine = FusionEngine(phase="validation")
        scores = {"iforest": 80.0, "lof": 60.0, "graph": 40.0}
        result = engine.fuse(True, 90.0, scores, "TXN002")

        # 规则一票否决：取max(90, 90*0.7 + 64*0.3) = max(90, 63+19.2) = 90
        assert result.final_score == 90.0
        assert result.rule_hit is True
        assert result.risk_level == "高风险"

    def test_fuse_high_risk(self):
        engine = FusionEngine(phase="stable")
        scores = {"iforest": 95.0, "lof": 90.0, "graph": 85.0}
        result = engine.fuse(False, 0, scores, "TXN003")

        assert result.risk_level == "高风险"
        assert result.final_score >= 80

    def test_custom_weights(self):
        engine = FusionEngine(phase="gray", custom_algo_w={"iforest": 1.0})
        scores = {"iforest": 100.0}
        score = engine.algo_score(scores)
        assert score == 100.0

    def test_invalid_phase(self):
        with pytest.raises(ValueError):
            FusionEngine(phase="invalid")
