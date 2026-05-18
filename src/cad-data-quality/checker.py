"""Data Quality Checker for CAD

校验中台输入数据质量，不通过则阻断下游并告警。
基于Pandas实现，校验逻辑配置化。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import pandas as pd


@dataclass
class DataQualityResult:
    passed: bool
    results: list[dict[str, Any]]
    action: str  # "proceed" or "block_and_alert"

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "results": self.results,
            "action": self.action
        }


class DataQualityChecker:
    """数据质量校验器"""

    def __init__(self, baseline_stats: dict | None = None):
        self.baseline = baseline_stats or {}
        self.results: list[dict[str, Any]] = []

    def check_completeness(
        self, df: pd.DataFrame, required: list[str], threshold: float = 0.05
    ) -> bool:
        """检查必填字段空值率"""
        ok = True
        for col in required:
            if col not in df.columns:
                self.results.append({
                    "cat": "completeness",
                    "field": col,
                    "rate": 1.0,
                    "ok": False,
                    "msg": "字段不存在"
                })
                ok = False
                continue
            rate = df[col].isnull().sum() / len(df)
            if rate > threshold:
                ok = False
                self.results.append({
                    "cat": "completeness",
                    "field": col,
                    "rate": round(rate, 4),
                    "ok": False
                })
        return ok

    def check_timeliness(
        self, df: pd.DataFrame, date_col: str = "transaction_date"
    ) -> bool:
        """检查数据批次日期是否为最新T+1"""
        if date_col not in df.columns:
            return True
        max_dt = pd.to_datetime(df[date_col]).max()
        expected = pd.Timestamp(datetime.now().date() - timedelta(days=1))
        ok = max_dt >= expected
        if not ok:
            self.results.append({
                "cat": "timeliness",
                "max": str(max_dt),
                "expected": str(expected),
                "ok": False
            })
        return ok

    def check_record_count(self, df: pd.DataFrame) -> bool:
        """检查记录数波动"""
        avg = self.baseline.get("avg_record_count")
        if avg is None:
            return True
        dev = abs(len(df) - avg) / avg
        ok = dev <= 0.3
        if not ok:
            self.results.append({
                "cat": "record_count",
                "count": len(df),
                "avg": avg,
                "deviation": round(dev, 4),
                "ok": False
            })
        return ok

    def check_consistency(self, df: pd.DataFrame) -> bool:
        """检查金额字段符号一致性"""
        ok = True
        if "balance" in df.columns:
            neg_balance = (df["balance"] < 0).sum()
            if neg_balance > 0:
                self.results.append({
                    "cat": "consistency",
                    "field": "balance",
                    "negative_count": int(neg_balance),
                    "ok": False
                })
                ok = False
        if "amount" in df.columns:
            invalid_amt = (df["amount"] <= 0).sum()
            if invalid_amt > 0:
                self.results.append({
                    "cat": "consistency",
                    "field": "amount",
                    "invalid_count": int(invalid_amt),
                    "ok": False
                })
                ok = False
        return ok

    def check_distribution(self, df: pd.DataFrame, key_fields: list[str]) -> bool:
        """检查关键字段分布漂移"""
        ok = True
        for col in key_fields:
            if col not in df.columns:
                continue
            hist_mean = self.baseline.get(f"{col}_mean")
            hist_std = self.baseline.get(f"{col}_std")
            if hist_mean is None or hist_std is None:
                continue
            current_mean = df[col].mean()
            drift = abs(current_mean - hist_mean) / max(hist_std, 1e-6)
            if drift > 2:
                self.results.append({
                    "cat": "distribution",
                    "field": col,
                    "drift_sigma": round(drift, 2),
                    "ok": False
                })
                ok = False
        return ok

    def run_all(
        self, df: pd.DataFrame, required: list[str], key_fields: list[str] | None = None
    ) -> DataQualityResult:
        """执行全部校验"""
        self.results = []
        c1 = self.check_completeness(df, required)
        c2 = self.check_timeliness(df)
        c3 = self.check_record_count(df)
        c4 = self.check_consistency(df)
        key_fields = key_fields or []
        c5 = self.check_distribution(df, key_fields)

        overall = c1 and c2 and c3 and c4 and c5
        action = "proceed" if overall else "block_and_alert"

        return DataQualityResult(
            passed=overall,
            results=self.results,
            action=action
        )
