"""
Compliance Tracking Page
ISO 17025:2017 & ISO 9001:2015 Compliance Management
"""
import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1/audit-risk"


def show():
    """Display the Compliance Tracking page"""
    st.header("✅ Compliance Tracking")

    tab1, tab2, tab3 = st.tabs(["📋 Compliance Matrix", "➕ Add Compliance Record", "📊 Compliance Summary"])

    with tab1:
        st.subheader("ISO Compliance Matrix")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_standard = st.selectbox(
                "Standard",
                options=["All", "ISO 17025:2017", "ISO 9001:2015"],
                index=0
            )
        with col2:
            filter_status = st.selectbox(
                "Compliance Status",
                options=["All", "COMPLIANT", "NON_COMPLIANT", "PARTIAL", "NOT_APPLICABLE"],
                index=0
            )

        # Fetch data button
        if st.button("🔄 Refresh Compliance Data", key="refresh_compliance"):
            try:
                params = {}
                if filter_standard != "All":
                    params["standard_name"] = filter_standard
                if filter_status != "All":
                    params["compliance_status"] = filter_status

                response = requests.get(f"{API_URL}/compliance", params=params)
                if response.status_code == 200:
                    compliance_records = response.json()
                    if compliance_records:
                        st.success(f"Found {len(compliance_records)} compliance record(s)")

                        # Group by standard
                        standards = {}
                        for record in compliance_records:
                            std = record['standard_name']
                            if std not in standards:
                                standards[std] = []
                            standards[std].append(record)

                        # Display by standard
                        for standard, records in standards.items():
                            st.markdown(f"### {standard}")

                            for record in records:
                                status_emoji = {
                                    "COMPLIANT": "✅",
                                    "NON_COMPLIANT": "❌",
                                    "PARTIAL": "⚠️",
                                    "NOT_APPLICABLE": "➖"
                                }.get(record['compliance_status'], "❓")

                                with st.expander(
                                    f"{status_emoji} Clause {record['clause_number']} - {record.get('clause_title', 'N/A')}"
                                ):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Clause Number:** {record['clause_number']}")
                                        st.write(f"**Status:** {record['compliance_status']}")
                                        st.write(f"**Responsible Person:** {record.get('responsible_person', 'N/A')}")
                                    with col2:
                                        st.write(f"**Last Audit:** {record.get('last_audit_date', 'N/A')}")
                                        st.write(f"**Next Audit:** {record.get('next_audit_date', 'N/A')}")

                                    if record.get('requirement'):
                                        st.write("**Requirement:**")
                                        st.write(record['requirement'])

                                    if record.get('evidence_reference'):
                                        st.write("**Evidence Reference:**")
                                        st.write(record['evidence_reference'])

                                    if record.get('remarks'):
                                        st.write("**Remarks:**")
                                        st.write(record['remarks'])
                    else:
                        st.info("No compliance records found")
                else:
                    st.error(f"Error fetching compliance data: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab2:
        st.subheader("Add Compliance Record")

        with st.form("create_compliance_form"):
            col1, col2 = st.columns(2)

            with col1:
                standard_name = st.selectbox(
                    "Standard",
                    options=["ISO 17025:2017", "ISO 9001:2015", "IEC 61215", "IEC 61730", "IEC 61701"]
                )
                clause_number = st.text_input(
                    "Clause Number",
                    help="e.g., 4.1, 6.2.1"
                )
                clause_title = st.text_input("Clause Title")

            with col2:
                compliance_status = st.selectbox(
                    "Compliance Status",
                    options=["COMPLIANT", "NON_COMPLIANT", "PARTIAL", "NOT_APPLICABLE"]
                )
                responsible_person = st.text_input("Responsible Person")

            requirement = st.text_area(
                "Requirement",
                height=100,
                help="Describe the standard requirement"
            )

            evidence_reference = st.text_area(
                "Evidence Reference",
                height=80,
                help="Links to documents, procedures, or records that demonstrate compliance"
            )

            col1, col2 = st.columns(2)
            with col1:
                last_audit_date = st.date_input("Last Audit Date")
            with col2:
                next_audit_date = st.date_input("Next Audit Date")

            remarks = st.text_area("Remarks (optional)")

            submitted = st.form_submit_button("✅ Add Compliance Record")

            if submitted:
                try:
                    data = {
                        "standard_name": standard_name,
                        "clause_number": clause_number,
                        "clause_title": clause_title,
                        "requirement": requirement,
                        "compliance_status": compliance_status,
                        "evidence_reference": evidence_reference,
                        "last_audit_date": last_audit_date.isoformat() if last_audit_date else None,
                        "next_audit_date": next_audit_date.isoformat() if next_audit_date else None,
                        "responsible_person": responsible_person,
                        "remarks": remarks,
                    }

                    response = requests.post(f"{API_URL}/compliance", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Compliance record added successfully for {standard_name} - Clause {clause_number}"
                        )
                    else:
                        st.error(f"Error adding compliance record: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab3:
        st.subheader("📊 Compliance Summary Dashboard")

        # Fetch summary data
        try:
            response = requests.get(f"{API_URL}/dashboard/summary")
            if response.status_code == 200:
                summary = response.json()

                # Display compliance metrics
                st.markdown("### Overall Compliance")
                col1, col2, col3 = st.columns(3)

                with col1:
                    compliance_data = summary.get('compliance', {})
                    st.metric(
                        "Total Clauses",
                        compliance_data.get('total_clauses', 0)
                    )

                with col2:
                    st.metric(
                        "Compliant Clauses",
                        compliance_data.get('compliant', 0)
                    )

                with col3:
                    st.metric(
                        "Compliance Rate",
                        f"{compliance_data.get('compliance_percentage', 0)}%"
                    )

                # Progress bar
                compliance_pct = compliance_data.get('compliance_percentage', 0)
                st.progress(compliance_pct / 100)

                st.markdown("---")

                # ISO 17025 Key Clauses
                st.markdown("### ISO 17025:2017 Key Requirements")
                st.info("""
                **Key Compliance Areas:**
                - 4.1 Impartiality
                - 6.2 Personnel Competence
                - 6.4 Equipment
                - 6.5 Metrological Traceability
                - 7.2 Selection, Verification & Validation of Methods
                - 7.4 Handling of Test Items
                - 7.7 Ensuring Validity of Results
                - 7.8 Reporting of Results
                - 8.8 Internal Audits
                - 8.9 Management Reviews
                """)

                st.markdown("### ISO 9001:2015 Key Requirements")
                st.info("""
                **Key Compliance Areas:**
                - 4.1 Understanding the Organization and Its Context
                - 5.1 Leadership and Commitment
                - 6.1 Actions to Address Risks and Opportunities
                - 7.5 Documented Information
                - 8.1 Operational Planning and Control
                - 9.1 Monitoring, Measurement, Analysis and Evaluation
                - 9.2 Internal Audit
                - 9.3 Management Review
                - 10.1 Nonconformity and Corrective Action
                - 10.2 Continual Improvement
                """)

            else:
                st.warning("Unable to fetch summary data")

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API. Please ensure the backend is running.")
