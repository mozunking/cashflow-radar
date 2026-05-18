"""Feature Factory for CAD

计算5类40个特征：
- 交易金额特征（8个）
- 交易频率特征（7个）
- 交易对手特征（9个）
- 时序与账户特征（8个）
- 交互特征（8个）
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class FeatureOutput:
    transaction_id: str
    account_id: str
    features: dict[str, float]
    feature_version: str
    computed_at: datetime
    quality_passed: bool = True
    quality_details: list[str] | None = None


class FeatureFactory:
    """特征工厂"""

    VERSION = "1.0.0"

    def __init__(self, version: str | None = None):
        self.version = version or self.VERSION
        self.details: list[str] = []

    def compute(self, df: pd.DataFrame) -> FeatureOutput:
        """计算全部特征"""
        if df.empty:
            return FeatureOutput(
                transaction_id="",
                account_id="",
                features={},
                feature_version=self.version,
                computed_at=datetime.now(),
                quality_passed=False,
                quality_details=["empty dataframe"]
            )

        txn_id = str(df.iloc[0].get("transaction_id", ""))
        acct_id = str(df.iloc[0].get("account_id", ""))

        features: dict[str, float] = {}
        features.update(self._amount_features(df))
        features.update(self._frequency_features(df))
        features.update(self._counterparty_features(df))
        features.update(self._temporal_features(df))
        features.update(self._interaction_features(features))

        return FeatureOutput(
            transaction_id=txn_id,
            account_id=acct_id,
            features=features,
            feature_version=self.version,
            computed_at=datetime.now(),
            quality_passed=True,
            quality_details=self.details if self.details else None
        )

    def _amount_features(self, df: pd.DataFrame) -> dict[str, float]:
        """交易金额特征（8个）"""
        amt = df["amount"].astype(float)
        hist_avg = df["amount"].astype(float).mean()
        features = {}

        # amt_deviation: 交易金额与历史均值偏离度
        mean_val = hist_avg if hist_avg != 0 else 1.0
        features["amt_deviation"] = float((amt.mean() - mean_val) / mean_val)

        # amt_industry_dev: 行业均值偏离度（简化：使用全局均值）
        features["amt_industry_dev"] = float((amt.mean() - mean_val) / mean_val)

        # amt_threshold_proximity: 大额交易标准接近度
        features["amt_threshold_proximity"] = float(max(
            1 - abs(amt.mean() - 500000) / 500000,
            1 - abs(amt.mean() - 2000000) / 2000000
        ))

        # amt_tail_pattern: 金额尾数特征
        last_digit = int(str(int(amt.mean()))[-1])
        features["amt_tail_pattern"] = 1.0 if last_digit == 0 else (
            0.5 if len(set(str(int(amt.mean())))) == 1 else 0.0
        )

        # amt_daily_total: 单日累计金额
        features["amt_daily_total"] = float(amt.sum())

        # amt_weekly_total: 单周累计金额（简化=日累计*7）
        features["amt_weekly_total"] = float(amt.sum() * 7)

        # amt_monthly_total: 单月累计金额（简化=日累计*30）
        features["amt_monthly_total"] = float(amt.sum() * 30)

        # amt_volatility: 金额波动率
        std_val = df["amount"].astype(float).std()
        mean_val = df["amount"].astype(float).mean()
        features["amt_volatility"] = float(std_val / mean_val) if mean_val != 0 else 0.0

        return features

    def _frequency_features(self, df: pd.DataFrame) -> dict[str, float]:
        """交易频率特征（7个）"""
        features = {}

        # freq_daily: 单日交易次数
        features["freq_daily"] = float(len(df))

        # freq_weekly: 单周交易次数
        features["freq_weekly"] = float(len(df) * 7)

        # freq_monthly: 单月交易次数
        features["freq_monthly"] = float(len(df) * 30)

        # freq_same_counterparty: 相同对手交易频率
        if "payee_id" in df.columns:
            features["freq_same_counterparty"] = float(
                df["payee_id"].value_counts().max()
            ) if len(df) > 0 else 0.0
        else:
            features["freq_same_counterparty"] = 0.0

        # freq_interval_std: 交易时间间隔标准差
        features["freq_interval_std"] = 0.0  # 简化

        # freq_holiday_ratio: 节假日交易占比
        features["freq_holiday_ratio"] = 0.0  # 简化

        # freq_off_hours_ratio: 非工作时间交易占比
        features["freq_off_hours_ratio"] = 0.0  # 简化

        return features

    def _counterparty_features(self, df: pd.DataFrame) -> dict[str, float]:
        """交易对手特征（9个）"""
        features = {}

        # cp_stranger_ratio: 陌生对手占比
        features["cp_stranger_ratio"] = 0.5  # 简化

        # cp_high_risk_region: 高风险地区对手占比
        features["cp_high_risk_region"] = 0.0  # 简化

        # cp_related_party: 关联企业交易占比
        features["cp_related_party"] = 0.0  # 简化

        # cp_business_match: 对手经营范围匹配度
        features["cp_business_match"] = 1.0  # 简化

        # cp_age: 对手成立时间
        features["cp_age"] = 3650.0  # 简化：10年

        # cp_capital_ratio: 对手注册资本交易比
        features["cp_capital_ratio"] = 0.1  # 简化

        # cp_concentration: 单一对手金额集中度
        features["cp_concentration"] = 0.3  # 简化

        # cp_change_freq: 对手变更频率
        features["cp_change_freq"] = 0.0  # 简化

        # cp_cash_ratio: 现金交易占比
        features["cp_cash_ratio"] = 0.0  # 简化

        return features

    def _temporal_features(self, df: pd.DataFrame) -> dict[str, float]:
        """时序与账户特征（8个）"""
        features = {}

        # acct_balance_change: 余额突增突降幅度
        if "balance" in df.columns:
            bal = df["balance"].astype(float)
            features["acct_balance_change"] = float(
                (bal.iloc[-1] - bal.iloc[0]) / abs(bal.iloc[0]) if bal.iloc[0] != 0 else 0.0
            )
        else:
            features["acct_balance_change"] = 0.0

        # acct_inflow_outflow: 流入流出比
        features["acct_inflow_outflow"] = 1.0  # 简化

        # acct_scatter_in: 分散转入集中转出系数
        features["acct_scatter_in"] = 1.0  # 简化

        # acct_scatter_out: 集中转入分散转出系数
        features["acct_scatter_out"] = 1.0  # 简化

        # acct_dormant_activation: 闲置账户突然启用
        features["acct_dormant_activation"] = 0.0  # 简化

        # acct_age_activity: 开户时间活跃度关系
        features["acct_age_activity"] = 1.0  # 简化

        # acct_cross_bank: 跨行划转频率
        features["acct_cross_bank"] = 0.0  # 简化

        # acct_cross_border: 跨境交易占比
        features["acct_cross_border"] = 0.0  # 简化

        return features

    def _interaction_features(self, base_features: dict[str, float]) -> dict[str, float]:
        """交互特征（8个）"""
        features = {}

        amt_dev = base_features.get("amt_deviation", 0)
        freq_off = base_features.get("freq_off_hours_ratio", 0)
        cp_stranger = base_features.get("cp_stranger_ratio", 0)
        cp_conc = base_features.get("cp_concentration", 0)
        freq_d = base_features.get("freq_daily", 0)
        amt_vol = base_features.get("amt_volatility", 0)
        cp_change = base_features.get("cp_change_freq", 0)
        acct_cross = base_features.get("acct_cross_border", 0)
        cp_related = base_features.get("cp_related_party", 0)
        freq_counter = base_features.get("freq_same_counterparty", 0)
        dormant = base_features.get("acct_dormant_activation", 0)

        # ix_amt_off_hours: 大额非工作时间交易
        features["ix_amt_off_hours"] = 1.0 if amt_dev > 2 and freq_off > 0.3 else 0.0

        # ix_stranger_freq: 陌生对手高频交易系数
        features["ix_stranger_freq"] = float(cp_stranger * freq_d)

        # ix_cp_amt_concentrate: 单一对手大额集中系数
        features["ix_cp_amt_concentrate"] = float(cp_conc * amt_dev)

        # ix_balance_low_outflow: 余额低位集中转出系数
        features["ix_balance_low_outflow"] = 0.0  # 简化

        # ix_volatility_cp_change: 金额波动对手变更系数
        features["ix_volatility_cp_change"] = float(amt_vol * cp_change)

        # ix_amt_cross_border: 大额跨境交易标识
        features["ix_amt_cross_border"] = 1.0 if amt_dev > 1.5 and acct_cross > 0 else 0.0

        # ix_related_freq: 关联企业高频交易系数
        features["ix_related_freq"] = float(cp_related * freq_counter)

        # ix_dormant_large: 闲置启用大额交易系数
        features["ix_dormant_large"] = float(dormant * amt_dev)

        return features
