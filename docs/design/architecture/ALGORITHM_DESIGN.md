# 算法设计

**文档编号**：CAD-DS-V10 | **版本**：10.0 | **日期**：2026-05-18

---

## 3.1 模型池（首期3模型）

### 3.1.1 IForest——静态异常筛查

适用：单笔大额、非常规金额、陌生往来单位交易。开源实现：PyOD。

```python
from pyod.models.iforest import IForest
model = IForest(n_estimators=100, max_samples='auto', contamination=0.01,
                random_state=42, n_jobs=-1)
```

专用解释器：`shap.TreeExplainer`（比KernelExplainer快100-1000倍）。

### 3.1.2 LOF——密度异常筛查

适用：短期高频、密集划转、拆分转账。开源实现：PyOD。

```python
from pyod.models.lof import LOF
model = LOF(n_neighbors=20, algorithm='auto', metric='minkowski',
            contamination=0.01, n_jobs=-1)
```

专用解释器：LIME（LOF无决策树结构，TreeExplainer不适用）。

### 3.1.3 Graph——图/网络异常检测

适用：资金循环转账、多层嵌套划转、归集-分散模式。开源实现：NetworkX + PyOD IForest。

图特征（6个）：

| 编码 | 名称 | 计算 |
|------|------|------|
| graph_degree_centrality | 度中心性 | nx.degree_centrality |
| graph_pagerank | PageRank | nx.pagerank(max_iter=50, tol=1e-2) |
| graph_in_out_ratio | 出入度比 | in_degree/max(out_degree,1) |
| graph_fund_concentration | 资金归集分散系数 | out_total/(in_total+1) |
| graph_cycle_count | 资金环路数 | 限制深度局部检测 |
| graph_community_deviation | 社区归属偏差 | 节点与主社区中心距离 |

---

## 3.2 融合引擎

**规则一票否决 + 算法增量挖掘 + 分阶段权重**：

```python
class FusionEngine:
    PHASE_W = {
        'gray': (0.85, 0.15),        # 灰度期：算法仅观察
        'validation': (0.70, 0.30),   # 验证期：人工复核
        'stable': (0.60, 0.40)        # 稳定期：同等对待
    }
    ALGO_W_V1 = {'iforest': 0.45, 'lof': 0.30, 'graph': 0.25}
    THRESH = {'high': 80, 'medium': 60}
```

**分阶段权重策略**：

| 上线阶段 | 规则权重 | 算法权重 | 算法作用 | 持续时间 | 准入标准 |
|---------|---------|---------|---------|---------|---------|
| 灰度期 | 0.85 | 0.15 | 仅记录，不触发预警 | ≥6周 | 服务可用率>99.5% |
| 验证期 | 0.70 | 0.30 | 人工复核 | ≥8周 | 算法独立价值≥5条/周，误报率<30% |
| 稳定期 | 0.60 | 0.40 | 同等对待 | 长期 | F1>0.75，漂移特征<5% |

---

## 3.3 解释引擎

**异常类型体系**：

| 代码 | 名称 | 判定规则 | 业务语义描述 |
|------|------|---------|-------------|
| TYPE_01 | 大额异常交易 | 金额类特征贡献>40% | 交易金额显著偏离账户历史行为 |
| TYPE_02 | 高频密集交易 | 频率类特征贡献>40% | 账户近期交易频率显著升高 |
| TYPE_03 | 陌生对手交易 | 对手类特征贡献>40% | 交易对手方与历史习惯不符 |
| TYPE_04 | 资金异动 | 时序/账户类贡献>40% | 账户资金流向出现异常变动 |
| TYPE_05 | 复合型异常 | 多类均衡 | 多个维度同时异常 |
| TYPE_06 | 资金链路异常 | 图特征贡献>40% | 资金链路存在循环或嵌套结构 |

**按模型分配解释器**：

| 模型 | 解释器 | 原因 |
|------|--------|------|
| IForest | `shap.TreeExplainer` | 速度快100-1000倍 |
| LOF | LIME | 无决策树结构 |
| Graph | 特征贡献排序 | 图特征维度少 |

---

## 3.4 降级管理器

| 降级级别 | 说明 | 触发条件 |
|---------|------|---------|
| full | 全部正常 | - |
| partial | 部分降级 | <3个模型降级 |
| rules_only | 仅规则 | ≥3个模型降级 |
| blocked | 完全阻断 | 连续失败超阈值 |

---

## 3.5 特征清单（5类40个）

### 交易金额特征（8个）

| 编码 | 名称 | 公式 |
|------|------|------|
| amt_deviation | 交易金额与历史均值偏离度 | (单笔-均值)/均值 |
| amt_industry_dev | 交易金额与同行业均值偏离度 | (单笔-行业均值)/行业均值 |
| amt_threshold_proximity | 大额交易标准接近度 | max(1-\|金额-50万\|/50万, 1-\|金额-200万\|/200万) |
| amt_tail_pattern | 金额尾数特征 | 整数=1, 重复尾数=0.5, 其他=0 |
| amt_daily_total | 单日累计金额 | 当日同账户累计 |
| amt_weekly_total | 单周累计金额 | 当周同账户累计 |
| amt_monthly_total | 单月累计金额 | 当月同账户累计 |
| amt_volatility | 金额波动率 | 近30天std/mean |

### 交易频率特征（7个）

| 编码 | 名称 | 公式 |
|------|------|------|
| freq_daily | 单日交易次数 | 当日同账户笔数 |
| freq_weekly | 单周交易次数 | 当周同账户笔数 |
| freq_monthly | 单月交易次数 | 当月同账户笔数 |
| freq_same_counterparty | 相同对手交易频率 | 近90天与同一对手次数 |
| freq_interval_std | 交易时间间隔标准差 | 近30天间隔std |
| freq_holiday_ratio | 节假日交易占比 | 近90天节假日笔数占比 |
| freq_off_hours_ratio | 非工作时间交易占比 | 近90天22-06点笔数占比 |

### 交易对手特征（9个）

| 编码 | 名称 | 公式 |
|------|------|------|
| cp_stranger_ratio | 陌生对手占比 | 近90天首次交易对手数/总对手数 |
| cp_high_risk_region | 高风险地区对手占比 | 高风险地区对手笔数占比 |
| cp_related_party | 关联企业交易占比 | 关联企业金额占比 |
| cp_business_match | 对手经营范围匹配度 | 行业代码匹配(0-1) |
| cp_age | 对手成立时间 | 成立天数 |
| cp_capital_ratio | 对手注册资本交易比 | 交易金额/对手注册资本 |
| cp_concentration | 单一对手金额集中度 | 最大对手金额/总金额 |
| cp_change_freq | 对手变更频率 | 近90天新增对手数/总对手数 |
| cp_cash_ratio | 现金交易占比 | 现金笔数/总笔数 |

### 时序与账户特征（8个）

| 编码 | 名称 | 公式 |
|------|------|------|
| acct_balance_change | 余额突增突降幅度 | (当前-前日)/\|前日\| |
| acct_inflow_outflow | 流入流出比 | 流入/流出 |
| acct_scatter_in | 分散转入集中转出系数 | 转入笔数/转出笔数 |
| acct_scatter_out | 集中转入分散转出系数 | 转出笔数/转入笔数 |
| acct_dormant_activation | 闲置账户突然启用 | 闲置>90天后首笔=1 |
| acct_age_activity | 开户时间活跃度关系 | 开户天数/近30天笔数 |
| acct_cross_bank | 跨行划转频率 | 跨行笔数/总笔数 |
| acct_cross_border | 跨境交易占比 | 跨境金额占比 |

### 交互特征（8个）

| 编码 | 名称 | 公式 |
|------|------|------|
| ix_amt_off_hours | 大额非工作时间交易 | amt_deviation>2且freq_off_hours_ratio>0.3 |
| ix_stranger_freq | 陌生对手高频交易系数 | cp_stranger_ratio×freq_daily |
| ix_cp_amt_concentrate | 单一对手大额集中系数 | cp_concentration×amt_deviation |
| ix_balance_low_outflow | 余额低位集中转出系数 | (1/余额百分位)×acct_scatter_out |
| ix_volatility_cp_change | 金额波动对手变更系数 | amt_volatility×cp_change_freq |
| ix_amt_cross_border | 大额跨境交易标识 | (amt_deviation>1.5)×acct_cross_border |
| ix_related_freq | 关联企业高频交易系数 | cp_related_party×freq_same_counterparty |
| ix_dormant_large | 闲置启用大额交易系数 | acct_dormant_activation×amt_deviation |
