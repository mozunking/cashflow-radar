"""Tests for ModelPool"""
import pandas as pd
import numpy as np
import pytest

from cad_model_pool.pool import ModelPool, GraphAnomalyDetector


class TestModelPool:
    def test_fit_and_predict(self):
        # Create sample features
        X = pd.DataFrame({
            "f1": np.random.randn(100),
            "f2": np.random.randn(100),
            "f3": np.random.randn(100),
        })

        pool = ModelPool(contamination=0.1)
        pool.fit(X)

        scores = pool.decision_function(X)
        assert "iforest" in scores
        assert "lof" in scores
        assert len(scores["iforest"]) == 100

    def test_not_fitted(self):
        pool = ModelPool()
        X = pd.DataFrame({"f1": [1, 2, 3]})

        with pytest.raises(RuntimeError):
            pool.decision_function(X)


class TestGraphAnomalyDetector:
    def test_build_graph(self):
        df = pd.DataFrame({
            "payer_id": ["A", "B", "C"],
            "payee_id": ["B", "C", "A"],
            "amount": [100, 200, 300]
        })

        detector = GraphAnomalyDetector()
        detector.build_graph(df)

        assert detector.G is not None
        assert detector.G.number_of_nodes() == 3
