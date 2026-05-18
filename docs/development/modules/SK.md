# 模块开发方案索引

本文档汇总各模块的详细开发方案。

---

## 模块列表

| 模块 | 开发方案 | 负责 | 截止 |
|------|---------|------|------|
| cad-data-quality | [data-quality.md](data-quality.md) | 数据工程师 | Week 2 |
| cad-feature-engine | [feature-engine.md](feature-engine.md) | 数据工程师 | Week 4 |
| cad-model-pool | [model-pool.md](model-pool.md) | 数据科学家 | Week 4 |
| cad-fusion-engine | [fusion-engine.md](fusion-engine.md) | 数据科学家 | Week 6 |
| cad-explainer | [explainer.md](explainer.md) | 数据科学家 | Week 6 |
| cad-degradation | [degradation.md](degradation.md) | 后端开发 | Week 6 |
| cad-service | [service.md](service.md) | 后端开发 | Week 8 |
| cad-console | [console.md](console.md) | 前端开发 | Week 8 |
| cad-infra | [infra.md](infra.md) | 运维工程师 | Week 8 |

---

## 通用要求

### 代码规范
- Python: Black + isort + Pyright
- UT覆盖率: ≥80%
- 契约测试: 通过

### 交付物
- 源代码（含UT）
- 模块开发文档
- API接口文档（OpenAPI）
- 部署配置（Dockerfile/docker-compose.yml）
