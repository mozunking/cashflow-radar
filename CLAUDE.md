# CAD - Capital Anomaly Detection

**项目路径**: `/Users/hfy/cashflow-radar`

## 技术栈

| 层级 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| API | FastAPI 0.111+ with uvicorn |
| 前端 | Streamlit 1.35+ |
| 数据库 | PostgreSQL (docker) |
| 缓存 | Redis (docker) |
| ML平台 | MLflow 2.13+ |
| 对象存储 | MinIO (docker) |
| 监控 | Prometheus + Grafana |
| 异常检测 | PyOD (IForest, LOF) + NetworkX (Graph) |
| 可解释性 | SHAP, LIME |
| 安全 | gmssl (国密SM2/SM3/SM4), JWT, slowapi |

## 模块结构

```
src/
├── cad-service/        # FastAPI后端 (auth, api, models, service)
├── cad-console/        # Streamlit控制台 (main.py + pages/)
├── cad-data-quality/   # 数据质量检查器
├── cad-feature-engine/ # 特征工厂 (40+特征)
├── cad-model-pool/     # 模型池 (IForest, LOF, Graph)
├── cad-fusion-engine/  # 融合引擎 (phase-based)
├── cad-explainer/      # 可解释性引擎 (SHAP/LIME)
└── cad-degradation/   # 降级管理器
```

## 质量门禁

- 所有模块需通过 `pytest src/*/tests -v`
- 测试覆盖率 ≥ 70%
- 无 P0/P1 Bug
- 安全扫描无高危漏洞

## Git 工作流

- 功能开发在 `feature/*` 分支
- PR 到 `main` 分支
- 需要至少 1 个 approval

## 快捷命令

```bash
# 启动全部服务
docker compose -f docker/compose.dev.yml up -d

# 运行测试
pytest src/*/tests -v

# 启动 API
cd src && uvicorn cad_service.main:app --host 0.0.0.0 --port 8000

# 启动控制台
cd src/cad-console && streamlit run main.py --server.port 8501
```
