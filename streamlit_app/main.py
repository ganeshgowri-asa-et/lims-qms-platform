"""
Streamlit Main Application - IEC Test Report Generation
"""
import streamlit as st
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

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
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #2c5aa0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4788;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1f4788/FFFFFF?text=LIMS-QMS", use_container_width=True)
    st.markdown("---")

    st.markdown(f"### {settings.LAB_NAME}")
    st.caption(f"Accreditation: {settings.LAB_ACCREDITATION}")

    st.markdown("---")

    st.markdown("### Navigation")
    st.markdown("""
    - 🏠 **Home** - Dashboard
    - 🧪 **Test Execution** - Run IEC tests
    - 📊 **Report Generation** - Create reports
    - 📜 **Test History** - View past tests
    """)

    st.markdown("---")

    st.markdown("### System Info")
    st.caption(f"Version: {settings.APP_VERSION}")
    st.caption(f"Environment: {settings.ENVIRONMENT}")

# Main content
st.markdown('<div class="main-header">🔬 LIMS-QMS Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Solar PV Module Testing & Certification System</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# Welcome section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="🎯 IEC Standards Supported",
        value="3",
        delta="IEC 61215, 61730, 61701"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="📋 Active Test Reports",
        value="0",
        delta="No active tests"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(
        label="✅ Certificates Issued",
        value="0",
        delta="This month"
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Features overview
st.markdown("### 🎯 Platform Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Test Execution
    - **IEC 61215**: Design qualification and type approval
    - **IEC 61730**: PV module safety qualification
    - **IEC 61701**: Salt mist corrosion testing
    - Real-time data acquisition
    - Automated pass/fail evaluation

    #### Report Generation
    - Professional PDF reports
    - Automated graph generation
    - I-V and P-V characteristic curves
    - Temperature profiles
    - Degradation analysis charts
    """)

with col2:
    st.markdown("""
    #### Digital Certificates
    - QR code verification
    - Digital signatures
    - Certificate authenticity tracking
    - Validity period management
    - Online verification portal

    #### Compliance & Standards
    - ISO/IEC 17025:2017 compliant
    - Automated documentation
    - Full traceability
    - Audit trail
    - Data integrity assurance
    """)

st.markdown("---")

# Quick start guide
st.markdown("### 🚀 Quick Start Guide")

st.markdown("""
1. **Create Test Report** - Navigate to Test Execution page
2. **Enter Module Specifications** - Fill in PV module details
3. **Run Test Sequence** - Execute IEC standard tests
4. **Review Results** - Check pass/fail criteria
5. **Generate Report** - Create PDF report with graphs
6. **Issue Certificate** - Generate digital certificate with QR code
""")

st.markdown("---")

# System status
st.markdown("### 📊 System Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.markdown('<div class="success-box">✅ API Server: <b>Online</b></div>', unsafe_allow_html=True)

with status_col2:
    st.markdown('<div class="success-box">✅ Database: <b>Connected</b></div>', unsafe_allow_html=True)

with status_col3:
    st.markdown('<div class="success-box">✅ Services: <b>Operational</b></div>', unsafe_allow_html=True)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><b>Solar PV Testing Laboratory</b></p>
    <p>Accredited to ISO/IEC 17025:2017 | License: {}</p>
    <p>© 2024 LIMS-QMS Platform | Version {}</p>
</div>
""".format(settings.LAB_LICENSE, settings.APP_VERSION), unsafe_allow_html=True)
