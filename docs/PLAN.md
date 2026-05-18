# CAD 实施计划 (PLAN.md)

**版本**: 1.0 | **日期**: 2026-05-18 | **状态**: 执行中

## 竖切片任务清单

### Phase 4 任务 (隔离开发)

#### P0 - 安全关键 (立即修复)

- [ ] **SEC-1**: 修复 JWT auth stub - 实现完整的 SM2 签名验证
  - 文件: `src/cad-service/auth.py`
  - 验证: 单元测试 + 无效签名被拒绝

- [ ] **SEC-2**: 移除 docker-compose.yml 硬编码密码
  - 文件: `docker/compose.dev.yml`
  - 验证: 使用环境变量或 secrets

- [ ] **SEC-3**: 移除 MinIO 默认凭证
  - 文件: `docker/compose.dev.yml`
  - 验证: 使用强密码

- [ ] **SEC-4**: 应用 rate limiter 到所有端点
  - 文件: `src/cad-service/main.py`
  - 验证: @limiter.limit() 装饰器已添加

#### P1 - 核心功能

- [ ] **API-1**: 实现批量检测端点 `/api/v1/detect/batch`
  - 文件: `src/cad-service/api.py`, `src/cad-service/service.py`
  - 验证: POST 请求返回正确格式

- [ ] **API-2**: 实现异常解释端点 `/api/v1/explain/{txn_id}`
  - 文件: `src/cad-service/api.py`
  - 验证: GET 请求返回解释结果

- [ ] **API-3**: 实现反馈端点 `/api/v1/feedback`
  - 文件: `src/cad-service/api.py`
  - 验证: POST 反馈被持久化

- [ ] **MODEL-1**: 验证模型池 IForest/LOF/Graph 可用
  - 文件: `src/cad-model-pool/pool.py`
  - 验证: pytest 测试全部通过

- [ ] **MODEL-2**: 验证特征工厂生成特征
  - 文件: `src/cad-feature-engine/factory.py`
  - 验证: pytest 测试全部通过

- [ ] **MODEL-3**: 验证融合引擎 phase-based 权重
  - 文件: `src/cad-fusion-engine/engine.py`
  - 验证: gray/validation/stable 阶段权重正确

#### P2 - 质量保障

- [ ] **TEST-1**: 所有模块 pytest 通过率 ≥ 70%
  - 验证: `pytest src/*/tests -v --cov`

- [ ] **TEST-2**: CI 流水线 green
  - 文件: `.github/workflows/ci.yml`
  - 验证: GitHub Actions 全部通过

#### P3 - 部署就绪

- [ ] **DEPLOY-1**: Docker compose 验证
  - 验证: `docker compose -f docker/compose.dev.yml config`

- [ ] **DEPLOY-2**: Streamlit 控制台可启动
  - 验证: `streamlit run src/cad-console/main.py`

---

## 任务状态

| 任务ID | 状态 | 依赖 |
|--------|------|------|
| SEC-1 | ⏳ 待开始 | - |
| SEC-2 | ⏳ 待开始 | - |
| SEC-3 | ⏳ 待开始 | SEC-2 |
| SEC-4 | ⏳ 待开始 | - |
| API-1 | ⏳ 待开始 | SEC-1 |
| API-2 | ⏳ 待开始 | API-1 |
| API-3 | ⏳ 待开始 | API-1 |
| MODEL-1 | ⏳ 待开始 | - |
| MODEL-2 | ⏳ 待开始 | - |
| MODEL-3 | ⏳ 待开始 | MODEL-1, MODEL-2 |
| TEST-1 | ⏳ 待开始 | SEC-*, API-*, MODEL-* |
| TEST-2 | ⏳ 待开始 | TEST-1 |
| DEPLOY-1 | ⏳ 待开始 | - |
| DEPLOY-2 | ⏳ 待开始 | - |

---

## Gate 3 检查

- [x] 所有任务是竖切片（端到端功能）
- [x] 粒度符合标准（2-5分钟）
- [x] 依赖关系已标注
- [ ] 用户批准开始开发
