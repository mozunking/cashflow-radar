"""Deployment Page - Model deployment and configuration management."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime


def show():
    """Render the deployment page."""
    st.header("🚀 Deployment")
    st.markdown("Model deployment and configuration management")

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Model Registry", "🔄 Pipelines", "⚙️ Configuration", "📜 Deployment History"])

    with tab1:
        _render_model_registry()
    with tab2:
        _render_pipelines()
    with tab3:
        _render_configuration()
    with tab4:
        _render_history()


def _render_model_registry():
    """Render model registry section."""
    st.subheader("Model Registry")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh Models", use_container_width=True):
            st.cache_data.clear()
    with col2:
        st.selectbox("Filter by Status", ["All", "Active", "Archived", "Staging"])
    with col3:
        st.selectbox("Sort by", ["Name", "Version", "F1 Score", "Last Updated"])

    # Model cards
    models = [
        {"name": "iForest", "version": "1.0.0", "status": "Active", "f1": 0.82, "deployed_at": "2024-01-15"},
        {"name": "LOF", "version": "1.0.0", "status": "Active", "f1": 0.76, "deployed_at": "2024-01-15"},
        {"name": "Graph", "version": "1.0.0", "status": "Active", "f1": 0.74, "deployed_at": "2024-01-15"},
        {"name": "iForest", "version": "1.1.0", "status": "Staging", "f1": 0.85, "deployed_at": "2024-03-01"},
        {"name": "AutoEncoder", "version": "0.9.0", "status": "Archived", "f1": 0.71, "deployed_at": "2023-11-20"},
    ]

    for i, model in enumerate(models):
        with st.container():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"**{model['name']}** (v{model['version']})")
                st.caption(f"Deployed: {model['deployed_at']}")
            with col_b:
                status_color = "green" if model["status"] == "Active" else "orange" if model["status"] == "Staging" else "gray"
                st.markdown(f"Status: :{status_color}[{model['status']}]")
            with col_c:
                st.metric("F1", f"{model['f1']:.2f}")

            col_d, col_e, col_f = st.columns(3)
            with col_d:
                if st.button("Deploy", key=f"deploy_{i}"):
                    st.success(f"Deploying {model['name']} v{model['version']}...")
            with col_e:
                if st.button("View Details", key=f"details_{i}"):
                    st.info("Details panel would open")
            with col_f:
                if st.button("Archive", key=f"archive_{i}"):
                    st.warning(f"Archive {model['name']}?")

            st.divider()

    # Upload new model
    st.subheader("Upload New Model")
    with st.form("upload_model"):
        col1, col2 = st.columns(2)
        with col1:
            model_name = st.text_input("Model Name")
            model_version = st.text_input("Version", placeholder="e.g., 1.2.0")
        with col2:
            model_type = st.selectbox("Model Type", ["iForest", "LOF", "Graph", "AutoEncoder", "Ensemble"])
            upload_file = st.file_uploader("Model File", type=["pkl", "onnx", "h5"])

        submitted = st.form_submit_button("Upload Model", type="primary")
        if submitted:
            if model_name and model_version and upload_file:
                st.success(f"Model {model_name} v{model_version} uploaded successfully!")
            else:
                st.error("Please fill in all required fields")


def _render_pipelines():
    """Render pipelines section."""
    st.subheader("CI/CD Pipelines")

    pipelines = [
        {"name": "detection_pipeline", "status": "success", "last_run": "2 min ago", "duration": "45s"},
        {"name": "training_pipeline", "status": "success", "last_run": "1 hour ago", "duration": "12m"},
        {"name": "validation_pipeline", "status": "running", "last_run": "Just now", "duration": "-"},
        {"name": "deployment_pipeline", "status": "failed", "last_run": "3 hours ago", "duration": "1m 23s"},
    ]

    for i, pipeline in enumerate(pipelines):
        status_icon = "✅" if pipeline["status"] == "success" else "🔄" if pipeline["status"] == "running" else "❌"
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.markdown(f"{status_icon} **{pipeline['name']}**")
            with col2:
                st.caption(f"Last: {pipeline['last_run']}")
            with col3:
                st.caption(f"Duration: {pipeline['duration']}")
            with col4:
                if st.button("Run", key=f"run_{i}"):
                    st.info(f"Triggering {pipeline['name']}...")
            st.divider()

    if st.button("➕ Create New Pipeline", type="primary"):
        st.info("Pipeline creation dialog would open")


def _render_configuration():
    """Render configuration section."""
    st.subheader("System Configuration")

    with st.expander("Detection Settings", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("High Risk Threshold", value=75.0, min_value=0.0, max_value=100.0, step=5.0)
            st.number_input("Medium Risk Threshold", value=50.0, min_value=0.0, max_value=100.0, step=5.0)
            st.number_input("Min Transaction Amount", value=1000.0, step=100.0)
        with col2:
            st.number_input("Contamination Rate", value=0.01, min_value=0.0, max_value=0.5, step=0.005, format="%.3f")
            st.number_input("Batch Size", value=10000, step=1000)
            st.selectbox("Fusion Phase", ["gray", "white", "black"])

    with st.expander("Model Configuration"):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("iForest n_estimators", value=100, min_value=10, max_value=500)
            st.number_input("LOF n_neighbors", value=20, min_value=5, max_value=100)
        with col2:
            st.number_input("Graph k_neighbors", value=15, min_value=5, max_value=50)
            st.slider("Feature Importance Threshold", 0.0, 1.0, 0.3)

    with st.expander("Alert Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.toggle("Enable Email Alerts")
            st.toggle("Enable Slack Alerts")
        with col2:
            st.toggle("Enable Webhook Notifications")
            st.text_input("Webhook URL", placeholder="https://...")

    if st.button("💾 Save Configuration", type="primary", use_container_width=True):
        st.success("Configuration saved successfully!")


def _render_history():
    """Render deployment history."""
    st.subheader("Deployment History")

    history = [
        {"id": "DEPL_001", "model": "iForest v1.0.0", "action": "Deploy", "status": "Success", "deployed_by": "admin", "timestamp": "2024-03-15 14:30"},
        {"id": "DEPL_002", "model": "LOF v1.0.0", "action": "Deploy", "status": "Success", "deployed_by": "admin", "timestamp": "2024-03-15 14:25"},
        {"id": "DEPL_003", "model": "Graph v1.0.0", "action": "Rollback", "status": "Success", "deployed_by": "admin", "timestamp": "2024-03-14 10:00"},
        {"id": "DEPL_004", "model": "iForest v0.9.0", "action": "Archive", "status": "Success", "deployed_by": "admin", "timestamp": "2024-03-10 09:15"},
    ]

    df = pd.DataFrame(history)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("📥 Export History"):
        st.info("Export functionality would trigger CSV download")


if __name__ == "__main__":
    show()
