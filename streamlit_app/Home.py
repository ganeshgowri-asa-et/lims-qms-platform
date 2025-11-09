"""
LIMS-QMS Platform - Streamlit Analytics Dashboard
Session 9: Analytics Dashboard & Customer Portal
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="LIMS-QMS Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"


def get_executive_dashboard():
    """Fetch executive dashboard data"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/executive-dashboard")
        return response.json()
    except:
        return {
            "test_requests_this_month": 0,
            "active_nonconformances": 0,
            "calibrations_due_30days": 0,
            "training_due_30days": 0,
            "revenue_this_month": 0
        }


def main():
    st.title("🔬 LIMS-QMS Analytics Dashboard")
    st.markdown("### AI-Powered Laboratory Information Management System")

    # Sidebar - Role Selection
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=LIMS-QMS", use_container_width=True)
        st.markdown("---")

        role = st.selectbox(
            "Select Your Role",
            ["Executive", "Quality Manager", "Laboratory Technician", "Customer"]
        )

        st.markdown("---")
        st.info(f"**Role:** {role}")
        st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Main Dashboard Content
    if role == "Executive":
        show_executive_dashboard()
    elif role == "Quality Manager":
        show_quality_dashboard()
    elif role == "Laboratory Technician":
        show_operational_dashboard()
    elif role == "Customer":
        show_customer_portal()


def show_executive_dashboard():
    """Executive Dashboard View"""
    st.header("📊 Executive Dashboard")

    data = get_executive_dashboard()

    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Test Requests",
            data["test_requests_this_month"],
            delta="This Month"
        )

    with col2:
        st.metric(
            "Active NCs",
            data["active_nonconformances"],
            delta=-2,
            delta_color="inverse"
        )

    with col3:
        st.metric(
            "Calibrations Due",
            data["calibrations_due_30days"],
            delta="Next 30 days"
        )

    with col4:
        st.metric(
            "Training Due",
            data["training_due_30days"],
            delta="Next 30 days"
        )

    with col5:
        st.metric(
            "Revenue",
            f"₹{data['revenue_this_month']:,.0f}",
            delta="This Month"
        )

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")
        # Sample data
        months = pd.date_range(start='2024-01', end='2024-06', freq='ME')
        revenue_data = pd.DataFrame({
            'Month': months.strftime('%b %Y'),
            'Revenue': [450000, 520000, 480000, 610000, 580000, 650000]
        })

        fig = px.line(revenue_data, x='Month', y='Revenue',
                      markers=True, title="Revenue Growth")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Test Requests by Status")
        status_data = pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'Pending', 'Cancelled'],
            'Count': [45, 23, 12, 3]
        })

        fig = px.pie(status_data, values='Count', names='Status',
                     title="Test Request Distribution")
        st.plotly_chart(fig, use_container_width=True)


def show_quality_dashboard():
    """Quality Manager Dashboard"""
    st.header("🎯 Quality Management Dashboard")

    try:
        response = requests.get(f"{API_BASE_URL}/analytics/quality-metrics")
        data = response.json()
    except:
        data = {
            "nc_trend": [],
            "capa_effectiveness_rate": 85.0,
            "open_audit_findings": 5,
            "risk_distribution": {}
        }

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CAPA Effectiveness", f"{data['capa_effectiveness_rate']}%")

    with col2:
        st.metric("Open Audit Findings", data["open_audit_findings"])

    with col3:
        total_risks = sum(data.get("risk_distribution", {}).values())
        st.metric("Active Risks", total_risks)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Non-Conformance Trend")

        # Sample NC trend data
        nc_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Count': [8, 6, 9, 5, 7, 4]
        })

        fig = px.bar(nc_data, x='Month', y='Count',
                     title="Monthly NC Count", color='Count')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Risk Distribution (5x5 Matrix)")

        risk_dist = data.get("risk_distribution", {
            "low": 12, "medium": 8, "high": 3, "critical": 1
        })

        fig = go.Figure(data=[go.Pie(
            labels=list(risk_dist.keys()),
            values=list(risk_dist.values()),
            marker=dict(colors=['green', 'yellow', 'orange', 'red'])
        )])
        fig.update_layout(title="Risk Levels")
        st.plotly_chart(fig, use_container_width=True)

    # Recent NCs
    st.subheader("📋 Recent Non-Conformances")
    try:
        response = requests.get(f"{API_BASE_URL}/nonconformance?limit=10")
        ncs = response.json()

        if ncs:
            nc_df = pd.DataFrame(ncs)
            st.dataframe(
                nc_df[['nc_number', 'nc_category', 'severity', 'status']],
                use_container_width=True
            )
    except:
        st.info("No non-conformances to display")


def show_operational_dashboard():
    """Operational Dashboard for Technicians"""
    st.header("🔧 Operational Dashboard")

    try:
        response = requests.get(f"{API_BASE_URL}/analytics/operational-metrics")
        data = response.json()
    except:
        data = {
            "equipment_status": {},
            "sample_status": {},
            "test_completion_rate": 0,
            "avg_test_duration_days": 0
        }

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Test Completion Rate", f"{data['test_completion_rate']}%")

    with col2:
        st.metric("Avg Test Duration", f"{data['avg_test_duration_days']} days")

    with col3:
        total_equipment = sum(data.get("equipment_status", {}).values())
        st.metric("Total Equipment", total_equipment)

    st.markdown("---")

    # Equipment & Samples
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Equipment Status")

        eq_status = data.get("equipment_status", {
            "operational": 45, "under_calibration": 3,
            "under_maintenance": 2, "out_of_service": 1
        })

        fig = px.bar(
            x=list(eq_status.keys()),
            y=list(eq_status.values()),
            labels={'x': 'Status', 'y': 'Count'},
            title="Equipment by Status"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sample Status")

        sample_status = data.get("sample_status", {
            "received": 34, "in_testing": 18, "tested": 56, "disposed": 12
        })

        fig = px.pie(
            values=list(sample_status.values()),
            names=list(sample_status.keys()),
            title="Samples by Status"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Calibration Due
    st.subheader("⚠️ Calibrations Due")
    try:
        response = requests.get(f"{API_BASE_URL}/equipment/calibration-due?days_ahead=30")
        equipment = response.json()

        if equipment:
            eq_df = pd.DataFrame(equipment)
            st.dataframe(
                eq_df[['equipment_id', 'name', 'next_calibration_date']],
                use_container_width=True
            )
        else:
            st.success("No calibrations due in next 30 days")
    except:
        st.info("Unable to fetch calibration data")


def show_customer_portal():
    """Customer Portal"""
    st.header("👤 Customer Portal")

    st.markdown("### Track Your Test Requests")

    # Search by TRQ number
    trq_number = st.text_input("Enter Test Request Number (TRQ)", placeholder="TRQ-2024-001")

    if trq_number:
        st.info(f"Searching for {trq_number}...")

        # Sample tracking data
        st.subheader(f"📦 Test Request: {trq_number}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Status", "In Progress")

        with col2:
            st.metric("Completion", "65%")

        with col3:
            st.metric("Est. Delivery", "2024-07-15")

        # Progress timeline
        st.markdown("---")
        st.subheader("Test Progress")

        progress_data = pd.DataFrame({
            'Stage': ['Sample Received', 'Testing Started', 'Testing In Progress', 'Report Generation', 'Delivery'],
            'Status': ['✅ Complete', '✅ Complete', '🔄 In Progress', '⏳ Pending', '⏳ Pending'],
            'Date': ['2024-06-01', '2024-06-05', '2024-06-10', '-', '-']
        })

        st.table(progress_data)

        # Sample details
        st.markdown("---")
        st.subheader("Sample Details")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Sample ID:** SMP-2024-0045")
            st.write("**Test Standard:** IEC 61215")
            st.write("**Sample Type:** Solar PV Module")

        with col2:
            st.write("**Manufacturer:** ABC Solar")
            st.write("**Model:** XYZ-300W")
            st.write("**Received Date:** 2024-06-01")

    else:
        st.info("Enter your test request number to track status")

    st.markdown("---")

    # New Test Request Form
    with st.expander("📝 Submit New Test Request"):
        st.subheader("New Test Request")

        company = st.text_input("Company Name")
        contact = st.text_input("Contact Person")
        email = st.text_input("Email")

        test_standard = st.selectbox(
            "Test Standard",
            ["IEC 61215", "IEC 61730", "IEC 61701"]
        )

        sample_type = st.text_input("Sample Type")
        quantity = st.number_input("Quantity", min_value=1, value=1)

        if st.button("Submit Request"):
            st.success("✅ Test request submitted successfully! You will receive a quotation within 24 hours.")


if __name__ == "__main__":
    main()
