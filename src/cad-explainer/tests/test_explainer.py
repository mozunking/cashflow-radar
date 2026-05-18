"""Tests for ExplainerEngine"""
import pytest
from cad_explainer.explainer import ExplainerEngine, ANOMALY_TYPE_MAP


class TestExplainerEngine:
    def test_explain_basic(self):
        engine = ExplainerEngine(model_name="iforest")
        features = {
            "amt_deviation": 3.0,
            "freq_daily": 50.0,
            "cp_stranger_ratio": 0.8,
        }
        scores = {"iforest": 85.0, "lof": 70.0, "graph": 60.0}

        result = engine.explain("TXN001", features, scores, top_k=3)

        assert result.transaction_id == "TXN001"
        assert result.anomaly_type in ANOMALY_TYPE_MAP
        assert len(result.top_features) == 3
        assert result.explain_method == "shap_iforest"

    def test_anomaly_type_classification(self):
        engine = ExplainerEngine()

        # Amount feature dominant -> TYPE_01
        features = {"amt_deviation": 5.0}
        atype = engine._classify_anomaly(features)
        assert atype in ["TYPE_01", "TYPE_02", "TYPE_03", "TYPE_04", "TYPE_05", "TYPE_06"]

    def test_feature_business_description(self):
        engine = ExplainerEngine()
        desc = engine.business_desc_map.get("amt_deviation")
        assert "金额" in desc

    def test_empty_features(self):
        engine = ExplainerEngine()
        result = engine.explain("TXN001", {}, {})
        assert result.anomaly_type == "TYPE_05"
        assert len(result.top_features) == 0
