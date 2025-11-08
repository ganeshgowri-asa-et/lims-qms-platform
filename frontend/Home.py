"""
LIMS-QMS Platform - Main Home Page
Streamlit Frontend Application
"""
import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="LIMS-QMS Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🔬 LIMS-QMS Platform</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Laboratory Information Management System & Quality Management System</p>',
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100.png?text=LIMS-QMS", use_column_width=True)
    st.title("Navigation")
    st.info("Welcome to the LIMS-QMS Platform")

    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("- 📊 Dashboard")
    st.markdown("- 🧪 Sample Management")
    st.markdown("- 🔬 Test Management")
    st.markdown("- ⚙️ Equipment")
    st.markdown("- 📋 Quality Control")
    st.markdown("- 📄 Documents")
    st.markdown("- 👥 User Management")

    st.markdown("---")
    st.markdown(f"**Version:** 0.1.0")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Active Samples",
        value="0",
        delta="0 today",
    )

with col2:
    st.metric(
        label="Pending Tests",
        value="0",
        delta="0 new",
    )

with col3:
    st.metric(
        label="Equipment Status",
        value="0/0",
        delta="All operational",
    )

with col4:
    st.metric(
        label="Open CAPAs",
        value="0",
        delta="0 overdue",
    )

st.markdown("---")

# API Connection Status
st.subheader("🔗 System Status")

try:
    # Try to connect to backend API
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        st.success(f"✅ Backend API is connected - {data.get('service', 'Unknown')}")
    else:
        st.error("❌ Backend API returned an error")
except requests.exceptions.RequestException as e:
    st.warning("⚠️ Backend API is not available. Please start the backend service.")
    st.info("Run: `cd backend && uvicorn app.main:app --reload`")

# Welcome Section
st.markdown("---")
st.subheader("👋 Welcome to LIMS-QMS Platform")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Key Features")
    st.markdown("""
    - **Sample Management**: Track samples from receipt to disposal
    - **Test Workflow**: Automated scheduling and execution tracking
    - **Equipment Management**: Calibration and maintenance tracking
    - **Quality Control**: ISO 17025/9001 compliance
    - **Document Control**: Version control and approval workflows
    - **Analytics**: AI-powered insights and predictions
    """)

with col2:
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Configure Database**: Set up PostgreSQL connection
    2. **Create Users**: Add laboratory personnel
    3. **Register Equipment**: Add testing equipment
    4. **Define Tests**: Configure test procedures
    5. **Start Testing**: Begin sample processing
    """)

# Modules Overview
st.markdown("---")
st.subheader("📦 Available Modules")

modules = [
    {
        "name": "Sample Management",
        "icon": "🧪",
        "description": "Complete sample lifecycle tracking",
        "status": "Coming Soon"
    },
    {
        "name": "Test Management",
        "icon": "🔬",
        "description": "Test scheduling and execution",
        "status": "Coming Soon"
    },
    {
        "name": "Equipment Management",
        "icon": "⚙️",
        "description": "Calibration and maintenance",
        "status": "Coming Soon"
    },
    {
        "name": "Quality Control",
        "icon": "📊",
        "description": "QC samples and control charts",
        "status": "Coming Soon"
    },
    {
        "name": "Document Management",
        "icon": "📄",
        "description": "Controlled documents and records",
        "status": "Coming Soon"
    },
    {
        "name": "User Management",
        "icon": "👥",
        "description": "Authentication and authorization",
        "status": "Coming Soon"
    },
    {
        "name": "Audit Management",
        "icon": "🔍",
        "description": "Internal/external audits",
        "status": "Coming Soon"
    },
    {
        "name": "CAPA Management",
        "icon": "🔧",
        "description": "Corrective/preventive actions",
        "status": "Coming Soon"
    },
]

cols = st.columns(4)
for idx, module in enumerate(modules):
    with cols[idx % 4]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{module['icon']} {module['name']}</h3>
            <p>{module['description']}</p>
            <p><strong>Status:</strong> <em>{module['status']}</em></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>LIMS-QMS Platform v0.1.0 | Solar PV Testing Laboratory Solution</p>
        <p>© 2025 | Built with FastAPI + Streamlit + PostgreSQL</p>
    </div>
    """,
    unsafe_allow_html=True
)
