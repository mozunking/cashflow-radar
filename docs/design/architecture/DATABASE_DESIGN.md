# 数据库设计

**文档编号**：CAD-DS-V10 | **版本**：10.0 | **日期**：2026-05-18

---

## 4.1 核心表结构

### 4.1.1 预警结果表 (cad_alert)

```sql
CREATE TABLE cad_alert (
    id              BIGSERIAL PRIMARY KEY,
    transaction_id  VARCHAR(64) NOT NULL,
    account_id      VARCHAR(64) NOT NULL,
    data_date       DATE NOT NULL,
    amount          DECIMAL(18,2),
    rule_hit        BOOLEAN DEFAULT FALSE,
    rule_score      DECIMAL(5,2) DEFAULT 0,
    algo_score      DECIMAL(5,2) DEFAULT 0,
    final_score     DECIMAL(5,2) NOT NULL,
    risk_level      VARCHAR(10) NOT NULL,
    anomaly_type    VARCHAR(10),
    model_scores    JSONB,
    shadow_mode     BOOLEAN DEFAULT TRUE,
    run_id          VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(transaction_id, data_date)
);
CREATE INDEX idx_alert_date ON cad_alert(data_date);
CREATE INDEX idx_alert_risk ON cad_alert(risk_level, data_date);
CREATE INDEX idx_alert_type ON cad_alert(anomaly_type);
```

### 4.1.2 人工复核反馈表 (cad_feedback)

```sql
CREATE TABLE cad_feedback (
    id              BIGSERIAL PRIMARY KEY,
    alert_id        BIGINT REFERENCES cad_alert(id),
    transaction_id  VARCHAR(64) NOT NULL,
    reviewer_id     VARCHAR(64) NOT NULL,
    review_result   VARCHAR(16) NOT NULL,
    review_comment  TEXT,
    anomaly_type    VARCHAR(10),
    anomaly_score   DECIMAL(5,2),
    feature_snapshot JSONB,
    reviewed_at     TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_feedback_result ON cad_feedback(review_result);
CREATE INDEX idx_feedback_reviewer ON cad_feedback(reviewer_id);
```

### 4.1.3 模型版本表 (cad_model_version)

```sql
CREATE TABLE cad_model_version (
    id              BIGSERIAL PRIMARY KEY,
    model_name      VARCHAR(32) NOT NULL,
    version         VARCHAR(32) NOT NULL,
    status          VARCHAR(16) NOT NULL,
    mlflow_run_id   VARCHAR(64),
    feature_version VARCHAR(32),
    parameters      JSONB,
    metrics         JSONB,
    contamination   DECIMAL(6,4) DEFAULT 0.01,
    fusion_weight   DECIMAL(4,2),
    deploy_reason   TEXT,
    approver        VARCHAR(64),
    deployed_at     TIMESTAMPTZ,
    retired_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(model_name, version)
);
```

### 4.1.4 数据血缘表 (cad_lineage)

```sql
CREATE TABLE cad_lineage (
    id              BIGSERIAL PRIMARY KEY,
    run_id          VARCHAR(64) NOT NULL UNIQUE,
    data_date       DATE NOT NULL,
    source_table    VARCHAR(128),
    source_version  VARCHAR(32),
    feature_version VARCHAR(32),
    feature_count   INTEGER,
    quality_passed  BOOLEAN,
    record_count    INTEGER,
    model_versions  JSONB,
    fusion_phase    VARCHAR(16),
    output_table    VARCHAR(128),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.1.5 审计日志表 (cad_audit_log)

```sql
CREATE TABLE cad_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    operator        VARCHAR(64) NOT NULL,
    action          VARCHAR(32) NOT NULL,
    target_type     VARCHAR(32),
    target_id       VARCHAR(64),
    details         JSONB,
    ip_address      VARCHAR(45),
    trace_id        VARCHAR(16),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_operator ON cad_audit_log(operator);
CREATE INDEX idx_audit_action ON cad_audit_log(action);
```

### 4.1.6 PSI漂移记录表 (cad_drift)

```sql
CREATE TABLE cad_drift (
    id              BIGSERIAL PRIMARY KEY,
    feature_name    VARCHAR(64) NOT NULL,
    psi_value       DECIMAL(8,6) NOT NULL,
    status          VARCHAR(10) NOT NULL,
    baseline_date   DATE,
    check_date      DATE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_drift_date ON cad_drift(check_date);
```

---

## 4.2 数据留存

| 表 | 保留期 | 归档策略 |
|----|--------|---------|
| cad_alert | 24个月 | 超期迁移至cad_alert_archive |
| cad_feedback | 24个月 | 同上 |
| cad_model_version | 永久 | — |
| cad_lineage | 24个月 | 同alert |
| cad_audit_log | 36个月（合规） | 审批后安全擦除 |
| cad_drift | 12个月 | 超期删除 |

---

## 4.3 角色权限矩阵

| 功能 | 风控分析师 | 风控主管 | 数据科学家 | 运维工程师 | 审计人员 |
|------|-----------|---------|-----------|-----------|---------|---------|
| 监控仪表盘 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 预警复核 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 复核审批 | ❌ | ✅ | ❌ | ❌ | ❌ |
| 模型训练 | ❌ | ❌ | ✅ | ❌ | ❌ |
| 模型发布/下线 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 降级策略 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 用户管理 | ❌ | ❌ | ❌ | ✅ | ❌ |
| 审计日志 | ❌ | ✅ | ❌ | ✅ | ✅ |
