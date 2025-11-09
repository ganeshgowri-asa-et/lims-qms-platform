"""Main Streamlit application for LIMS & QMS Platform."""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="LIMS & QMS Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main page
st.title("🔬 LIMS & QMS Platform")
st.markdown("## Laboratory Information Management & Quality Management System")

st.markdown("""
### Welcome to the LIMS & QMS Platform

This integrated platform provides comprehensive management for:

#### 📄 Document Management System (QMS)
- Auto document numbering (QSF-YYYY-XXX)
- Version control with major.minor versioning
- Approval workflow (Doer-Checker-Approver)
- PDF generation with watermarks
- Full-text search capabilities
- Digital signatures
- Controlled copy distribution

#### 🔧 Equipment Calibration & Maintenance
- Auto equipment ID generation (EQP-YYYY-XXXX)
- Calibration scheduling and tracking
- Preventive maintenance scheduling
- Calibration due alerts (30/15/7 days)
- OEE (Overall Equipment Effectiveness) tracking
- QR code generation for equipment
- Maintenance logs and history

### Getting Started

Use the sidebar navigation to access different modules:
- **Documents**: Manage QMS documents
- **Equipment**: Manage equipment and calibration
- **Alerts**: View calibration and maintenance alerts
- **Reports**: Generate reports and analytics

### Quick Stats
""")

# Display quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Documents", value="0")

with col2:
    st.metric(label="Total Equipment", value="0")

with col3:
    st.metric(label="Pending Approvals", value="0")

with col4:
    st.metric(label="Calibration Alerts", value="0")

st.markdown("---")

st.info("""
**Note**: This is the home page. Please use the sidebar to navigate to specific modules.

**API Documentation**: The backend API documentation is available at `http://localhost:8000/docs`
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<p>LIMS & QMS Platform v1.0 | ISO 17025/9001 Compliant</p>
</div>
""", unsafe_allow_html=True)
