#!/bin/bash
# Demo script for cashflow-radar

set -e

echo "=========================================="
echo "  CAD - Capital Anomaly Detection Demo"
echo "=========================================="
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed."; exit 1; }

echo "[1/4] Starting services..."
docker compose -f docker/compose.dev.yml up -d
echo ""

echo "[2/4] Waiting for services to be ready..."
sleep 10
echo ""

echo "[3/4] Checking API health..."
curl -s http://localhost:8000/health || echo "API not ready yet"
echo ""

echo "[4/4] Services started successfully!"
echo ""
echo "=========================================="
echo "  Access Points:"
echo "  - API:    http://localhost:8000"
echo "  - Console: http://localhost:8501"
echo "  - MLflow: http://localhost:5000"
echo "  - Grafana: http://localhost:3000"
echo "=========================================="
