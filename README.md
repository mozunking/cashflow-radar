# 🔍 Cashflow Radar — Enterprise Capital Anomaly Detection

<div align="center">

[![Stars](https://img.shields.io/github/stars/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/stargazers)
[![Forks](https://img.shields.io/github/forks/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/network/members)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Build](https://github.com/mozunking/cashflow-radar/actions/workflows/ci.yml/badge.svg)](https://github.com/mozunking/cashflow-radar/actions)
[![Coverage](https://codecov.io/gh/mozunking/cashflow-radar/branch/main/graph/badge.svg)](https://codecov.io/gh/mozunking/cashflow-radar)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io/)

**English | [中文](README_zh.md)**

> **Open-source enterprise-grade capital anomaly detection system for financial risk control.**
> Detect hidden anomalies, circular fund transfers, and high-frequency trading patterns —
> all in one command.

**[Quick Start](#-quick-start)** · **[Features](#-features)** · **[Architecture](#-architecture)** · **[Demo](#-demo)** · **[Documentation](#-documentation)**

</div>

---

## 🤔 What is Cashflow Radar?

Cashflow Radar is an **open-source capital anomaly detection system** designed for financial institutions, fintech companies, and compliance teams. It leverages multiple anomaly detection algorithms (Isolation Forest, LOF, Graph-based Network Analysis) combined with a phase-based fusion engine to identify suspicious transactions that rule-based systems miss.

### Industry Use Cases

| Industry | Use Case |
|----------|----------|
| **Banking** | Detect circular fund transfers, shell company networks, and layering schemes |
| **Fintech** | Identify payment fraud, account takeover, and anomalous trading patterns |
| **E-commerce** | Spot fake reviews, abnormal order volumes, and payment fraud |
| **Insurance** | Discover claim fraud patterns and provider networks |
| **Securities** | Monitor insider trading, wash trading, and market manipulation |
| **Compliance** | Anti-money laundering (AML), KYC/KYB, and regulatory reporting |

---

## ✨ Features

### 🤖 Multi-Model Detection Engine

| Model | Algorithm | Best For | Explainability |
|-------|-----------|----------|----------------|
| **IForest** | Isolation Forest | Large single transactions, statistically unusual amounts | SHAP TreeExplainer |
| **LOF** | Local Outlier Factor | High-frequency trading, time-series anomalies | LIME |
| **Graph** | Network Analysis | Circular transfers, nested payment structures | Feature Ranking |

### 📊 Explainable AI

Every detection includes **business-contextual explanations** powered by SHAP and LIME. No more black-box alerts — understand exactly why a transaction was flagged.

### ⚡ Phase-Based Fusion Engine

Adaptive dual-engine architecture that combines rule-based and ML-based detection with phase-based weight tuning (Gray → Validation → Stable).

### 🔐 Enterprise Security

- **国密算法**: SM2/SM3/SM4 cryptographic compliance
- **等保2.0 Level 3**: Chinese cybersecurity compliance standard
- **JWT + SM2**: Multi-factor authentication
- **Rate Limiting**: Per-endpoint protection with SlowAPI

### 📈 Full Observability

- **Prometheus Metrics**: Real-time detection rates, model accuracy, latency
- **Grafana Dashboards**: Pre-built monitoring panels
- **Structured Logging**: python-json-logger with correlation IDs
- **Health Endpoints**: `/health`, `/health/degradation`

### 🧩 Modular Architecture

```
src/
├── cad-service/        # FastAPI backend (auth, api, models, service)
├── cad-console/        # Streamlit console (4 pages)
├── cad-data-quality/   # Data quality checker
├── cad-feature-engine/ # Feature factory (40+ features)
├── cad-model-pool/     # Model pool (IForest, LOF, Graph)
├── cad-fusion-engine/  # Phase-based fusion engine
├── cad-explainer/      # SHAP/LIME explainer
└── cad-degradation/   # Degradation manager
```

---

## 📖 Quick Start

### One-Command Demo

```bash
# Clone and start
git clone https://github.com/mozunking/cashflow-radar.git
cd cashflow-radar

# Start all services (PostgreSQL, Redis, MLflow, MinIO, API, Console)
docker compose -f docker/compose.dev.yml up -d

# Access the console at http://localhost:8501
open http://localhost:8501
```

### Manual Installation

```bash
# Prerequisites
pip install python>=3.11
docker with docker-compose

# Install dependencies
pip install -r src/requirements.txt

# Start infrastructure
docker compose -f docker/compose.dev.yml up -d postgres redis mlflow minio

# Run API
cd src && uvicorn cad_service.main:app --host 0.0.0.0 --port 8000

# Run Console (separate terminal)
cd src/cad-console && streamlit run main.py --server.port 8501
```

### Running Tests

```bash
# All modules
pytest src/*/tests -v

# With coverage
pytest src/*/tests --cov=src --cov-report=term-missing

# Specific module
pytest src/cad-model-pool/tests -v
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        CAD Console (Streamlit)                       │
│              Dashboard │ Detection │ Explain │ Feedback             │
│                    localhost:8501                                    │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ REST API (JWT/SM2 Auth)
┌────────────────────────────────▼─────────────────────────────────────┐
│                       CAD Service (FastAPI)                            │
│              localhost:8000 │ Rate Limited │ SSL/TLS                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ /detect   │  │ /explain   │  │ /feedback  │  │ /models        │  │
│  │ /batch    │  │ /{tx_id}   │  │            │  │ /health        │  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────┘  │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────┐
│                          CAD Core Engine                               │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ Data Quality │  │   Feature    │  │    Model     │                   │
│  │   Checker    │  │   Factory    │  │    Pool      │                   │
│  │              │  │  40+ feats   │  │ IForest/LOF  │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │    Fusion    │  │   Explain    │  │ Degradation │                   │
│  │   Engine     │  │   Engine     │  │   Manager   │                   │
│  │ Phase-based  │  │ SHAP/LIME    │  │ Fallback     │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘                   │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌─────────┐  ┌─────────┐  ┌─────────┐
              │PostgreSQL│  │  Redis  │  │  MLflow │
              │   DB    │  │  Cache  │  │ Model   │
              └─────────┘  └─────────┘  │ Registry│
                                        └─────────┘
```

---

## 📊 Supported Anomaly Types

| Type | Code | Description |
|------|------|-------------|
| Large Amount Anomaly | TYPE_01 | Transaction amount deviates significantly from account history |
| High-Frequency Trading | TYPE_02 | Abnormally high trading frequency within time window |
| Unknown Counterparty | TYPE_03 | Counterparty not in historical transaction network |
| Capital Flow Anomaly | TYPE_04 | Sudden balance changes or flow direction reversals |
| Composite Anomaly | TYPE_05 | Multiple anomaly patterns combined |
| Circular Transfer | TYPE_06 | Circular fund flows or nested payment structures |
| Structured Transactions | TYPE_07 | Multiple related transactions designed to evade reporting thresholds |
| Rapid Movement | TYPE_08 | Funds rapidly moving through multiple accounts |

---

## 🔍 Demo

### Dashboard View

![Dashboard](docs/images/dashboard.png)

### Detection Results

![Detection](docs/images/detection.png)

### Anomaly Explanation

![Explanation](docs/images/explanation.png)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Product Definition](docs/design/product.md) | Product overview, user stories, success metrics |
| [System Architecture](docs/design/architecture/SYSTEM_ARCHITECTURE.md) | System design, data flow |
| [Algorithm Design](docs/design/architecture/ALGORITHM_DESIGN.md) | Model details, fusion logic |
| [API Design](docs/design/architecture/API_DESIGN.md) | API reference, authentication |
| [Development Guide](docs/development/SK.md) | Setup, coding standards, PR workflow |
| [Deployment Guide](docs/deployment/SK.md) | Docker, Kubernetes, monitoring |

---

## 🧪 Testing & Quality

```bash
# Run all tests
pytest src/*/tests -v

# Coverage report
pytest src/*/tests --cov=src --cov-report=html --cov-report=term

# Code quality
black --check src/
isort --check-only src/
pyright src/
```

### Quality Gates

- All tests must pass
- Coverage ≥ 70%
- No P0/P1 bugs
- Security scan (bandit) with no high/severe issues

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest src/*/tests -v

# Commit (conventional commits)
git commit -m "feat: add new detection model"

# Push and create PR
git push origin feature/your-feature-name
```

---

## 🗺️ Roadmap

- [ ] **v1.1** - Real-time streaming detection with Kafka
- [ ] **v1.2** - Additional models (OC-SVM, AutoEncoder)
- [ ] **v1.3** - Graph neural network (GNN) based detection
- [ ] **v1.4** - Multi-tenancy support
- [ ] **v2.0** - Cloud-native deployment (Kubernetes operator)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

This project builds on excellent open-source libraries:

| Library | Purpose |
|---------|---------|
| [PyOD](https://github.com/yzhao062/pyod) | Outlier detection algorithms |
| [SHAP](https://github.com/slundberg/shap) | Model explainability |
| [MLflow](https://github.com/mlflow/mlflow) | Model lifecycle management |
| [Streamlit](https://github.com/streamlit/streamlit) | Data application framework |
| [FastAPI](https://github.com/tiangolo/fastapi) | Modern Python web framework |
| [gmssl](https://github.com/ganzhiyi/gmssl) | Chinese cryptographic library |

---

<div align="center">

**If this project helps you, please give us a ⭐**

[![Stars](https://img.shields.io/github/stars/mozunking/cashflow-radar?style=social)](https://github.com/mozunking/cashflow-radar/stargazers)

</div>