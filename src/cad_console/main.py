"""CAD Console - Main Entry Point.

Streamlit-based console UI for Cashflow Anomaly Detection system.
Run with: streamlit run main.py --server.port 8501
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Cashflow Radar Console",
    page_icon=":radar:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Page definitions (must be before st.navigation in newer versions)
PAGES = {
    "Dashboard": "pages.dashboard",
    "Review": "pages.review",
    "Deployment": "pages.deployment",
    "Settings": "pages.settings",
}


def main():
    """Main application entry."""
    # Header
    st.title(":radar: Cashflow Radar Console")
    st.markdown("**C**ashflow **A**nomaly **D**etection System")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio(
        "Go to",
        options=list(PAGES.keys()),
        index=0,
        format_func=lambda x: (
            f"📊 {x}"
            if x == "Dashboard"
            else (
                f"📋 {x}"
                if x == "Review"
                else f"🚀 {x}" if x == "Deployment" else f"⚙️ {x}"
            )
        ),
    )

    # Route to selected page
    if selection == "Dashboard":
        from pages import dashboard

        dashboard.show()
    elif selection == "Review":
        from pages import review

        review.show()
    elif selection == "Deployment":
        from pages import deployment

        deployment.show()
    elif selection == "Settings":
        from pages import settings

        settings.show()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.0 | Cashflow Radar")


if __name__ == "__main__":
    main()
