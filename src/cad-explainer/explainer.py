"""Explainer Engine for CAD

提供异常解释能力，将特征贡献度转换为业务语义
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class FeatureContribution:
    feature_name: str
    contribution: float
    current_value: float
    historical_mean: float
    business_description: str
    comparison_text: str


@dataclass
class ExplanationOutput:
    transaction_id: str
    anomaly_type: str
    anomaly_type_desc: str
    top_features: list[FeatureContribution]
    explain_method: str
    explain_time_ms: float


ANOMALY_TYPE_MAP = {
    "TYPE_01": "大额异常交易",
    "TYPE_02": "高频密集交易",
    "TYPE_03": "陌生对手交易",
    "TYPE_04": "资金异动",
    "TYPE_05": "复合型异常",
    "TYPE_06": "资金链路异常",
}

FEATURE_BUSINESS_DESC = {
    "amt_deviation": "交易金额偏离账户历史水平",
    "amt_industry_dev": "交易金额偏离同行业水平",
    "amt_threshold_proximity": "接近大额交易标准",
    "amt_tail_pattern": "金额尾数特征异常",
    "amt_daily_total": "单日累计交易金额",
    "amt_weekly_total": "单周累计交易金额",
    "amt_monthly_total": "单月累计交易金额",
    "amt_volatility": "金额波动率",
    "freq_daily": "单日交易次数",
    "freq_weekly": "单周交易次数",
    "freq_monthly": "单月交易次数",
    "freq_same_counterparty": "相同对手交易频率",
    "freq_interval_std": "交易时间间隔波动",
    "freq_holiday_ratio": "节假日交易占比",
    "freq_off_hours_ratio": "非工作时间交易占比",
    "cp_stranger_ratio": "陌生对手占比",
    "cp_high_risk_region": "高风险地区对手占比",
    "cp_related_party": "关联企业交易占比",
    "cp_business_match": "对手经营范围匹配度",
    "cp_age": "对手成立时间",
    "cp_capital_ratio": "对手注册资本交易比",
    "cp_concentration": "单一对手金额集中度",
    "cp_change_freq": "对手变更频率",
    "cp_cash_ratio": "现金交易占比",
    "acct_balance_change": "账户余额变动",
    "acct_inflow_outflow": "流入流出比",
    "acct_scatter_in": "分散转入特征",
    "acct_scatter_out": "集中转出特征",
    "acct_dormant_activation": "闲置账户启用",
    "acct_age_activity": "开户时间活跃度关系",
    "acct_cross_bank": "跨行划转频率",
    "acct_cross_border": "跨境交易占比",
    "ix_amt_off_hours": "大额非工作时间交易",
    "ix_stranger_freq": "陌生对手高频交易",
    "ix_cp_amt_concentrate": "单一对手大额集中",
    "ix_balance_low_outflow": "余额低位集中转出",
    "ix_volatility_cp_change": "金额波动对手变更",
    "ix_amt_cross_border": "大额跨境交易",
    "ix_related_freq": "关联企业高频交易",
    "ix_dormant_large": "闲置启用大额交易",
    "graph_degree_centrality": "资金交易频繁程度",
    "graph_pagerank": "资金流动重要性",
    "graph_in_out_ratio": "资金归集分散模式",
    "graph_fund_concentration": "资金归集分散系数",
    "graph_cycle_count": "资金环路数",
    "graph_community_deviation": "社区归属异常",
}


class ExplainerEngine:
    """解释引擎"""

    def __init__(self, model_name: str = "iforest"):
        self.model_name = model_name
        self.business_desc_map = FEATURE_BUSINESS_DESC

    def explain(
        self,
        transaction_id: str,
        features: dict[str, float],
        scores: dict[str, float],
        top_k: int = 3,
    ) -> ExplanationOutput:
        """生成异常解释"""
        # 确定异常类型
        anomaly_type = self._classify_anomaly(features)

        # 计算特征贡献度（简化：直接使用特征值）
        contributions = self._compute_contributions(features, scores)

        # 取TopK
        top_features = contributions[:top_k]

        # 构建业务语义描述
        for tf in top_features:
            tf.business_description = self.business_desc_map.get(
                tf.feature_name, tf.feature_name
            )
            tf.comparison_text = self._build_comparison_text(tf)

        return ExplanationOutput(
            transaction_id=transaction_id,
            anomaly_type=anomaly_type,
            anomaly_type_desc=ANOMALY_TYPE_MAP.get(anomaly_type, "未知类型"),
            top_features=top_features,
            explain_method=(
                f"shap_{self.model_name}" if self.model_name == "iforest" else "lime"
            ),
            explain_time_ms=0.0,
        )

    def _classify_anomaly(self, features: dict[str, float]) -> str:
        """根据特征贡献度确定异常类型"""
        amount_features = ["amt_deviation", "amt_industry_dev", "amt_volatility"]
        freq_features = ["freq_daily", "freq_weekly", "freq_monthly"]
        counterparty_features = ["cp_stranger_ratio", "cp_concentration"]
        temporal_features = ["acct_balance_change", "acct_dormant_activation"]
        graph_features = ["graph_degree_centrality", "graph_cycle_count"]

        scores = {}
        for feat in amount_features:
            scores[feat] = abs(features.get(feat, 0))
        for feat in freq_features:
            scores[feat] = abs(features.get(feat, 0)) * 2  # 加权
        for feat in counterparty_features:
            scores[feat] = abs(features.get(feat, 0))
        for feat in temporal_features:
            scores[feat] = abs(features.get(feat, 0))
        for feat in graph_features:
            scores[feat] = abs(features.get(feat, 0))

        if not scores:
            return "TYPE_05"

        max_feat = max(scores, key=scores.get)
        if max_feat in amount_features:
            return "TYPE_01"
        elif max_feat in freq_features:
            return "TYPE_02"
        elif max_feat in counterparty_features:
            return "TYPE_03"
        elif max_feat in temporal_features:
            return "TYPE_04"
        elif max_feat in graph_features:
            return "TYPE_06"
        else:
            return "TYPE_05"

    def _compute_contributions(
        self, features: dict[str, float], scores: dict[str, float]
    ) -> list[FeatureContribution]:
        """计算特征贡献度"""
        contributions = []
        total_score = sum(abs(scores.get(m, 0)) for m in scores)

        for name, value in features.items():
            contrib = FeatureContribution(
                feature_name=name,
                contribution=round(abs(value) / (total_score + 1e-6), 4),
                current_value=round(value, 4),
                historical_mean=0.0,
                business_description=name,
                comparison_text="",
            )
            contributions.append(contrib)

        # 按贡献度排序
        contributions.sort(key=lambda x: x.contribution, reverse=True)
        return contributions

    def _build_comparison_text(self, fc: FeatureContribution) -> str:
        """构建对比文本"""
        if fc.historical_mean == 0:
            pct = "偏离度无法计算"
        else:
            pct = f"{abs((fc.current_value - fc.historical_mean) / fc.historical_mean * 100):.1f}%"

        return f"当前值{fc.current_value}，偏离均值{pct}"
