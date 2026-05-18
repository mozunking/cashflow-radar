# 开发工作流

**文档编号**：CAD-DS-V10 | **版本**：10.0 | **日期**：2026-05-18

---

## 1.1 总体流程

```
需求分析 → 设计评审 → 并行开发 → 集成联调 → 测试验证 → 灰度上线 → 正式发布
    ↓          ↓           ↓           ↓           ↓           ↓          ↓
  US-xxx    架构设计    Agent分工   契约测试    回归测试    监控验证    交付确认
```

---

## 1.2 TDD开发流程

### Step 1: 写测试（Red）

```bash
# 为每个模块编写测试用例
pytest tests/unit/test_feature_factory.py -v
# 预期：测试失败（功能未实现）
```

### Step 2: 实现功能（Green）

```bash
# 实现最小功能代码
python -m src.cad_feature_engine
# 预期：测试通过
```

### Step 3: 重构优化（Refactor）

```bash
# 代码审查 + 优化
pytest tests/unit/test_feature_factory.py -v --cov=src
# 覆盖率≥80%通过
```

---

## 1.3 多代理协作规范

### 1.3.1 Agent职责划分

| Agent | 职责范围 | 输入 | 输出 |
|-------|---------|------|------|
| Agent-数据工程师 | 数据质量、特征工程 | 中台宽表 | FeatureOutput |
| Agent-数据科学家 | 模型开发、调优 | 特征数据 | ModelOutput |
| Agent-后端开发 | API服务、融合逻辑 | ModelOutput | REST API |
| Agent-前端开发 | 控制台页面 | REST API响应 | Streamlit页面 |
| Agent-运维 | 部署、监控、CI/CD | 容器镜像 | 可用服务 |

### 1.3.2 交接检查点

| 检查点 | 发起方 | 接收方 | 通过标准 |
|--------|--------|--------|---------|
| 契约测试 | 数据工程师 | 数据科学家 | 特征接口UT通过 |
| 模型交付 | 数据科学家 | 后端开发 | MLflow记录完整 |
| API联调 | 后端开发 | 前端开发 | API测试通过 |
| 部署验证 | 运维 | 全队 | 灰度环境可用 |

---

## 1.4 代码规范

### Python规范

- **风格**：Black + isort
- **类型检查**：Pyright
- **Import顺序**：标准库→第三方库→本地模块

```bash
# 格式化
black src/
isort src/

# 类型检查
pyright src/
```

### Git提交规范

```
格式：<类型>(<模块>): <描述>

类型：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- refactor: 重构
- test: 测试
- chore: 杂项

示例：
feat(feature-engine): 添加交易频率特征计算
fix(fusion-engine): 修复融合权重边界问题
docs(api): 更新API错误码文档
```

---

## 1.5 契约测试

### 模块间契约

```python
# tests/contract/test_feature_factory_contract.py
def test_feature_output_contract():
    """特征工厂输出必须符合FeatureOutput契约"""
    result = FeatureFactory.compute(sample_df)
    assert hasattr(result, 'transaction_id')
    assert hasattr(result, 'features')
    assert hasattr(result, 'feature_version')
    assert isinstance(result.features, dict)
```

### API契约

```python
# tests/contract/test_api_contract.py
def test_batch_detect_contract():
    """批量检测API响应符合BatchDetectResponse契约"""
    response = client.post("/api/v1/detect/batch", json={
        "data_date": "2026-05-17"
    })
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert "anomaly_count" in response.json()
```

---

## 1.6 Code Review清单

| 检查项 | 标准 |
|--------|------|
| 功能完整性 | 所有US验收标准有对应实现 |
| 代码质量 | 无坏味道，圈复杂度≤10 |
| 测试覆盖 | UT覆盖率≥80% |
| 错误处理 | 所有异常有明确处理 |
| 日志埋点 | 关键路径有INFO日志 |
| 安全检查 | 无硬编码密码/密钥 |
