"""
Report Generation Page
"""
import streamlit as st
import sys
from pathlib import Path
import requests

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings

st.set_page_config(page_title="Report Generation", page_icon="📊", layout="wide")

st.title("📊 Report Generation")
st.markdown("Generate professional test reports and certificates")

st.markdown("---")

API_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1"

# Report ID input
report_id = st.number_input("Enter Report ID", min_value=1, value=1, step=1)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 PDF Report Generation")

    st.info("""
    Generate a comprehensive PDF test report including:
    - Test specifications
    - Module information
    - Test results and measurements
    - Graphs and charts
    - Pass/fail evaluation
    - Signatures
    """)

    if st.button("Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/iec-tests/reports/{report_id}/generate-pdf"
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ PDF Report Generated Successfully!")
                    st.info(f"📁 File Path: {result['pdf_path']}")
                    st.success(f"📊 Status: {result['status']}")

                    # Download button (in production, this would serve the actual file)
                    st.markdown("---")
                    st.download_button(
                        label="📥 Download Report",
                        data=b"PDF content would be here",
                        file_name=f"test_report_{report_id}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(f"Failed to generate report: {response.text}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 🎫 Digital Certificate Generation")

    st.info("""
    Generate a digital test certificate with:
    - Certificate number
    - QR code for verification
    - Digital signature
    - Test results summary
    - Validity period
    """)

    if st.button("Generate Certificate", type="primary", use_container_width=True):
        with st.spinner("Generating certificate..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/iec-tests/reports/{report_id}/generate-certificate"
                )

                if response.status_code == 200:
                    certificate = response.json()
                    st.success(f"✅ Certificate Generated Successfully!")

                    # Display certificate info
                    st.markdown("---")
                    st.markdown("#### Certificate Details")

                    cert_col1, cert_col2 = st.columns(2)

                    with cert_col1:
                        st.metric("Certificate Number", certificate['certificate_number'])
                        st.metric("Issue Date", certificate['issue_date'][:10])

                    with cert_col2:
                        st.metric("Status", "Valid" if certificate['is_valid'] else "Invalid")
                        st.metric("Revoked", "Yes" if certificate['revoked'] else "No")

                    st.markdown("---")
                    st.info(f"🔗 Verification URL: {certificate.get('verification_url', 'N/A')}")

                    if certificate.get('qr_code_image_path'):
                        st.success(f"📱 QR Code: {certificate['qr_code_image_path']}")

                    # Download button
                    if certificate.get('certificate_pdf_path'):
                        st.download_button(
                            label="📥 Download Certificate",
                            data=b"Certificate PDF content",
                            file_name=f"certificate_{certificate['certificate_number']}.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.error(f"Failed to generate certificate: {response.text}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")

# Graph generation section
st.markdown("### 📈 Graph Generation")

st.markdown("""
Generate various graphs for test analysis:
- I-V Characteristic Curves
- P-V Power Curves
- Temperature Profiles
- Degradation Analysis Charts
""")

graph_type = st.selectbox(
    "Select Graph Type",
    options=["IV Curve", "Power Curve", "Temperature Profile", "Degradation Chart"]
)

if st.button("Generate Graph", use_container_width=True):
    st.info(f"Generating {graph_type}...")
    st.warning("Graph generation requires test data - connect to API endpoint")

st.markdown("---")

# Batch operations
st.markdown("### 🔄 Batch Operations")

st.markdown("Generate multiple reports or certificates at once")

uploaded_file = st.file_uploader(
    "Upload CSV file with Report IDs",
    type=['csv'],
    help="Upload a CSV file containing report IDs for batch processing"
)

if uploaded_file:
    st.info("Batch processing will be implemented to handle multiple reports")

    batch_col1, batch_col2 = st.columns(2)

    with batch_col1:
        if st.button("Batch Generate Reports", use_container_width=True):
            st.info("Processing batch report generation...")

    with batch_col2:
        if st.button("Batch Generate Certificates", use_container_width=True):
            st.info("Processing batch certificate generation...")
