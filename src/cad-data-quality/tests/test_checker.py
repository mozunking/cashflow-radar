"""Tests for DataQualityChecker"""
import pandas as pd
import pytest
from datetime import datetime, timedelta

from cad_data_quality.checker import DataQualityChecker, DataQualityResult


class TestDataQualityChecker:
    def test_check_completeness_pass(self):
        df = pd.DataFrame({"txn_id": [1, 2, 3], "amount": [100, 200, 300]})
        checker = DataQualityChecker()
        result = checker.check_completeness(df, ["txn_id", "amount"])
        assert result is True

    def test_check_completeness_fail(self):
        df = pd.DataFrame({"txn_id": [1, 2, 3], "amount": [None, 200, None]})
        checker = DataQualityChecker()
        result = checker.check_completeness(df, ["txn_id", "amount"], threshold=0.1)
        assert result is False

    def test_check_timeliness_pass(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        df = pd.DataFrame({"transaction_date": [yesterday] * 3})
        checker = DataQualityChecker()
        result = checker.check_timeliness(df)
        assert result is True

    def test_check_record_count_pass(self):
        df = pd.DataFrame({"txn_id": range(100)})
        checker = DataQualityChecker({"avg_record_count": 100})
        result = checker.check_record_count(df)
        assert result is True

    def test_run_all_pass(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        df = pd.DataFrame({
            "transaction_date": [yesterday] * 100,
            "txn_id": range(100),
            "amount": [100.0] * 100,
            "balance": [1000.0] * 100,
        })
        checker = DataQualityChecker({"avg_record_count": 100})
        result = checker.run_all(df, ["txn_id", "amount"], ["amount"])
        assert result.passed is True
        assert result.action == "proceed"

    def test_run_all_fail(self):
        df = pd.DataFrame({
            "txn_id": range(100),
            "amount": [None] * 50 + [100.0] * 50,
        })
        checker = DataQualityChecker()
        result = checker.run_all(df, ["txn_id", "amount"])
        assert result.passed is False
        assert result.action == "block_and_alert"
