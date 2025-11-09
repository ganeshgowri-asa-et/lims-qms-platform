"""
Audit Program Management Page
QSF1701 - Annual Internal Audit Program
"""
import streamlit as st
import requests
from datetime import datetime, date

API_URL = "http://localhost:8000/api/v1/audit-risk"


def show():
    """Display the Audit Program page"""
    st.header("📅 Annual Audit Program (QSF1701)")

    tab1, tab2 = st.tabs(["📋 View Programs", "➕ Create New Program"])

    with tab1:
        st.subheader("Audit Programs List")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_year = st.selectbox(
                "Filter by Year",
                options=["All"] + list(range(datetime.now().year, 2023, -1)),
                index=0
            )
        with col2:
            filter_status = st.selectbox(
                "Filter by Status",
                options=["All", "DRAFT", "APPROVED", "ACTIVE", "COMPLETED"],
                index=0
            )

        # Fetch data button
        if st.button("🔄 Refresh Data", key="refresh_programs"):
            try:
                params = {}
                if filter_year != "All":
                    params["year"] = filter_year
                if filter_status != "All":
                    params["status"] = filter_status

                response = requests.get(f"{API_URL}/programs", params=params)
                if response.status_code == 200:
                    programs = response.json()
                    if programs:
                        st.success(f"Found {len(programs)} program(s)")
                        for program in programs:
                            with st.expander(
                                f"{program['program_number']} - {program['program_title']}"
                            ):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Year:** {program['program_year']}")
                                    st.write(f"**Status:** {program['status']}")
                                with col2:
                                    st.write(f"**Prepared By:** {program['prepared_by']}")
                                    st.write(f"**Reviewed By:** {program['reviewed_by']}")
                                with col3:
                                    st.write(f"**Approved By:** {program['approved_by']}")
                                    st.write(f"**Start Date:** {program['start_date']}")

                                st.write(f"**Scope:** {program['scope']}")
                                st.write(f"**Objectives:** {program['objectives']}")
                    else:
                        st.info("No audit programs found")
                else:
                    st.error(f"Error fetching programs: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab2:
        st.subheader("Create New Audit Program")

        with st.form("create_program_form"):
            col1, col2 = st.columns(2)

            with col1:
                program_year = st.number_input(
                    "Program Year",
                    min_value=2024,
                    max_value=2030,
                    value=datetime.now().year
                )
                program_title = st.text_input(
                    "Program Title",
                    value=f"Annual Internal Audit Program {program_year}"
                )
                status = st.selectbox(
                    "Status",
                    options=["DRAFT", "APPROVED", "ACTIVE", "COMPLETED"],
                    index=0
                )

            with col2:
                start_date = st.date_input(
                    "Start Date",
                    value=date(program_year, 1, 1)
                )
                end_date = st.date_input(
                    "End Date",
                    value=date(program_year, 12, 31)
                )

            scope = st.text_area(
                "Scope",
                value="Complete QMS and LIMS coverage including ISO 17025 and ISO 9001 requirements"
            )

            objectives = st.text_area(
                "Objectives",
                value="""- Verify compliance with ISO 17025:2017 and ISO 9001:2015
- Identify opportunities for improvement
- Ensure process effectiveness
- Evaluate competence of personnel"""
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                prepared_by = st.text_input("Prepared By")
            with col2:
                reviewed_by = st.text_input("Reviewed By")
            with col3:
                approved_by = st.text_input("Approved By")

            submitted = st.form_submit_button("✅ Create Audit Program")

            if submitted:
                try:
                    data = {
                        "program_year": program_year,
                        "program_title": program_title,
                        "scope": scope,
                        "objectives": objectives,
                        "prepared_by": prepared_by,
                        "reviewed_by": reviewed_by,
                        "approved_by": approved_by,
                        "status": status,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    }

                    response = requests.post(f"{API_URL}/programs", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Audit Program created successfully! Program Number: {result['program_number']}"
                        )
                    else:
                        st.error(f"Error creating program: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Please ensure the backend is running.")
