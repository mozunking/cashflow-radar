# 🔍 CAD - Capital Anomaly Detection

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red.svg)](https://streamlit.io/)

> Enterprise-grade capital anomaly detection system for financial risk control.
> Detects hidden anomalies, circular fund transfers, and high-frequency trading patterns
> that rule-based systems cannot find.

## ✨ Features

- **🔬 Multi-Model Detection**: IForest, LOF, and Graph-based anomaly detection
- **📊 Explainable AI**: SHAP/LIME-powered feature attribution with business semantics
- **⚡ Real-time Processing**: T+1 batch detection with sub-second explanation response
- **🔄 Adaptive Fusion**: Rule + Algorithm dual-engine with phase-based weight tuning
- **🛡️ Enterprise Security**: 国密算法 (SM2/SM3/SM4), 等保2.0 Level 3 compliant
- **📈 Full Observability**: Prometheus metrics, Grafana dashboards, structured logging

## 📦 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/mozunking/cashflow-radar.git
cd cashflow-radar

# Start all services
docker compose -f docker/compose.dev.yml up -d

# Access the console
open http://localhost:8501
```

### Manual Installation

```bash
# Install dependencies
pip install -r src/requirements.txt

# Start services
docker compose -f docker/compose.dev.yml up -d postgres redis mlflow minio

# Run the API server
cd src
uvicorn cad_service.main:app --host 0.0.0.0 --port 8000

# In another terminal, run the console
cd src
streamlit run cad_console/main.py --server.port 8501
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    CAD Console (Streamlit)           │
│                 localhost:8501                        │
└──────────────────────┬───────────────────────────────┘
                       │ REST API
┌──────────────────────▼───────────────────────────────┐
│                  CAD Service (FastAPI)               │
│                 localhost:8000                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ Detect API │ │ Explain API │ │Feedback API│      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│                    CAD Core                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │  Quality  │ │  Feature  │ │   Model   │           │
│  │  Checker  │ │  Factory  │ │   Pool    │           │
│  └────────────┘ └────────────┘ └────────────┘           │
│  ┌────────────┐ ┌────────────┐                        │
│  │   Fusion  │ │  Explain   │                        │
│  │   Engine  │ │   Engine   │                        │
│  └────────────┘ └────────────┘                        │
└─────────────────────────────────────────────────────┘
```

## 📊 Supported Models

| Model | Algorithm | Best For | Explainer |
|-------|-----------|----------|-----------|
| IForest | Isolation Forest | Large single transactions | SHAP TreeExplainer |
| LOF | Local Outlier Factor | High-frequency trading | LIME |
| Graph | Network Analysis | Circular transfers, nested patterns | Feature ranking |

## 🎯 Anomaly Types

| Type | Code | Description |
|------|------|-------------|
| 大额异常交易 | TYPE_01 | Transaction amount deviates significantly from account history |
| 高频密集交易 | TYPE_02 | Abnormally high trading frequency |
| 陌生对手交易 | TYPE_03 | Counterparty not in historical transaction network |
| 资金异动 | TYPE_04 | Sudden balance changes or flow anomalies |
| 复合型异常 | TYPE_05 | Multiple anomaly patterns combined |
| 资金链路异常 | TYPE_06 | Circular transfers or nested payment structures |

## 📖 Documentation

- [Product Definition](docs/design/product.md) - Product overview, user stories
- [System Architecture](docs/design/architecture/SYSTEM_ARCHITECTURE.md) - Architecture details
- [Algorithm Design](docs/design/architecture/ALGORITHM_DESIGN.md) - Model details
- [API Documentation](docs/design/architecture/API_DESIGN.md) - API reference
- [Development Guide](docs/development/SK.md) - Development workflow
- [Deployment Guide](docs/deployment/SK.md) - Deployment and operations

## 🧪 Testing

```bash
# Run all tests
pytest src/*/tests -v

# Run with coverage
pytest src/*/tests --cov=src --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

This project builds on excellent open-source libraries:
- [PyOD](https://github.com/yzhao062/pyod) - Outlier detection
- [SHAP](https://github.com/slundberg/shap) - Model explainability
- [MLflow](https://github.com/mlflow/mlflow) - Model lifecycle management
- [Streamlit](https://github.com/streamlit/streamlit) - Data apps framework
