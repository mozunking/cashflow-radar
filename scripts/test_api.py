#!/usr/bin/env python3
"""Test the CAD API endpoints.

Usage:
    python scripts/test_api.py [--base-url http://localhost:8000]
"""
import argparse
import requests


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    resp = requests.get(f"{BASE_URL}/health")
    resp.raise_for_status()
    data = resp.json()
    print(f"✓ Health check: {data['status']} (v{data['version']})")
    return data


def test_batch_detect():
    """Test batch detect endpoint."""
    resp = requests.post(
        f"{BASE_URL}/api/v1/detect/batch",
        json={"data_date": "2026-05-17"}
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"✓ Batch detect: {data['total_count']} transactions, {data['anomaly_count']} anomalies")
    print(f"  High risk: {data['high_risk']}, Medium: {data['medium_risk']}, Low: {data['low_risk']}")
    return data


def test_explain(txn_id: str = "TXN000001"):
    """Test explain endpoint."""
    resp = requests.get(f"{BASE_URL}/api/v1/explain/{txn_id}")
    resp.raise_for_status()
    data = resp.json()
    print(f"✓ Explain transaction {txn_id}:")
    print(f"  Type: {data['anomaly_type']} ({data['anomaly_type_desc']})")
    print(f"  Top feature: {data['top_features'][0]['feature_name']}")
    return data


def test_models():
    """Test models listing."""
    resp = requests.get(f"{BASE_URL}/api/v1/models")
    resp.raise_for_status()
    data = resp.json()
    print(f"✓ Available models: {len(data)}")
    for m in data:
        print(f"  - {m['name']} {m['version']}: F1={m['metrics'].get('f1', 'N/A')}")
    return data


def test_degradation():
    """Test degradation status."""
    resp = requests.get(f"{BASE_URL}/api/v1/health/degradation")
    resp.raise_for_status()
    data = resp.json()
    print(f"✓ Degradation status: {data['level']} ({data['level_desc']})")
    if data['degraded']:
        print(f"  Degraded models: {data['degraded']}")
    return data


def main():
    parser = argparse.ArgumentParser(description="Test CAD API")
    parser.add_argument("--base-url", default=BASE_URL, help="API base URL")
    global BASE_URL
    BASE_URL = parser.parse_args().base_url
    
    print("=" * 50)
    print("CAD API Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_batch_detect()
        test_explain()
        test_models()
        test_degradation()
        print("\n" + "=" * 50)
        print("All tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
