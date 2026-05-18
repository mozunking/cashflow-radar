"""Degradation Manager for CAD

模型降级管理：监控模型健康状态，自动降级/恢复
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DegradationManager:
    """降级管理器"""

    LEVELS = {
        "full": "全部正常",
        "partial": "部分降级",
        "rules_only": "仅规则",
        "blocked": "完全阻断",
    }

    def __init__(self, fail_threshold: int = 3, redis_client: Any = None):
        self.level = "full"
        self.degraded: set[str] = set()
        self.fail_count: dict[str, int] = field(default_factory=dict)
        self.fail_threshold = fail_threshold
        self.redis = redis_client
        self._lock = threading.Lock()

    def report_failure(self, name: str) -> None:
        """报告模型失败"""
        with self._lock:
            self.fail_count[name] = self.fail_count.get(name, 0) + 1
        if self.fail_count[name] >= self.fail_threshold:
            self.degraded.add(name)
            self._update()
            self._persist()

    def report_success(self, name: str) -> None:
        """报告模型成功"""
        with self._lock:
            self.fail_count[name] = 0
        if name in self.degraded:
            self.degraded.discard(name)
            self._update()
            self._persist()

    def _update(self) -> None:
        """更新降级级别"""
        if not self.degraded:
            self.level = "full"
        elif len(self.degraded) < 3:
            self.level = "partial"
        else:
            self.level = "rules_only"

    def _persist(self) -> None:
        """持久化状态到Redis"""
        if self.redis:
            self.redis.hset(
                "cad:degradation",
                mapping={
                    "level": self.level,
                    "degraded": ",".join(self.degraded),
                    "updated_at": datetime.now().isoformat(),
                },
            )

    def active_models(self) -> list[str]:
        """返回当前可用的模型列表"""
        all_models = ["iforest", "lof", "graph"]
        return [m for m in all_models if m not in self.degraded]

    def get_state(self) -> dict[str, Any]:
        """获取当前降级状态"""
        return {
            "level": self.level,
            "level_desc": self.LEVELS.get(self.level, ""),
            "degraded": list(self.degraded),
            "fail_count": self.fail_count.copy(),
            "active_models": self.active_models(),
        }

    def is_available(self) -> bool:
        """判断服务是否可用（至少有一个模型可用）"""
        return len(self.active_models()) > 0
