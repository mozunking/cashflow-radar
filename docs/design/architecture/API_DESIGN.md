# API设计

**文档编号**：CAD-DS-V10 | **版本**：10.0 | **日期**：2026-05-18

---

## 5.1 API清单

| API | 方法 | 路径 | 用途 | 鉴权角色 |
|-----|------|------|------|---------|
| 批量检测 | POST | `/api/v1/detect/batch` | T+1离线批量 | admin,operator |
| 健康检查 | GET | `/api/v1/health` | 服务状态 | 无 |
| 降级状态 | GET | `/api/v1/health/degradation` | 降级级别 | admin,operator |
| 异常解释 | GET | `/api/v1/explain/{txn_id}` | 异常解释 | all |
| 模型列表 | GET | `/api/v1/models` | 模型列表 | all |
| 模型详情 | GET | `/api/v1/models/{name}` | 版本与指标 | all |
| 模型发布 | POST | `/api/v1/models/{name}/deploy` | 部署生产 | admin |
| 模型下线 | POST | `/api/v1/models/{name}/undeploy` | 下线 | admin |
| 模型回滚 | POST | `/api/v1/models/{name}/rollback` | 回滚 | admin |
| 反馈提交 | POST | `/api/v1/feedback` | 人工复核 | analyst,supervisor |
| 反馈统计 | GET | `/api/v1/feedback/stats` | 统计 | all |
| 漂移检测 | GET | `/api/v1/drift/psi` | 逐特征PSI | all |
| 回测执行 | POST | `/api/v1/backtest/run` | 触发回测 | scientist,admin |
| 回测结果 | GET | `/api/v1/backtest/{task_id}` | 获取结果 | scientist,admin |
| 审计日志 | GET | `/api/v1/audit/logs` | 操作日志 | supervisor,audit |

---

## 5.2 统一错误码

| 错误码 | HTTP状态 | 含义 | 场景 |
|--------|---------|------|------|
| CAD-001 | 400 | 请求参数校验失败 | 必填字段缺失 |
| CAD-002 | 401 | 未认证 | JWT缺失或过期 |
| CAD-003 | 403 | 无权限 | 角色无操作权限 |
| CAD-004 | 404 | 资源不存在 | 模型/交易不存在 |
| CAD-005 | 409 | 冲突 | 模型已在部署中 |
| CAD-010 | 422 | 数据质量校验未通过 | 输入数据异常 |
| CAD-020 | 500 | 内部服务错误 | 未预期异常 |
| CAD-021 | 503 | 服务降级 | 算法全量降级 |

---

## 5.3 数据契约

### 特征工厂输出 (FeatureOutput)

```python
class FeatureOutput(BaseModel):
    transaction_id: str
    account_id: str
    features: dict[str, float]
    feature_version: str
    computed_at: datetime
    quality_passed: bool
    quality_details: list[str] | None = None
```

### 模型池输出 (ModelOutput)

```python
class ModelOutput(BaseModel):
    model_name: str
    model_version: str
    anomaly_score: float              # 0-100
    anomaly_flag: bool
    contamination: float
    inference_time_ms: float
```

### 融合引擎输出 (FusionOutput)

```python
class FusionOutput(BaseModel):
    transaction_id: str
    rule_hit: bool
    rule_score: float
    algo_score: float
    final_score: float
    risk_level: str                   # 高风险/中风险/低风险
    phase: str                        # gray/validation/stable
    model_contributions: dict[str, float]
```

### 解释引擎输出 (ExplanationOutput)

```python
class FeatureContribution(BaseModel):
    feature_name: str
    contribution: float
    current_value: float
    historical_mean: float
    business_description: str
    comparison_text: str

class ExplanationOutput(BaseModel):
    transaction_id: str
    anomaly_type: str                 # TYPE_01~TYPE_06
    anomaly_type_desc: str            # 业务语义
    top_features: list[FeatureContribution]
    explain_method: str
    explain_time_ms: float
```

---

## 5.4 日志规范

所有日志遵循结构化JSON格式，包含trace_id支持链路追踪：

| 事件 | 级别 | 关键字段 |
|------|------|---------|
| 服务启动 | INFO | models_loaded, phase |
| 数据质量校验失败 | WARNING | data_date, check_results |
| 模型推理失败 | ERROR | model_name, error, consecutive_failures |
| 降级切换 | CRITICAL | from_level, to_level, degraded_models |
| 模型发布 | INFO | model_name, version, approver |
| 预警复核 | INFO | txn_id, reviewer, result |
| PSI漂移告警 | WARNING | feature, psi_value |
