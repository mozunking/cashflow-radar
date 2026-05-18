"""Dashboard Page - Real-time monitoring and anomaly detection overview."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/Users/hfy/cashflow-radar/src")
from cad_service.models import BatchDetectResponse


def show():
    """Render the dashboard page."""
    st.header("📊 Dashboard")
    st.markdown("Real-time monitoring and anomaly detection overview")

    # API configuration
    API_BASE = st.session_state.get("api_base", "http://localhost:8080/api/v1")

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", "12,847", "+1,234 today")
    with col2:
        st.metric("Anomalies Detected", "128", "+15 high risk")
    with col3:
        st.metric("Detection Rate", "99.2%", "+0.3%")
    with col4:
        st.metric("Avg Response Time", "45ms", "-12ms")

    st.divider()

    # Detection controls
    col_left, col_right = st.columns([1, 3])
    with col_left:
        st.subheader("Detection Controls")
        data_date = st.date_input(
            "Data Date",
            value=datetime.now().date() - timedelta(days=1),
            max_value=datetime.now().date(),
        )
        feature_version = st.text_input("Feature Version", value="v1.0.0")

        if st.button("🚀 Run Detection", type="primary", use_container_width=True):
            with st.spinner("Running batch detection..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/detect/batch",
                        json={"data_date": data_date.strftime("%Y-%m-%d"), "feature_version": feature_version},
                        timeout=30,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state["detection_result"] = result
                        st.success(f"Detection completed! Task ID: {result.get('task_id', 'N/A')}")
                    else:
                        st.error(f"API error: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend service not available. Displaying demo data.")
                    st.session_state["detection_result"] = _get_demo_data()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Detection results
    result = st.session_state.get("detection_result", _get_demo_data())

    with col_right:
        st.subheader("Detection Results")
        if result:
            tabs = st.tabs(["Overview", "Risk Distribution", "Transaction List"])

            with tabs[0]:
                _render_overview(result)
            with tabs[1]:
                _render_risk_distribution(result)
            with tabs[2]:
                _render_transaction_list(result)

    st.divider()

    # Model status section
    st.subheader("🤖 Model Status")
    _render_model_status()

    st.divider()

    # Degradation status
    st.subheader("📉 Degradation Status")
    _render_degradation_status()


def _render_overview(result: dict):
    """Render overview metrics."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("High Risk", result.get("high_risk", 0), delta="需要关注")
    with col2:
        st.metric("Medium Risk", result.get("medium_risk", 0))
    with col3:
        st.metric("Low Risk", result.get("low_risk", 0))


def _render_risk_distribution(result: dict):
    """Render risk distribution chart."""
    data = {
        "Risk Level": ["高风险", "中风险", "低风险"],
        "Count": [
            result.get("high_risk", 0),
            result.get("medium_risk", 0),
            result.get("low_risk", 0),
        ],
    }
    df = pd.DataFrame(data)

    fig = px.pie(
        df,
        values="Count",
        names="Risk Level",
        color="Risk Level",
        color_discrete_map={"高风险": "#ff4b4b", "中风险": "#ffa500", "低风险": "#00cc96"},
        hole=0.4,
    )
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def _render_transaction_list(result: dict):
    """Render transaction list table."""
    transactions = result.get("results", [])
    if not transactions:
        st.info("No transactions to display")
        return

    df = pd.DataFrame(transactions)
    display_df = df[["transaction_id", "account_id", "amount" if "amount" in df.columns else "final_score", "risk_level", "final_score"]].copy()
    display_df.columns = ["Transaction ID", "Account ID", "Amount/Score", "Risk Level", "Final Score"]

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=250)


def _render_model_status():
    """Render model status table."""
    models = [
        {"name": "iForest", "version": "1.0.0", "status": "active", "f1": 0.82},
        {"name": "LOF", "version": "1.0.0", "status": "active", "f1": 0.76},
        {"name": "Graph", "version": "1.0.0", "status": "active", "f1": 0.74},
    ]
    df = pd.DataFrame(models)

    def status_color(s):
        color = "#00cc96" if s == "active" else "#ff4b4b" if s == "inactive" else "#ffa500"
        return f":{color}[{s}]"

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    for idx, row in df.iterrows():
        with col1:
            st.text(f"**{row['name']}** (v{row['version']})")
        with col2:
            st.markdown(f"Status: {status_color(row['status'])}")
        with col3:
            st.metric("F1", f"{row['f1']:.2f}")
        with col4:
            if st.button("Details", key=f"model_{idx}"):
                st.info(f"Model {row['name']} details would appear here")


def _render_degradation_status():
    """Render degradation status."""
    st.success("All systems operational - No degradation detected")

    with st.expander("View detailed degradation metrics"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("Degraded Models: None")
            st.write("Fail Count: 0 / 3 threshold")
        with col2:
            st.write("Current Level: Normal")
            st.write("Last Check: Just now")


def _get_demo_data() -> dict:
    """Return demo detection data when backend is unavailable."""
    return {
        "task_id": "demo_task_001",
        "total_count": 100,
        "anomaly_count": 23,
        "high_risk": 8,
        "medium_risk": 15,
        "low_risk": 77,
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "transaction_id": f"TXN{i:06d}",
                "account_id": f"ACC{i % 10:04d}",
                "rule_hit": i % 5 == 0,
                "rule_score": 85.0 if i % 5 == 0 else 0.0,
                "algo_score": 72.5,
                "final_score": 75.0 + (i % 20),
                "risk_level": "高风险" if i % 10 < 3 else "中风险" if i % 10 < 6 else "低风险",
                "anomaly_type": "TYPE_01",
                "model_scores": {"iforest": 0.8, "lof": 0.75, "graph": 0.72},
            }
            for i in range(20)
        ],
    }


if __name__ == "__main__":
    show()
