# 开发文档索引

本文档为CAD项目开发工作的总体索引。

---

## 一、开发工作流

| 文档 | 路径 | 概述 |
|------|------|------|
| **开发工作流** | [workflow.md](workflow.md) | TDD流程、多代理协作、代码规范 |
| **模块开发方案** | [modules/SK.md](modules/SK.md) | 各模块开发计划、交付标准 |

---

## 二、模块开发方案

| 模块 | 负责角色 | 交付物 | 截止时间 |
|------|---------|--------|---------|
| cad-data-quality | 数据工程师 | DataQualityChecker组件+UT | Week 2 |
| cad-feature-engine | 数据工程师 | FeatureFactory组件+UT | Week 4 |
| cad-model-pool | 数据科学家 | 3个模型+MLflow记录 | Week 4 |
| cad-fusion-engine | 数据科学家 | FusionEngine+回测报告 | Week 6 |
| cad-explainer | 数据科学家 | ExplainerEngine+业务语义映射 | Week 6 |
| cad-degradation | 后端开发 | DegradationManager+降级策略 | Week 6 |
| cad-service | 后端开发 | FastAPI服务+API文档 | Week 8 |
| cad-console | 前端开发 | Streamlit 4页面 | Week 8 |
| cad-infra | 运维工程师 | Docker Compose+CI/CD | Week 8 |

---

## 三、多代理任务拆解

### 并行开发策略

```
Agent-数据工程师:
  → 环境搭建 (Week 1)
  → 数据探查 (Week 1)
  → 质量校验开发 (Week 2)
  → 特征工厂开发 (Week 3-4)

Agent-数据科学家:
  → IForest模型开发 (Week 3-4)
  → LOF模型开发 (Week 3-4)
  → Graph模型开发 (Week 3-4)
  → 模型调优 (Week 5-6)

Agent-后端开发:
  → API框架搭建 (Week 3)
  → 融合引擎对接 (Week 5-6)
  → 解释引擎对接 (Week 5-6)
  → 降级管理开发 (Week 5-6)

Agent-前端开发:
  → 原型设计 (Week 3)
  → 4页面开发 (Week 5-8)

Agent-运维工程师:
  → CI/CD流水线 (Week 7-8)
  → 监控告警配置 (Week 7-8)
  → 灰度环境部署 (Week 9-10)
```

---

## 四、交付标准

| 交付物 | 标准 |
|--------|------|
| 组件代码 | UT覆盖率≥80%，通过契约测试 |
| 模型文件 | MLflow记录完整，可回滚 |
| API服务 | 通过API测试，响应时间达标 |
| 前端页面 | 通过功能测试，页面加载<3秒 |
| 部署配置 | 通过部署验证，热切换成功 |
| 文档 | SK.md索引+模块开发文档齐全 |
