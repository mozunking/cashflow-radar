"""Fusion Engine for CAD

规则一票否决 + 算法增量挖掘 + 分阶段权重融合
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FusionOutput:
    transaction_id: str
    rule_hit: bool
    rule_score: float
    algo_score: float
    final_score: float
    risk_level: str
    phase: str
    model_contributions: dict[str, float]


class FusionEngine:
    """融合引擎"""

    PHASE_W = {
        "gray": (0.85, 0.15),
        "validation": (0.70, 0.30),
        "stable": (0.60, 0.40),
    }

    ALGO_W_V1 = {"iforest": 0.45, "lof": 0.30, "graph": 0.25}

    THRESH = {"high": 80, "medium": 60}

    def __init__(
        self,
        phase: str = "gray",
        custom_algo_w: dict[str, float] | None = None,
        custom_phase_w: dict[str, tuple[float, float]] | None = None,
    ):
        if phase not in self.PHASE_W:
            raise ValueError(f"Invalid phase: {phase}")
        self.phase = phase
        self.algo_w = custom_algo_w or self.ALGO_W_V1.copy()
        self.phase_w = custom_phase_w or self.PHASE_W

    def algo_score(self, scores: dict[str, float]) -> float:
        """计算算法综合分数"""
        total = sum(
            scores.get(name, 0) * weight for name, weight in self.algo_w.items()
        )
        return min(max(total, 0), 100)

    def fuse(
        self,
        rule_hit: bool,
        rule_score: float,
        scores: dict[str, float],
        transaction_id: str = "",
    ) -> FusionOutput:
        """融合规则分数和算法分数"""
        rw, aw = self.phase_w[self.phase]
        asc = self.algo_score(scores)

        # 规则一票否决：规则命中时综合分不可被算法稀释
        if rule_hit:
            final = max(rule_score, rule_score * rw + asc * aw)
        else:
            final = asc

        # 风险等级
        if final >= self.THRESH["high"]:
            risk_level = "高风险"
        elif final >= self.THRESH["medium"]:
            risk_level = "中风险"
        else:
            risk_level = "低风险"

        # 模型贡献度
        contribs = {
            name: round(scores.get(name, 0) * weight, 4)
            for name, weight in self.algo_w.items()
        }

        return FusionOutput(
            transaction_id=transaction_id,
            rule_hit=rule_hit,
            rule_score=rule_score,
            algo_score=round(asc, 2),
            final_score=round(final, 2),
            risk_level=risk_level,
            phase=self.phase,
            model_contributions=contribs,
        )

    def get_state(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "algo_weights": self.algo_w,
            "phase_weights": {
                k: f"{v[0]}/{v[1]}" for k, v in self.phase_w.items()
            },
        }
