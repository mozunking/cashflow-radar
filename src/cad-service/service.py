"""CAD Service Business Logic"""
import uuid
from datetime import datetime
from typing import Any

import pandas as pd

from cad_data_quality import DataQualityChecker
from cad_feature_engine import FeatureFactory
from cad_model_pool import ModelPool
from cad_fusion_engine import FusionEngine
from cad_explainer import ExplainerEngine
from cad_degradation import DegradationManager


class CADService:
    """CAD服务"""

    def __init__(self):
        self.checker = DataQualityChecker()
        self.feature_factory = FeatureFactory()
        self.model_pool = ModelPool(contamination=0.01)
        self.fusion_engine = FusionEngine(phase="gray")
        self.explainer = ExplainerEngine()
        self.degradation = DegradationManager(fail_threshold=3)
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            # 模拟加载模型（实际从MinIO/MLflow加载）
            sample_data = pd.DataFrame({
                "f1": [0.1] * 10,
                "f2": [0.2] * 10,
                "f3": [0.3] * 10,
            })
            self.model_pool.fit(sample_data)
            self._initialized = True

    async def batch_detect(
        self, data_date: str, feature_version: str | None = None
    ) -> Any:
        """批量检测"""
        self._ensure_initialized()

        # 模拟数据
        df = pd.DataFrame({
            "transaction_id": [f"TXN{i:06d}" for i in range(100)],
            "account_id": [f"ACC{i % 10:04d}" for i in range(100)],
            "amount": [10000.0 + i * 100 for i in range(100)],
            "balance": [100000.0] * 100,
        })

        # 质量校验
        quality_result = self.checker.run_all(df, ["transaction_id", "amount"])

        # 特征计算
        features = self.feature_factory.compute(df)

        # 模型推理
        scores = self.model_pool.decision_function(df)

        # 融合打分
        results = []
        for i in range(len(df)):
            txn_id = df.iloc[i]["transaction_id"]
            rule_hit = i % 20 == 0  # 模拟20%规则命中
            rule_score = 85.0 if rule_hit else 0.0
            score_dict = {name: float(scores[name][i]) for name in scores}

            fusion_result = self.fusion_engine.fuse(
                rule_hit=rule_hit,
                rule_score=rule_score,
                scores=score_dict,
                transaction_id=txn_id,
            )

            results.append({
                "transaction_id": txn_id,
                "account_id": df.iloc[i]["account_id"],
                "rule_hit": rule_hit,
                "rule_score": rule_score,
                "algo_score": fusion_result.algo_score,
                "final_score": fusion_result.final_score,
                "risk_level": fusion_result.risk_level,
                "anomaly_type": "TYPE_01",
                "model_scores": score_dict,
            })

        # 统计
        high_risk = sum(1 for r in results if r["risk_level"] == "高风险")
        medium_risk = sum(1 for r in results if r["risk_level"] == "中风险")

        return {
            "task_id": f"task_{uuid.uuid4().hex[:8]}",
            "total_count": len(results),
            "anomaly_count": sum(1 for r in results if r["final_score"] >= 60),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": len(results) - high_risk - medium_risk,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_explanation(self, transaction_id: str) -> dict | None:
        """获取异常解释"""
        self._ensure_initialized()

        # 模拟返回
        return {
            "transaction_id": transaction_id,
            "anomaly_type": "TYPE_01",
            "anomaly_type_desc": "大额异常交易",
            "top_features": [
                {
                    "feature_name": "amt_deviation",
                    "contribution": 0.42,
                    "current_value": 3.8,
                    "historical_mean": 0.45,
                    "business_description": "交易金额偏离账户历史水平",
                    "comparison_text": "当前值3.8，偏离均值744%",
                }
            ],
            "explain_method": "shap_iforest",
            "explain_time_ms": 120.5,
        }

    async def submit_feedback(self, request) -> dict:
        """提交反馈"""
        return {
            "success": True,
            "message": "反馈已提交",
            "feedback_id": f"fb_{uuid.uuid4().hex[:8]}",
        }

    def get_models(self) -> list[dict]:
        """获取模型列表"""
        return [
            {"name": "iforest", "version": "1.0.0", "status": "active", "metrics": {"f1": 0.82}},
            {"name": "lof", "version": "1.0.0", "status": "active", "metrics": {"f1": 0.76}},
            {"name": "graph", "version": "1.0.0", "status": "active", "metrics": {"f1": 0.74}},
        ]

    def get_degradation_status(self) -> dict:
        """获取降级状态"""
        return self.degradation.get_state()
