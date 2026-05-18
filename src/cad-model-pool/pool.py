"""Model Pool for CAD

包含三个异常检测模型：
- IForest: 隔离森林，适用于单笔大额、非常规金额
- LOF: 局部离群因子，适用于短期高频、密集划转
- Graph: 图网络异常检测，适用于资金环路、多层嵌套
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from pyod.models.iforest import IForest
from pyod.models.lof import LOF


@dataclass
class ModelOutput:
    model_name: str
    model_version: str
    anomaly_score: float
    anomaly_flag: bool
    contamination: float
    inference_time_ms: float


class ModelPool:
    """模型池"""

    def __init__(self, contamination: float = 0.01):
        self.contamination = contamination
        self.iforest = IForest(
            n_estimators=100,
            max_samples="auto",
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        self.lof = LOF(
            n_neighbors=20,
            algorithm="auto",
            metric="minkowski",
            contamination=contamination,
            n_jobs=-1
        )
        self.graph_detector: Any = None
        self._fitted = False

    def fit(self, features: pd.DataFrame) -> "ModelPool":
        """训练全部模型"""
        feature_df = features.select_dtypes(include=[np.number]).fillna(0)

        self.iforest.fit(feature_df)
        self.lof.fit(feature_df)

        # Graph detector will be set externally
        self._fitted = True
        return self

    def decision_function(self, features: pd.DataFrame) -> dict[str, np.ndarray]:
        """返回各模型异常分数"""
        if not self._fitted:
            raise RuntimeError("Models not fitted. Call fit() first.")

        feature_df = features.select_dtypes(include=[np.number]).fillna(0)

        return {
            "iforest": self.iforest.decision_function(feature_df),
            "lof": self.lof.decision_function(feature_df),
        }

    def get_model_scores(self, features: pd.DataFrame) -> dict[str, float]:
        """返回单个样本的各模型分数"""
        scores = self.decision_function(features)
        return {name: float(scores[name][0]) for name in scores}

    def get_model_output(self, features: pd.DataFrame) -> list[ModelOutput]:
        """返回ModelOutput列表"""
        scores = self.decision_function(features)
        results = []

        for name, score_arr in scores.items():
            score = float(score_arr[0])
            feat_for_pred = features.select_dtypes(include=[np.number]).fillna(0)
            pred_input = feat_for_pred.iloc[[0]]
            if name == "iforest":
                anomaly_flag = bool(self.iforest.predict(pred_input)[0])
            elif name == "lof":
                anomaly_flag = bool(self.lof.predict(pred_input)[0])
            else:
                anomaly_flag = False
            results.append(ModelOutput(
                model_name=name,
                model_version="1.0.0",
                anomaly_score=score,
                anomaly_flag=anomaly_flag,
                contamination=self.contamination,
                inference_time_ms=0.0
            ))

        if self.graph_detector is not None:
            graph_scores = self.graph_detector.decision_function(
                features.select_dtypes(include=[np.number]).fillna(0)
            )
            results.append(ModelOutput(
                model_name="graph",
                model_version="1.0.0",
                anomaly_score=float(graph_scores[0]),
                anomaly_flag=False,
                contamination=self.contamination,
                inference_time_ms=0.0
            ))

        return results


class GraphAnomalyDetector:
    """资金交易图谱异常检测器，基于NetworkX+PyOD"""

    def __init__(self, contamination: float = 0.01, max_nodes: int = 100000):
        self.iforest = IForest(
            contamination=contamination,
            n_estimators=100,
            random_state=42
        )
        self.G = None
        self.community_map = None
        self.max_nodes = max_nodes

    def build_graph(self, df: pd.DataFrame) -> "GraphAnomalyDetector":
        """从交易数据构建图"""
        import networkx as nx

        if len(df) > self.max_nodes:
            df = df.sample(n=self.max_nodes, random_state=42)

        self.G = nx.DiGraph()
        for _, r in df.iterrows():
            if "payer_id" in r and "payee_id" in r:
                self.G.add_edge(r["payer_id"], r["payee_id"],
                              weight=r.get("amount", 1.0))

        if self.G.number_of_nodes() > 0:
            try:
                self.community_map = nx.community.louvain_communities(
                    self.G.to_undirected(), seed=42
                )
            except Exception:
                self.community_map = None

        return self

    def extract_node_features(self, node_id: str) -> dict[str, float]:
        """提取节点图特征"""
        import networkx as nx

        if self.G is None or node_id not in self.G:
            return {k: 0.0 for k in [
                "graph_degree_centrality", "graph_pagerank",
                "graph_in_out_ratio", "graph_fund_concentration",
                "graph_cycle_count", "graph_community_deviation"
            ]}

        in_d = self.G.in_degree(node_id)
        out_d = self.G.out_degree(node_id)
        in_t = sum(d["weight"] for _, _, d in self.G.in_edges(node_id, data=True))
        out_t = sum(d["weight"] for _, _, d in self.G.out_edges(node_id, data=True))

        try:
            communities = list(self.community_map) if self.community_map else []
            comm_dev = self._comm_dev(node_id, communities)
        except Exception:
            comm_dev = 0.0

        try:
            deg_cent = nx.degree_centrality(self.G).get(node_id, 0)
        except Exception:
            deg_cent = 0.0

        try:
            pagerank = nx.pagerank(self.G, max_iter=50, tol=1e-2).get(node_id, 0)
        except Exception:
            pagerank = 0.0

        return {
            "graph_degree_centrality": float(deg_cent),
            "graph_pagerank": float(pagerank),
            "graph_in_out_ratio": float(in_d / max(out_d, 1)),
            "graph_fund_concentration": float(out_t / (in_t + 1)),
            "graph_cycle_count": 0.0,
            "graph_community_deviation": comm_dev
        }

    def _comm_dev(self, nid: str, communities: list) -> float:
        if not communities:
            return 0.0
        for comm in communities:
            if nid in comm:
                degs = [self.G.degree(n) for n in comm if n in self.G]
                avg = np.mean(degs) if degs else 0
                return abs(self.G.degree(nid) - avg) / max(avg, 1)
        return 0.0

    def fit(self, feat_df: pd.DataFrame) -> "GraphAnomalyDetector":
        self.iforest.fit(feat_df)
        return self

    def decision_function(self, feat_df: pd.DataFrame) -> np.ndarray:
        return self.iforest.decision_function(feat_df)
