"""Settings Page - System settings and user preferences."""

import streamlit as st
import requests
from datetime import datetime


def show():
    """Render the settings page."""
    st.header("⚙️ Settings")
    st.markdown("System configuration and user preferences")

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 API Configuration", "👥 User Management", "📊 Preferences", "ℹ️ About"])

    with tab1:
        _render_api_config()
    with tab2:
        _render_user_management()
    with tab3:
        _render_preferences()
    with tab4:
        _render_about()


def _render_api_config():
    """Render API configuration settings."""
    st.subheader("API Configuration")

    # Current API base URL
    api_base = st.session_state.get("api_base", "http://localhost:8080/api/v1")
    new_api_base = st.text_input(
        "CAD Service API Base URL",
        value=api_base,
        placeholder="http://localhost:8080/api/v1",
        help="Base URL for the CAD backend service",
    )

    if st.button("🔄 Test Connection"):
        try:
            response = requests.get(f"{new_api_base.rstrip('/v1')}/health", timeout=5)
            if response.status_code == 200:
                st.success("Connection successful!")
            else:
                st.warning(f"Connection returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the specified API. Please check the URL.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    if st.button("💾 Save API Settings"):
        st.session_state["api_base"] = new_api_base
        st.success("API settings saved!")

    st.divider()

    # API Documentation
    st.subheader("API Endpoints")
    endpoints = [
        {"method": "POST", "path": "/api/v1/detect/batch", "description": "Run batch anomaly detection"},
        {"method": "GET", "path": "/api/v1/explain/{transaction_id}", "description": "Get anomaly explanation"},
        {"method": "POST", "path": "/api/v1/feedback", "description": "Submit review feedback"},
        {"method": "GET", "path": "/api/v1/models", "description": "List available models"},
        {"method": "GET", "path": "/api/v1/health/degradation", "description": "Check degradation status"},
    ]

    for ep in endpoints:
        col1, col2, col3 = st.columns([1, 3, 4])
        with col1:
            method_color = "green" if ep["method"] == "GET" else "blue" if ep["method"] == "POST" else "orange"
            st.markdown(f":{method_color}[{ep['method']}]")
        with col2:
            st.code(ep["path"], language=None)
        with col3:
            st.text(ep["description"])

    st.divider()

    # Rate limiting settings
    st.subheader("Rate Limiting")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Max Requests per Minute", value=60, min_value=1, max_value=1000)
        st.number_input("Timeout (seconds)", value=30, min_value=5, max_value=300)
    with col2:
        st.toggle("Enable Retry on Failure")
        st.number_input("Max Retries", value=3, min_value=0, max_value=10)


def _render_user_management():
    """Render user management settings."""
    st.subheader("User Management")

    # Current user info
    st.markdown("**Current User**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Username", value="admin", disabled=True)
    with col2:
        st.text_input("Role", value="supervisor", disabled=True)
    with col3:
        st.text_input("Team", value="fraud_detection", disabled=True)

    st.divider()

    # User roles
    st.subheader("Role Permissions")
    roles = [
        {"role": "admin", "permissions": ["Full access", "User management", "Deploy models"]},
        {"role": "supervisor", "permissions": ["View dashboard", "Submit feedback", "View models"]},
        {"role": "analyst", "permissions": ["View dashboard", "Submit feedback"]},
        {"role": "viewer", "permissions": ["View dashboard only"]},
    ]

    for role in roles:
        with st.expander(f"Role: {role['role']}"):
            for perm in role["permissions"]:
                st.checkbox(perm, value=True, disabled=True, key=f"perm_{role['role']}_{perm}")

    st.divider()

    # Team management
    st.subheader("Team Management")
    teams = [
        {"name": "fraud_detection", "members": 5, "description": "Fraud detection team"},
        {"name": "risk_management", "members": 3, "description": "Risk management team"},
        {"name": "compliance", "members": 2, "description": "Compliance monitoring team"},
    ]

    for team in teams:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{team['name']}**")
                st.caption(team["description"])
            with col2:
                st.metric("Members", team["members"])
            with col3:
                if st.button("Manage", key=f"team_{team['name']}"):
                    st.info(f"Managing {team['name']}")
            st.divider()


def _render_preferences():
    """Render user preferences."""
    st.subheader("Display Preferences")

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Theme", ["Light", "Dark", "System"])
        st.selectbox("Date Format", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        st.selectbox("Time Format", ["24-hour", "12-hour"])
    with col2:
        st.selectbox("Language", ["English", "中文"])
        st.selectbox("Currency Format", ["1,234.56", "1.234,56"])

    st.divider()

    st.subheader("Dashboard Preferences")
    col1, col2 = st.columns(2)
    with col1:
        st.slider("Refresh Interval (seconds)", 10, 300, 60)
        st.slider("Table Page Size", 10, 100, 25)
    with col2:
        st.toggle("Show Debug Info")
        st.toggle("Enable Animations")

    st.divider()

    st.subheader("Notification Preferences")
    col1, col2 = st.columns(2)
    with col1:
        st.toggle("Desktop Notifications")
        st.toggle("Sound Alerts")
    with col2:
        st.toggle("Email Digest")
        st.toggle("Weekly Report")

    if st.button("💾 Save Preferences", type="primary", use_container_width=True):
        st.success("Preferences saved successfully!")


def _render_about():
    """Render about section."""
    st.subheader("About Cashflow Radar")

    st.markdown("""
    **Cashflow Radar** (CAD - Cashflow Anomaly Detection) is a real-time anomaly
    detection system designed for financial transaction monitoring.
    """)

    st.markdown("### System Information")
    info = [
        ("Version", "1.0.0"),
        ("Build Date", "2024-03-15"),
        ("Environment", "Production"),
        ("CAD Console", "Streamlit 1.35.0+"),
    ]
    for key, value in info:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{key}**")
        with col2:
            st.text(value)

    st.divider()

    st.markdown("### Technology Stack")
    stack = [
        ("Backend", "FastAPI + Python 3.11"),
        ("ML Models", "iForest, LOF, Graph-based Detection"),
        ("Data Quality", "CAD Data Quality Checker"),
        ("Feature Engineering", "CAD Feature Engine"),
        ("Fusion Engine", "Multi-algorithm score fusion"),
        ("UI Framework", "Streamlit"),
        ("Visualization", "Plotly"),
    ]
    for tech, desc in stack:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{tech}**")
        with col2:
            st.text(desc)

    st.divider()

    st.markdown("### Support")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📖 Documentation"):
            st.info("Documentation would open in new tab")
    with col2:
        if st.button("🐛 Report Issue"):
            st.info("Issue tracker would open")
    with col3:
        if st.button("💬 Contact Support"):
            st.info("Support contact would appear")


if __name__ == "__main__":
    show()
