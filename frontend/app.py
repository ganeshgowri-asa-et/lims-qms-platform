"""
Streamlit Frontend for LIMS-QMS Platform
Session 8: Audit & Risk Management System
"""
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="LIMS-QMS Platform - Audit & Risk Management",
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
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-critical {
        background-color: #ff4444;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .risk-high {
        background-color: #ff8800;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .risk-medium {
        background-color: #ffbb33;
        color: black;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .risk-low {
        background-color: #00C851;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
    }
    .footer {
        text-align: center;
        color: #888;
        padding: 2rem 0 1rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔍 LIMS-QMS Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Audit & Risk Management System - Session 8</div>',
    unsafe_allow_html=True
)

# Sidebar navigation
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Dashboard",
        "📅 Audit Program",
        "📆 Audit Schedule",
        "🔍 Audit Findings",
        "⚠️ Risk Register",
        "✅ Compliance Tracking",
    ]
)

# Information section
st.sidebar.markdown("---")
st.sidebar.info("""
**Session 8 Features:**
- QSF1701 Annual Audit Program
- 5x5 Risk Matrix
- Audit Findings with NC Linkage
- ISO 17025 & ISO 9001 Compliance Tracking
""")

# API Status
st.sidebar.markdown("---")
API_URL = "http://localhost:8000"
st.sidebar.markdown(f"**API Endpoint:** `{API_URL}`")

# Main content area
if page == "🏠 Dashboard":
    st.header("📊 Audit & Risk Management Dashboard")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Audits", "12", "+3")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Open Findings", "8", "-2")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Risks", "15", "+1")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Compliance Rate", "94.5%", "+2.5%")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Upcoming Audits")
        st.info("Audit schedule widget will be displayed here")

    with col2:
        st.subheader("⚠️ High Priority Risks")
        st.warning("Risk matrix visualization will be displayed here")

    st.markdown("---")

    # Recent activity
    st.subheader("📌 Recent Activity")
    st.info("Recent audit findings and risk updates will be displayed here")

elif page == "📅 Audit Program":
    from frontend.pages import audit_program
    audit_program.show()

elif page == "📆 Audit Schedule":
    from frontend.pages import audit_schedule
    audit_schedule.show()

elif page == "🔍 Audit Findings":
    from frontend.pages import audit_findings
    audit_findings.show()

elif page == "⚠️ Risk Register":
    from frontend.pages import risk_register
    risk_register.show()

elif page == "✅ Compliance Tracking":
    from frontend.pages import compliance_tracking
    compliance_tracking.show()

# Footer
st.markdown("---")
st.markdown(
    f'<div class="footer">LIMS-QMS Platform v1.0 | ISO 17025:2017 & ISO 9001:2015 Compliant | © {datetime.now().year}</div>',
    unsafe_allow_html=True
)
