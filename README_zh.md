# 🔍 Cashflow Radar — 企业级资金异常检测系统

<div align="center">

[![Stars](https://img.shields.io/github/stars/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/stargazers)
[![Forks](https://img.shields.io/github/forks/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/network/members)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Build](https://github.com/mozunking/cashflow-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/mozunking/cashflow-radar/actions)

**English | 中文**

> **开源企业级资金异常检测系统，专为金融风控设计。**
> 检测隐藏异常、洗钱交易、高频交易模式 — 一键启动。

**[快速开始](#-快速开始)** · **[功能特性](#-功能特性)** · **[系统架构](#-系统架构)** · **[文档](#-文档)**

</div>

---

## 🤔 什么是 Cashflow Radar？

Cashflow Radar 是一款**开源企业级资金异常检测系统**，专为金融机构、金融科技公司和合规团队设计。它结合多种异常检测算法（Isolation Forest、LOF、基于图的网络分析）和基于阶段的融合引擎，识别传统规则系统无法发现的可疑交易。

### 行业应用场景

| 行业 | 应用场景 |
|------|----------|
| **银行业** | 检测循环转账、空壳公司网络、层层嵌套的资金流动 |
| **金融科技** | 识别支付欺诈、账户盗用、异常交易模式 |
| **电子商务** | 发现虚假交易、异常订单量、支付欺诈 |
| **保险业** | 发现欺诈理赔模式和关联提供商网络 |
| **证券业** | 监测内幕交易、对倒交易、市场操纵行为 |
| **合规部门** | 反洗钱 (AML)、KYC/KYB、监管报告 |

---

## ✨ 功能特性

### 🤖 多模型检测引擎

| 模型 | 算法 | 适用于 | 可解释性 |
|------|------|--------|----------|
| **IForest** | 隔离森林 | 大额单笔交易、统计异常金额 | SHAP TreeExplainer |
| **LOF** | 局部异常因子 | 高频交易、时间序列异常 | LIME |
| **Graph** | 网络分析 | 循环转账、嵌套支付结构 | 特征重要性排序 |

### 📊 可解释人工智能

每次检测都包含由 SHAP 和 LIME 提供支持的**业务上下文解释**。不再有黑盒告警。

### ⚡ 基于阶段的融合引擎

自适应双引擎架构，结合基于规则的检测和基于ML的检测，具有阶段性权重调优（灰度 → 验证 → 稳定）。

### 🔐 企业级安全

- **国密算法**: SM2/SM3/SM4 密码学合规
- **等保2.0三级**: 中国网络安全合规标准
- **JWT + SM2**: 多因素认证
- **限流保护**: 基于 SlowAPI 的每个端点保护

---

## 📖 快速开始

```bash
git clone https://github.com/mozunking/cashflow-radar.git
cd cashflow-radar
docker compose -f docker/compose.dev.yml up -d
open http://localhost:8501
```

---

## 🗺️ 路线图

- [ ] **v1.1** - 基于 Kafka 的实时流式检测
- [ ] **v1.2** - 补充模型（OC-SVM、AutoEncoder）
- [ ] **v1.3** - 基于图神经网络的检测
- [ ] **v2.0** - 云原生部署（Kubernetes Operator）

---

## 📄 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。

<div align="center">

**如果本项目对您有帮助，请给我们一个 ⭐**

[![Stars](https://img.shields.io/github/stars/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/stargazers)

</div>
