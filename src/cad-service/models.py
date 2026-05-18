"""CAD Pydantic Models"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class BatchDetectRequest(BaseModel):
    data_date: str = Field(description="数据日期 YYYY-MM-DD")
    feature_version: str | None = Field(default=None, description="特征版本")

    @field_validator("data_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("data_date must be in YYYY-MM-DD format")
        return v


class AnomalyResult(BaseModel):
    transaction_id: str
    account_id: str
    rule_hit: bool
    rule_score: float
    algo_score: float
    final_score: float
    risk_level: str
    anomaly_type: str | None = None
    model_scores: dict[str, float] = {}


class BatchDetectResponse(BaseModel):
    task_id: str
    total_count: int
    anomaly_count: int
    high_risk: int
    medium_risk: int
    low_risk: int
    results: list[AnomalyResult] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class FeedbackRequest(BaseModel):
    transaction_id: str
    review_result: str = Field(description="确认/排除/存疑")
    review_comment: str = Field(description="复核意见")
    anomaly_type: str | None = None

    @field_validator("review_result")
    @classmethod
    def validate_review_result(cls, v: str) -> str:
        if v not in ("确认", "排除", "存疑"):
            raise ValueError("review_result must be 确认, 排除, or 存疑")
        return v


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    feedback_id: str | None = None


class ModelInfo(BaseModel):
    name: str
    version: str
    status: str
    metrics: dict[str, float] = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    degradation_level: str | None = None
    degraded_models: list[str] = []


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict[str, Any] | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
