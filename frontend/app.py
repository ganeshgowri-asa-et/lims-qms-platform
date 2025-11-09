"""Main Streamlit application for LIMS QMS Platform."""

import streamlit as st
from config import settings

# Page configuration
st.set_page_config(
    page_title=f"{settings.APP_NAME} - NC & CAPA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .severity-critical {
        color: #d32f2f;
        font-weight: bold;
    }
    .severity-major {
        color: #f57c00;
        font-weight: bold;
    }
    .severity-minor {
        color: #fbc02d;
        font-weight: bold;
    }
    .status-open {
        color: #d32f2f;
    }
    .status-closed {
        color: #388e3c;
    }
</style>
""", unsafe_allow_html=True)

# Main page
def main():
    st.markdown(f'<div class="main-header">🔍 {settings.APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Non-Conformance & CAPA Management System</div>', unsafe_allow_html=True)

    # Welcome message
    st.info("""
    👋 Welcome to the Non-Conformance & CAPA Management System!

    This platform helps you:
    - **Register and track** non-conformances
    - **Perform root cause analysis** using 5-Why and Fishbone methodologies
    - **Manage CAPA actions** with effectiveness verification
    - **Get AI-powered suggestions** for root causes
    """)

    # Quick navigation
    st.markdown("### 🚀 Quick Navigation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📝 Register NC", use_container_width=True):
            st.switch_page("pages/1_NC_Registration.py")

    with col2:
        if st.button("🔍 View NCs", use_container_width=True):
            st.switch_page("pages/2_NC_List.py")

    with col3:
        if st.button("🎯 Root Cause Analysis", use_container_width=True):
            st.switch_page("pages/3_RCA_Analysis.py")

    with col4:
        if st.button("✅ CAPA Management", use_container_width=True):
            st.switch_page("pages/4_CAPA_Management.py")

    # System information
    st.markdown("---")
    st.markdown("### 📊 System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Features:**")
        st.markdown("""
        - ✓ NC-YYYY-XXX automatic numbering
        - ✓ CAPA-YYYY-XXX automatic numbering
        - ✓ AI-powered root cause suggestions
        - ✓ 5-Why analysis template
        - ✓ Fishbone (Ishikawa) diagram
        - ✓ Effectiveness verification
        """)

    with col2:
        st.markdown("**Navigation:**")
        st.markdown("""
        - **NC Registration**: Create new non-conformances
        - **NC List**: View and manage all NCs
        - **Root Cause Analysis**: Perform RCA using various methods
        - **CAPA Management**: Track corrective and preventive actions
        - **Dashboard**: View statistics and metrics
        """)

    # Footer
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #888;'>© 2024 {settings.ORGANIZATION_NAME} | {settings.APP_NAME} v1.0.0</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
