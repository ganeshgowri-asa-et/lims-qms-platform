"""
Customer Portal - Test Request Submission and Real-Time Sample Tracking
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Customer Portal", page_icon="🌐", layout="wide")

# Check if user is a customer
if st.session_state.get('user_role') != 'customer':
    st.warning("⚠️ This portal is designed for customers. Switch to 'Customer' role in the sidebar to access all features.")

st.title("🌐 Customer Portal")
st.markdown("Welcome to LIMS-QMS Customer Portal")

API_BASE_URL = "http://localhost:8000/api"

# Get customer ID from session state
customer_id = st.session_state.get('customer_id', 1)

# Fetch customer dashboard data
@st.cache_data(ttl=60)  # Refresh every minute for real-time tracking
def fetch_customer_dashboard(customer_id):
    try:
        response = requests.get(f"{API_BASE_URL}/portal/dashboard/{customer_id}")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Mock data
    return {
        "customer": {
            "name": "Solar Tech Industries",
            "customer_code": "CUST-2024-001",
            "email": "contact@solartech.com"
        },
        "statistics": {
            "total_requests": 42,
            "active_requests": 5,
            "completed_requests": 37,
            "active_samples": 8
        },
        "recent_requests": [
            {"request_number": "TRQ-2025-245", "request_date": "2025-11-05",
             "test_type": "IEC 61215", "status": "In Progress"},
            {"request_number": "TRQ-2025-232", "request_date": "2025-10-28",
             "test_type": "IEC 61730", "status": "Completed"},
            {"request_number": "TRQ-2025-218", "request_date": "2025-10-15",
             "test_type": "IEC 61701", "status": "Completed"},
        ],
        "active_samples": [
            {"sample_id": "SMP-2025-1234", "sample_name": "Solar Panel SP-300W",
             "status": "Testing", "received_date": "2025-11-05"},
            {"sample_id": "SMP-2025-1235", "sample_name": "Solar Module SM-400W",
             "status": "In Progress", "received_date": "2025-11-06"},
        ]
    }

dashboard_data = fetch_customer_dashboard(customer_id)

# ============================================================================
# CUSTOMER INFORMATION
# ============================================================================

st.info(f"**Customer:** {dashboard_data['customer']['name']} | "
       f"**Code:** {dashboard_data['customer']['customer_code']} | "
       f"**Email:** {dashboard_data['customer']['email']}")

# ============================================================================
# QUICK STATISTICS
# ============================================================================

st.subheader("📊 Your Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📋 Total Test Requests",
        value=dashboard_data['statistics']['total_requests']
    )

with col2:
    st.metric(
        label="🔄 Active Requests",
        value=dashboard_data['statistics']['active_requests']
    )

with col3:
    st.metric(
        label="✅ Completed Requests",
        value=dashboard_data['statistics']['completed_requests']
    )

with col4:
    st.metric(
        label="🔬 Active Samples",
        value=dashboard_data['statistics']['active_samples']
    )

st.markdown("---")

# ============================================================================
# TAB NAVIGATION
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Submit Test Request",
    "📦 Track Samples",
    "📋 My Test Requests",
    "📊 Reports & Certificates"
])

# ============================================================================
# TAB 1: SUBMIT TEST REQUEST
# ============================================================================

with tab1:
    st.subheader("📝 Submit New Test Request")

    with st.form("test_request_form"):
        col_form1, col_form2 = st.columns(2)

        with col_form1:
            sample_description = st.text_area(
                "Sample Description*",
                placeholder="e.g., Monocrystalline Solar Panel, 300W, Model XYZ-300",
                height=100
            )

            test_type = st.selectbox(
                "Test Type*",
                [
                    "IEC 61215 - PV Module Design Qualification",
                    "IEC 61730 - PV Module Safety Qualification",
                    "IEC 61701 - Salt Mist Corrosion Testing",
                    "IEC 62716 - Ammonia Corrosion Testing",
                    "Performance Testing - Custom"
                ]
            )

        with col_form2:
            required_date = st.date_input(
                "Required Completion Date",
                min_value=datetime.now().date() + timedelta(days=7),
                value=datetime.now().date() + timedelta(days=30)
            )

            priority = st.selectbox(
                "Priority",
                ["Normal", "High", "Urgent"]
            )

            quantity = st.number_input(
                "Number of Samples",
                min_value=1,
                max_value=100,
                value=1
            )

        additional_notes = st.text_area(
            "Additional Notes/Requirements",
            placeholder="Any special requirements or additional information",
            height=80
        )

        submitted = st.form_submit_button("🚀 Submit Test Request", use_container_width=True)

        if submitted:
            if sample_description:
                # In real implementation, this would call the API
                st.success(f"✅ Test Request submitted successfully!")
                st.info(f"**Request Number:** TRQ-2025-{246 + customer_id}")
                st.balloons()
            else:
                st.error("Please fill in all required fields (*)")

# ============================================================================
# TAB 2: TRACK SAMPLES (REAL-TIME)
# ============================================================================

with tab2:
    st.subheader("📦 Real-Time Sample Tracking")

    # Fetch sample tracking data
    @st.cache_data(ttl=60)
    def fetch_sample_tracking(customer_id):
        try:
            response = requests.get(f"{API_BASE_URL}/portal/samples/track/{customer_id}")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        # Mock data
        return [
            {
                "sample_id": "SMP-2025-1234",
                "sample_name": "Solar Panel SP-300W",
                "status": "Testing",
                "received_date": "2025-11-05",
                "test_request_number": "TRQ-2025-245",
                "test_progress": 65
            },
            {
                "sample_id": "SMP-2025-1235",
                "sample_name": "Solar Module SM-400W",
                "status": "In Progress",
                "received_date": "2025-11-06",
                "test_request_number": "TRQ-2025-245",
                "test_progress": 35
            },
            {
                "sample_id": "SMP-2025-1220",
                "sample_name": "PV Module PV-350W",
                "status": "Completed",
                "received_date": "2025-10-28",
                "test_request_number": "TRQ-2025-232",
                "test_progress": 100
            }
        ]

    tracking_data = fetch_sample_tracking(customer_id)

    # Display samples with progress
    for sample in tracking_data:
        with st.container():
            col_s1, col_s2, col_s3, col_s4 = st.columns([3, 2, 2, 2])

            with col_s1:
                st.markdown(f"**{sample['sample_name']}**")
                st.caption(f"Sample ID: {sample['sample_id']}")

            with col_s2:
                status_color = {
                    "Received": "🟡",
                    "In Progress": "🟠",
                    "Testing": "🔵",
                    "Completed": "🟢",
                    "Reported": "✅"
                }
                st.markdown(f"{status_color.get(sample['status'], '⚪')} **{sample['status']}**")

            with col_s3:
                st.caption("Test Progress")
                st.progress(sample['test_progress'] / 100)
                st.caption(f"{sample['test_progress']}% Complete")

            with col_s4:
                if st.button("View Details", key=f"btn_{sample['sample_id']}", use_container_width=True):
                    st.session_state.selected_sample = sample['sample_id']

            st.markdown("---")

    # Sample detail view
    if 'selected_sample' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Sample Details")

        # Mock detailed data
        sample_details = {
            "sample_id": st.session_state.selected_sample,
            "sample_name": "Solar Panel SP-300W",
            "manufacturer": "Solar Tech Industries",
            "model": "SP-300W-MC",
            "serial_number": "SN-2025-001",
            "received_date": "2025-11-05",
            "status": "Testing",
            "test_parameters": [
                {"parameter": "Visual Inspection", "status": "Completed", "result": "Pass"},
                {"parameter": "Electrical Performance", "status": "Completed", "result": "Pass"},
                {"parameter": "Thermal Cycling", "status": "In Progress", "result": "-"},
                {"parameter": "Humidity Freeze", "status": "Pending", "result": "-"},
                {"parameter": "UV Preconditioning", "status": "Pending", "result": "-"}
            ]
        }

        col_det1, col_det2 = st.columns(2)

        with col_det1:
            st.markdown("#### Sample Information")
            st.write(f"**Sample ID:** {sample_details['sample_id']}")
            st.write(f"**Name:** {sample_details['sample_name']}")
            st.write(f"**Manufacturer:** {sample_details['manufacturer']}")
            st.write(f"**Model:** {sample_details['model']}")
            st.write(f"**Serial Number:** {sample_details['serial_number']}")
            st.write(f"**Received Date:** {sample_details['received_date']}")
            st.write(f"**Current Status:** {sample_details['status']}")

        with col_det2:
            st.markdown("#### Test Parameters Progress")
            df_params = pd.DataFrame(sample_details['test_parameters'])

            st.dataframe(
                df_params,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "parameter": st.column_config.TextColumn("Test Parameter", width="medium"),
                    "status": st.column_config.TextColumn("Status", width="small"),
                    "result": st.column_config.TextColumn("Result", width="small")
                }
            )

    # Auto-refresh toggle
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 Auto-refresh tracking data (every 60 seconds)", value=True)
    if auto_refresh:
        st.caption("Data refreshes automatically every 60 seconds")

# ============================================================================
# TAB 3: MY TEST REQUESTS
# ============================================================================

with tab3:
    st.subheader("📋 My Test Requests")

    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Submitted", "In Progress", "Testing", "Completed", "Reported"]
        )

    with col_filter2:
        date_range = st.selectbox(
            "Date Range",
            ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
        )

    with col_filter3:
        test_type_filter = st.selectbox(
            "Filter by Test Type",
            ["All", "IEC 61215", "IEC 61730", "IEC 61701", "Custom"]
        )

    # Mock request data
    requests_data = pd.DataFrame([
        {"Request #": "TRQ-2025-245", "Date": "2025-11-05", "Test Type": "IEC 61215",
         "Status": "In Progress", "Samples": 2, "Quote": "$8,500"},
        {"Request #": "TRQ-2025-232", "Date": "2025-10-28", "Test Type": "IEC 61730",
         "Status": "Completed", "Samples": 3, "Quote": "$12,000"},
        {"Request #": "TRQ-2025-218", "Date": "2025-10-15", "Test Type": "IEC 61701",
         "Status": "Completed", "Samples": 1, "Quote": "$5,500"},
        {"Request #": "TRQ-2025-205", "Date": "2025-09-22", "Test Type": "IEC 61215",
         "Status": "Reported", "Samples": 2, "Quote": "$9,000"},
        {"Request #": "TRQ-2025-189", "Date": "2025-09-10", "Test Type": "Custom",
         "Status": "Reported", "Samples": 1, "Quote": "$6,500"}
    ])

    st.dataframe(
        requests_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Request #": st.column_config.TextColumn("Request Number", width="small"),
            "Date": st.column_config.DateColumn("Request Date", width="small"),
            "Test Type": st.column_config.TextColumn("Test Type", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Samples": st.column_config.NumberColumn("Samples", width="small"),
            "Quote": st.column_config.TextColumn("Quote Amount", width="small")
        }
    )

    # Request statistics
    st.markdown("---")
    st.subheader("📊 Request Statistics")

    stat_col1, stat_col2 = st.columns(2)

    with stat_col1:
        # Status distribution
        status_dist = requests_data['Status'].value_counts()
        fig_status = px.pie(
            values=status_dist.values,
            names=status_dist.index,
            title='Requests by Status'
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with stat_col2:
        # Test type distribution
        test_dist = requests_data['Test Type'].value_counts()
        fig_test = px.bar(
            x=test_dist.index,
            y=test_dist.values,
            title='Requests by Test Type',
            labels={'x': 'Test Type', 'y': 'Count'}
        )
        st.plotly_chart(fig_test, use_container_width=True)

# ============================================================================
# TAB 4: REPORTS & CERTIFICATES
# ============================================================================

with tab4:
    st.subheader("📊 Test Reports & Certificates")

    st.info("📄 Download completed test reports and certificates")

    # Mock reports data
    reports_data = pd.DataFrame([
        {
            "Report #": "RPT-2025-0232",
            "Request #": "TRQ-2025-232",
            "Test Type": "IEC 61730",
            "Issue Date": "2025-11-02",
            "Status": "Available",
            "Certificate #": "CERT-2025-0232"
        },
        {
            "Report #": "RPT-2025-0218",
            "Request #": "TRQ-2025-218",
            "Test Type": "IEC 61701",
            "Issue Date": "2025-10-20",
            "Status": "Available",
            "Certificate #": "CERT-2025-0218"
        },
        {
            "Report #": "RPT-2025-0205",
            "Request #": "TRQ-2025-205",
            "Test Type": "IEC 61215",
            "Issue Date": "2025-09-28",
            "Status": "Available",
            "Certificate #": "CERT-2025-0205"
        }
    ])

    for idx, row in reports_data.iterrows():
        with st.container():
            col_r1, col_r2, col_r3, col_r4 = st.columns([2, 2, 2, 1])

            with col_r1:
                st.markdown(f"**{row['Report #']}**")
                st.caption(f"Request: {row['Request #']}")

            with col_r2:
                st.write(row['Test Type'])
                st.caption(f"Issued: {row['Issue Date']}")

            with col_r3:
                st.write(f"✅ {row['Status']}")
                st.caption(f"Cert: {row['Certificate #']}")

            with col_r4:
                st.button("📥 Download", key=f"download_{row['Report #']}", use_container_width=True)

            st.markdown("---")

# ============================================================================
# HELP & SUPPORT
# ============================================================================

st.markdown("---")
st.subheader("❓ Help & Support")

help_col1, help_col2, help_col3 = st.columns(3)

with help_col1:
    st.info("📧 **Email Support**\n\nsupport@lims-qms.com")

with help_col2:
    st.info("📞 **Phone Support**\n\n+1 (555) 123-4567")

with help_col3:
    st.info("⏰ **Business Hours**\n\nMon-Fri: 9AM - 6PM EST")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
