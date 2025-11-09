"""
LIMS-QMS Platform - Streamlit Multi-Page App
Main Entry Point
"""
import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="LIMS-QMS Platform",
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
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'executive'  # Default role
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = None

# Sidebar
with st.sidebar:
    st.title("🔬 LIMS-QMS Platform")
    st.markdown("---")

    # Role selector (for demo purposes)
    st.subheader("User Role")
    role = st.selectbox(
        "Select Role",
        ["Executive", "Lab Manager", "Quality Manager", "Technician", "Customer"],
        index=["Executive", "Lab Manager", "Quality Manager", "Technician", "Customer"].index(
            st.session_state.user_role.title() if st.session_state.user_role else "Executive"
        )
    )
    st.session_state.user_role = role.lower()

    # Customer ID selector (if customer role)
    if st.session_state.user_role == 'customer':
        st.session_state.customer_id = st.number_input(
            "Customer ID",
            min_value=1,
            value=st.session_state.customer_id if st.session_state.customer_id else 1
        )

    st.markdown("---")
    st.caption("Session 9: Analytics Dashboard & Customer Portal")

# Main page content
st.title("Welcome to LIMS-QMS Platform")

st.markdown("""
### Laboratory Information Management System with Quality Management

This integrated platform provides comprehensive management of laboratory operations,
quality systems, and customer interactions.

#### 📊 Analytics Dashboards
- **Executive Dashboard**: High-level KPIs, revenue, and performance metrics
- **Operational Dashboard**: Sample tracking, equipment, and training metrics
- **Quality Dashboard**: Non-conformance trends, CAPA, and audit findings

#### 🌐 Customer Portal
- Submit test requests online
- Track samples in real-time
- View test progress and results
- Access test reports and certificates

#### Select a page from the sidebar to get started.
""")

# Display quick stats based on role
if st.session_state.user_role in ['executive', 'lab manager', 'quality manager']:
    st.markdown("---")
    st.subheader("Quick Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Active Test Requests",
            value="24",
            delta="5"
        )

    with col2:
        st.metric(
            label="Samples in Progress",
            value="38",
            delta="-2"
        )

    with col3:
        st.metric(
            label="Quality Rate",
            value="98.5%",
            delta="0.3%"
        )

    with col4:
        st.metric(
            label="On-Time Delivery",
            value="95.2%",
            delta="1.2%"
        )

elif st.session_state.user_role == 'customer':
    st.markdown("---")
    st.info("👉 Navigate to 'Customer Portal' from the sidebar to access your dashboard")

st.markdown("---")
st.caption("Powered by Streamlit | LIMS-QMS Platform v1.0.0")
