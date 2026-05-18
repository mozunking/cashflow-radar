# 设计文档索引

本文档为资金异常筛查算法模型模块（CAD）设计文档的总体索引，汇总各子方案的入口链接。

---

## 一、产品与架构设计

| 文档 | 路径 | 概述 |
|------|------|------|
| **产品定义（UVP）** | [product.md](product.md) | 产品概述、用户画像、用户故事、价值主张、设计原则、演进路线 |
| **系统架构** | [architecture/SYSTEM_ARCHITECTURE.md](architecture/SYSTEM_ARCHITECTURE.md) | 架构全景、技术栈选型、模块边界、数据契约 |
| **模块设计** | [architecture/MODULE_DESIGN.md](architecture/MODULE_DESIGN.md) | 各模块职责、接口契约、依赖关系 |
| **数据契约** | [architecture/DATA_CONTRACT.md](architecture/DATA_CONTRACT.md) | 模块间数据结构定义 |
| **需求方案** | [requirements.md](requirements.md) | 业务需求、功能需求、非功能需求、验收标准 |

---

## 二、详细设计

| 文档 | 路径 | 概述 |
|------|------|------|
| **算法设计** | [architecture/ALGORITHM_DESIGN.md](architecture/ALGORITHM_DESIGN.md) | IForest/LOF/Graph模型、融合引擎、解释引擎、降级管理 |
| **数据质量校验** | [architecture/DATA_QUALITY.md](architecture/DATA_QUALITY.md) | 校验规则、阈值、不通过处理 |
| **特征工厂** | [architecture/FEATURE_FACTORY.md](architecture/FEATURE_FACTORY.md) | 5类40个特征清单、特征处理流水线 |
| **数据库设计** | [architecture/DATABASE_DESIGN.md](architecture/DATABASE_DESIGN.md) | 核心表结构、索引、留存策略 |
| **API设计** | [architecture/API_DESIGN.md](architecture/API_DESIGN.md) | API清单、错误码、FastAPI核心代码 |
| **管理控制台设计** | [architecture/CONSOLE_DESIGN.md](architecture/CONSOLE_DESIGN.md) | 4页面详细设计、交互规格 |
| **安全与合规** | [architecture/SECURITY_COMPLIANCE.md](architecture/SECURITY_COMPLIANCE.md) | STRIDE威胁分析、国密适配、等保2.0映射 |
| **可观测性** | [architecture/OBSERVABILITY.md](architecture/OBSERVABILITY.md) | SLI/SLO/SLA、监控指标、PSI计算 |

---

## 三、版本历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| V1-V6 | 2026-04~05 | 架构迭代、技术修正、UVP重构、安全增强 | 产品架构组 |
| V7-V9 | 2026-05 | 多专家联审、事件驱动、A/B框架、国密适配、混沌工程 | 多团队联编 |
| V10 | 2026-05-18 | 终极定稿：正式规范文档、开源复用清单、完整Runbook、并行开发计划 | 产品架构组 |

---

## 四、关联文档

- [开发文档索引](../development/SK.md)
- [技术文档索引](../technical/SK.md)
- [测试文档索引](../testing/SK.md)
- [部署文档索引](../deployment/SK.md)
- [检查方案索引](../check/SK.md)
- [改进方案索引](../improvement/SK.md)
- [执行进展索引](../process/SK.md)