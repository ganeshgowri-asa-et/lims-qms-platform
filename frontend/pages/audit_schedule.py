"""
Audit Schedule Management Page
"""
import streamlit as st
import requests
from datetime import datetime, date, timedelta

API_URL = "http://localhost:8000/api/v1/audit-risk"


def show():
    """Display the Audit Schedule page"""
    st.header("📆 Audit Schedule Management")

    tab1, tab2 = st.tabs(["📋 View Schedule", "➕ Create New Audit"])

    with tab1:
        st.subheader("Audit Schedule List")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox(
                "Audit Type",
                options=["All", "INTERNAL", "EXTERNAL", "SURVEILLANCE", "CERTIFICATION"],
                index=0
            )
        with col2:
            filter_status = st.selectbox(
                "Status",
                options=["All", "SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"],
                index=0
            )
        with col3:
            filter_department = st.text_input("Department (optional)")

        # Fetch data button
        if st.button("🔄 Refresh Schedule", key="refresh_schedule"):
            try:
                params = {}
                if filter_type != "All":
                    params["audit_type"] = filter_type
                if filter_status != "All":
                    params["status"] = filter_status
                if filter_department:
                    params["department"] = filter_department

                response = requests.get(f"{API_URL}/schedules", params=params)
                if response.status_code == 200:
                    schedules = response.json()
                    if schedules:
                        st.success(f"Found {len(schedules)} audit(s)")
                        for audit in schedules:
                            status_emoji = {
                                "SCHEDULED": "📅",
                                "IN_PROGRESS": "🔄",
                                "COMPLETED": "✅",
                                "CANCELLED": "❌"
                            }.get(audit['status'], "📋")

                            with st.expander(
                                f"{status_emoji} {audit['audit_number']} - {audit['department']} ({audit['planned_date']})"
                            ):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Audit Type:** {audit['audit_type']}")
                                    st.write(f"**Scope:** {audit['audit_scope']}")
                                    st.write(f"**Process Area:** {audit['process_area']}")
                                with col2:
                                    st.write(f"**Lead Auditor:** {audit['lead_auditor']}")
                                    st.write(f"**Auditee:** {audit['auditee']}")
                                    st.write(f"**Duration:** {audit['duration_days']} days")
                                with col3:
                                    st.write(f"**Planned Date:** {audit['planned_date']}")
                                    st.write(f"**Actual Date:** {audit['actual_date']}")
                                    st.write(f"**Status:** {audit['status']}")

                                st.write(f"**Standard Reference:** {audit['standard_reference']}")
                                st.write(f"**Audit Team:** {audit['audit_team']}")
                                if audit['remarks']:
                                    st.write(f"**Remarks:** {audit['remarks']}")
                    else:
                        st.info("No audits scheduled")
                else:
                    st.error(f"Error fetching schedule: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab2:
        st.subheader("Schedule New Audit")

        with st.form("create_audit_form"):
            col1, col2 = st.columns(2)

            with col1:
                audit_type = st.selectbox(
                    "Audit Type",
                    options=["INTERNAL", "EXTERNAL", "SURVEILLANCE", "CERTIFICATION"]
                )
                audit_scope = st.selectbox(
                    "Audit Scope",
                    options=["DEPARTMENT", "PROCESS", "SYSTEM", "PRODUCT"]
                )
                department = st.text_input("Department", value="Testing Lab")
                process_area = st.text_input("Process Area", value="Sample Management")

            with col2:
                standard_reference = st.text_input(
                    "Standard Reference",
                    value="ISO 17025:2017 - Clause 7.4"
                )
                planned_date = st.date_input(
                    "Planned Date",
                    value=date.today() + timedelta(days=30)
                )
                duration_days = st.number_input("Duration (days)", min_value=1, value=1)
                status = st.selectbox(
                    "Status",
                    options=["SCHEDULED", "IN_PROGRESS", "COMPLETED", "CANCELLED"],
                    index=0
                )

            lead_auditor = st.text_input("Lead Auditor")
            audit_team = st.text_input("Audit Team (comma-separated)")
            auditee = st.text_input("Auditee")
            remarks = st.text_area("Remarks (optional)")

            submitted = st.form_submit_button("✅ Schedule Audit")

            if submitted:
                try:
                    data = {
                        "audit_type": audit_type,
                        "audit_scope": audit_scope,
                        "department": department,
                        "process_area": process_area,
                        "standard_reference": standard_reference,
                        "planned_date": planned_date.isoformat(),
                        "duration_days": duration_days,
                        "lead_auditor": lead_auditor,
                        "audit_team": audit_team,
                        "auditee": auditee,
                        "status": status,
                        "remarks": remarks,
                    }

                    response = requests.post(f"{API_URL}/schedules", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Audit scheduled successfully! Audit Number: {result['audit_number']}"
                        )
                    else:
                        st.error(f"Error scheduling audit: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Please ensure the backend is running.")
