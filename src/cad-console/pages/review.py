"""Review Page - Anomaly review and feedback submission."""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime


def show():
    """Render the review page."""
    st.header("📋 Review Queue")
    st.markdown("Review and confirm detected anomalies")

    API_BASE = st.session_state.get("api_base", "http://localhost:8080/api/v1")

    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_txn = st.text_input("Search Transaction ID", placeholder="Enter transaction ID...")
    with col2:
        risk_filter = st.selectbox("Risk Level", ["All", "高风险", "中风险", "低风险"])
    with col3:
        status_filter = st.selectbox("Status", ["All", "Pending", "Confirmed", "Excluded", "Uncertain"])

    # Sample review items
    review_items = _get_demo_review_items()

    # Review table
    st.subheader("Review Items")
    if review_items:
        df = pd.DataFrame(review_items)

        # Apply filters
        if search_txn:
            df = df[df["transaction_id"].str.contains(search_txn, case=False, na=False)]
        if risk_filter != "All":
            df = df[df["risk_level"] == risk_filter]

        st.dataframe(
            df[["transaction_id", "account_id", "risk_level", "final_score", "anomaly_type", "status"]],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        # Review detail panel
        st.subheader("Review Details")
        col_left, col_right = st.columns([1, 2])

        with col_left:
            selected_txn = st.selectbox(
                "Select Transaction to Review",
                options=df["transaction_id"].tolist(),
            )

        # Get selected item details
        selected = next((item for item in review_items if item["transaction_id"] == selected_txn), None)

        if selected:
            with col_right:
                st.json({
                    "transaction_id": selected["transaction_id"],
                    "account_id": selected["account_id"],
                    "risk_level": selected["risk_level"],
                    "final_score": selected["final_score"],
                    "anomaly_type": selected.get("anomaly_type", "TYPE_01"),
                    "rule_hit": selected.get("rule_hit", False),
                    "rule_score": selected.get("rule_score", 0.0),
                })

                # Explanation section
                st.markdown("**Anomaly Explanation**")
                with st.expander("View SHAP Explanation"):
                    st.info("Feature contribution analysis would appear here")
                    st.write("- amt_deviation: 0.42 contribution (3.8 vs 0.45 historical mean)")
                    st.write("- velocity_score: 0.28 contribution")
                    st.write("- balance_ratio: 0.15 contribution")

            st.divider()

            # Feedback form
            st.subheader("Submit Feedback")
            col1, col2 = st.columns([2, 1])
            with col1:
                review_result = st.radio(
                    "Review Result",
                    options=["确认", "排除", "存疑"],
                    horizontal=True,
                    help="Confirm the anomaly, exclude it, or mark as uncertain",
                )
                anomaly_type = st.selectbox(
                    "Anomaly Type",
                    ["TYPE_01", "TYPE_02", "TYPE_03", "TYPE_04", "Other"],
                )
                comment = st.text_area(
                    "Review Comment",
                    placeholder="Enter your review comments here...",
                    height=100,
                )
            with col2:
                st.write("### Quick Actions")
                if st.button("✅ Confirm (确认)", use_container_width=True):
                    _submit_feedback(API_BASE, selected_txn, "确认", comment, anomaly_type)
                if st.button("❌ Exclude (排除)", use_container_width=True):
                    _submit_feedback(API_BASE, selected_txn, "排除", comment, anomaly_type)
                if st.button("❓ Mark Uncertain (存疑)", use_container_width=True):
                    _submit_feedback(API_BASE, selected_txn, "存疑", comment, anomaly_type)
    else:
        st.info("No items in review queue")


def _submit_feedback(api_base: str, transaction_id: str, result: str, comment: str, anomaly_type: str):
    """Submit feedback for a transaction."""
    try:
        response = requests.post(
            f"{api_base}/feedback",
            json={
                "transaction_id": transaction_id,
                "review_result": result,
                "review_comment": comment,
                "anomaly_type": anomaly_type,
            },
            timeout=10,
        )
        if response.status_code == 200:
            st.success(f"Feedback submitted successfully for {transaction_id}")
        else:
            st.error(f"Failed to submit feedback: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.success(f"[Demo] Feedback submitted: {transaction_id} -> {result}")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def _get_demo_review_items():
    """Return demo review items."""
    return [
        {
            "transaction_id": f"TXN{i:06d}",
            "account_id": f"ACC{i % 10:04d}",
            "risk_level": "高风险" if i % 5 == 0 else "中风险" if i % 5 < 3 else "低风险",
            "final_score": 75.0 + (i % 25),
            "anomaly_type": f"TYPE_0{i % 4 + 1}",
            "status": "Pending",
            "rule_hit": i % 3 == 0,
            "rule_score": 85.0 if i % 3 == 0 else 0.0,
        }
        for i in range(15)
    ]


if __name__ == "__main__":
    show()
