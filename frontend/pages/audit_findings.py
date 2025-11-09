"""
Audit Findings Management Page
With NC Linkage Support
"""
import streamlit as st
import requests
from datetime import date, timedelta

API_URL = "http://localhost:8000/api/v1/audit-risk"


def show():
    """Display the Audit Findings page"""
    st.header("🔍 Audit Findings Management")

    tab1, tab2 = st.tabs(["📋 View Findings", "➕ Create New Finding"])

    with tab1:
        st.subheader("Audit Findings List")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox(
                "Finding Type",
                options=["All", "NCR", "OFI", "OBS"],
                index=0
            )
        with col2:
            filter_status = st.selectbox(
                "Status",
                options=["All", "OPEN", "IN_PROGRESS", "CLOSED", "VERIFIED"],
                index=0
            )
        with col3:
            filter_severity = st.selectbox(
                "Severity",
                options=["All", "CRITICAL", "MAJOR", "MINOR"],
                index=0
            )

        # Fetch data button
        if st.button("🔄 Refresh Findings", key="refresh_findings"):
            try:
                params = {}
                if filter_type != "All":
                    params["finding_type"] = filter_type
                if filter_status != "All":
                    params["status"] = filter_status
                if filter_severity != "All":
                    params["severity"] = filter_severity

                response = requests.get(f"{API_URL}/findings", params=params)
                if response.status_code == 200:
                    findings = response.json()
                    if findings:
                        st.success(f"Found {len(findings)} finding(s)")
                        for finding in findings:
                            # Determine color based on severity
                            severity_color = {
                                "CRITICAL": "🔴",
                                "MAJOR": "🟠",
                                "MINOR": "🟡"
                            }.get(finding.get('severity', ''), "⚪")

                            status_emoji = {
                                "OPEN": "📌",
                                "IN_PROGRESS": "🔄",
                                "CLOSED": "✅",
                                "VERIFIED": "✔️"
                            }.get(finding['status'], "📋")

                            with st.expander(
                                f"{severity_color} {status_emoji} {finding['finding_number']} - {finding['finding_type']} ({finding['area_audited']})"
                            ):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Type:** {finding['finding_type']}")
                                    st.write(f"**Severity:** {finding.get('severity', 'N/A')}")
                                    st.write(f"**Category:** {finding.get('category', 'N/A')}")
                                with col2:
                                    st.write(f"**Status:** {finding['status']}")
                                    st.write(f"**Responsible:** {finding.get('responsible_person', 'N/A')}")
                                    st.write(f"**Target Date:** {finding.get('target_date', 'N/A')}")
                                with col3:
                                    st.write(f"**Clause Ref:** {finding.get('clause_reference', 'N/A')}")
                                    st.write(f"**NC Reference:** {finding.get('nc_reference', 'N/A')}")
                                    st.write(f"**Verified:** {'Yes' if finding['effectiveness_verified'] else 'No'}")

                                st.write("**Description:**")
                                st.write(finding['description'])

                                if finding.get('objective_evidence'):
                                    st.write("**Objective Evidence:**")
                                    st.write(finding['objective_evidence'])

                                if finding.get('corrective_action'):
                                    st.write("**Corrective Action:**")
                                    st.write(finding['corrective_action'])

                                if finding.get('root_cause'):
                                    st.write("**Root Cause:**")
                                    st.write(finding['root_cause'])
                    else:
                        st.info("No audit findings found")
                else:
                    st.error(f"Error fetching findings: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab2:
        st.subheader("Create New Audit Finding")

        # First, fetch audit schedules for selection
        with st.form("create_finding_form"):
            col1, col2 = st.columns(2)

            with col1:
                audit_id = st.number_input(
                    "Audit ID",
                    min_value=1,
                    value=1,
                    help="Enter the ID of the associated audit"
                )
                finding_type = st.selectbox(
                    "Finding Type",
                    options=["NCR", "OFI", "OBS"],
                    help="NCR=Non-Conformance, OFI=Opportunity for Improvement, OBS=Observation"
                )
                severity = st.selectbox(
                    "Severity",
                    options=["MINOR", "MAJOR", "CRITICAL"],
                    help="Only applicable for NCRs"
                )
                category = st.selectbox(
                    "Category",
                    options=["DOCUMENTATION", "PROCESS", "EQUIPMENT", "PERSONNEL", "CALIBRATION"]
                )

            with col2:
                clause_reference = st.text_input(
                    "Clause Reference",
                    value="ISO 17025:2017 - 7.4",
                    help="ISO clause reference"
                )
                area_audited = st.text_input("Area Audited")
                responsible_person = st.text_input("Responsible Person")
                target_date = st.date_input(
                    "Target Closure Date",
                    value=date.today() + timedelta(days=30)
                )

            description = st.text_area(
                "Finding Description",
                height=100,
                help="Describe the non-conformance or observation"
            )

            objective_evidence = st.text_area(
                "Objective Evidence",
                height=80,
                help="Evidence supporting the finding"
            )

            requirement = st.text_area(
                "Requirement",
                height=60,
                help="What was the requirement that was not met?"
            )

            corrective_action = st.text_area(
                "Corrective Action",
                height=80,
                help="Proposed corrective action"
            )

            root_cause = st.text_area(
                "Root Cause Analysis",
                height=80,
                help="Root cause of the non-conformance"
            )

            col1, col2 = st.columns(2)
            with col1:
                status = st.selectbox(
                    "Status",
                    options=["OPEN", "IN_PROGRESS", "CLOSED", "VERIFIED"],
                    index=0
                )
            with col2:
                nc_reference = st.text_input(
                    "NC Reference (optional)",
                    help="Link to NC-YYYY-XXX from NC/CAPA module"
                )

            submitted = st.form_submit_button("✅ Create Finding")

            if submitted:
                try:
                    data = {
                        "audit_id": audit_id,
                        "finding_type": finding_type,
                        "severity": severity,
                        "category": category,
                        "clause_reference": clause_reference,
                        "area_audited": area_audited,
                        "description": description,
                        "objective_evidence": objective_evidence,
                        "requirement": requirement,
                        "root_cause": root_cause,
                        "corrective_action": corrective_action,
                        "responsible_person": responsible_person,
                        "target_date": target_date.isoformat(),
                        "status": status,
                        "nc_reference": nc_reference if nc_reference else None,
                        "effectiveness_verified": False,
                    }

                    response = requests.post(f"{API_URL}/findings", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Audit Finding created successfully! Finding Number: {result['finding_number']}"
                        )
                    else:
                        st.error(f"Error creating finding: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Please ensure the backend is running.")
