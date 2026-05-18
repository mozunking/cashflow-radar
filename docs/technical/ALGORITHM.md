# 算法技术方案

---

## 1. IForest（隔离森林）

### 原理
通过随机切分数据进行隔离，异常点更容易被早期隔离出来。

### 核心参数

```python
IForest(
    n_estimators=100,      # 树的数量
    max_samples='auto',   # 自动采样比例
    contamination=0.01,    # 污染率（异常比例）
    random_state=42,
    n_jobs=-1              # 充分利用CPU
)
```

### 适用特征
- amt_deviation（金额偏离度）
- amt_volatility（金额波动率）
- ix_xxx（交互特征）

---

## 2. LOF（局部离群因子）

### 原理
比较样本与其邻域的密度，密度远低于邻居的为异常点。

### 核心参数

```python
LOF(
    n_neighbors=20,        # 邻居数量
    algorithm='auto',      # 自动选择最优算法
    metric='minkowski',    # 距离度量
    contamination=0.01,
    n_jobs=-1
)
```

### 适用特征
- freq_daily/freq_weekly（频率特征）
- cp_stranger_ratio（陌生对手）

---

## 3. Graph（图网络异常检测）

### 原理
构建资金交易有向图，提取图特征后用IForest检测异常节点/边。

### 图特征

| 特征 | 计算方法 | 异常含义 |
|------|---------|---------|
| 度中心性 | nx.degree_centrality | 交易频繁程度 |
| PageRank | nx.pagerank | 资金流动重要性 |
| 出入度比 | in_degree/out_degree | 资金归集/分散模式 |
| 环路数 | nx.simple_cycles | 资金循环转账 |
| 社区偏离 | Louvain社区距离 | 异常社群归属 |

---

## 4. 模型对比

| 模型 | 精准率 | 召回率 | F1 | 解释器 |
|------|--------|--------|-----|--------|
| IForest | 0.85 | 0.79 | 0.82 | TreeExplainer |
| LOF | 0.78 | 0.74 | 0.76 | LIME |
| Graph | 0.72 | 0.76 | 0.74 | 特征排序 |
