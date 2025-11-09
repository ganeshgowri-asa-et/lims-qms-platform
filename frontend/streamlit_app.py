"""
Main Streamlit application for LIMS/QMS Platform
"""
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pages import test_request_page, sample_management_page, dashboard_page
from utils.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="LIMS/QMS Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #2c3e50;
    }
    h2 {
        color: #34495e;
    }
    </style>
    """, unsafe_allow_html=True)


def check_api_health():
    """Check if API is accessible"""
    try:
        result = APIClient.health_check()
        return result.get("status") == "healthy"
    except Exception as e:
        st.sidebar.error(f"⚠️ API Connection Error: {str(e)}")
        st.sidebar.warning("Please ensure the backend API is running.")
        return False


def main():
    """Main application"""

    # Sidebar
    st.sidebar.title("🔬 LIMS/QMS Platform")
    st.sidebar.markdown("---")

    # Check API health
    api_healthy = check_api_health()

    if api_healthy:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.sidebar.info("Start the backend API:\n```\ncd backend\npython -m app.main\n```")

    st.sidebar.markdown("---")

    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📝 Test Requests",
            "🧪 Sample Management",
            "👥 Customers",
            "📈 Reports"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Session 5: LIMS Core**

    - Test Request Management (QSF0601)
    - Sample Tracking
    - Auto TRQ Numbering
    - Barcode Generation
    - Quote Automation
    """)

    # Render selected page
    if page == "📊 Dashboard":
        dashboard_page.show()
    elif page == "📝 Test Requests":
        test_request_page.show()
    elif page == "🧪 Sample Management":
        sample_management_page.show()
    elif page == "👥 Customers":
        st.title("👥 Customer Management")
        st.info("Customer management page - Coming soon!")
    elif page == "📈 Reports":
        st.title("📈 Reports & Analytics")
        st.info("Reports and analytics page - Coming soon!")


if __name__ == "__main__":
    main()
