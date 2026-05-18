"""Tests for FeatureFactory"""

import pandas as pd
import pytest
from datetime import datetime

from cad_feature_engine.factory import FeatureFactory, FeatureOutput


class TestFeatureFactory:
    def test_compute_basic(self):
        df = pd.DataFrame(
            {
                "transaction_id": ["TXN001"],
                "account_id": ["ACC001"],
                "amount": [10000.0],
                "balance": [100000.0],
            }
        )
        factory = FeatureFactory()
        result = factory.compute(df)

        assert isinstance(result, FeatureOutput)
        assert result.transaction_id == "TXN001"
        assert result.account_id == "ACC001"
        assert len(result.features) > 0
        assert result.feature_version == "1.0.0"

    def test_compute_empty(self):
        df = pd.DataFrame()
        factory = FeatureFactory()
        result = factory.compute(df)

        assert result.quality_passed is False
        assert result.features == {}

    def test_amount_features_exist(self):
        df = pd.DataFrame(
            {
                "transaction_id": ["TXN001"],
                "account_id": ["ACC001"],
                "amount": [50000.0],
            }
        )
        factory = FeatureFactory()
        result = factory.compute(df)

        expected = [
            "amt_deviation",
            "amt_threshold_proximity",
            "amt_daily_total",
            "amt_volatility",
        ]
        for feat in expected:
            assert feat in result.features
