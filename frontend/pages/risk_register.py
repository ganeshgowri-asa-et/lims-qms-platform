"""
Risk Register Management Page
5x5 Risk Matrix Implementation
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

API_URL = "http://localhost:8000/api/v1/audit-risk"


def get_risk_color(risk_level):
    """Get color for risk level"""
    colors = {
        "LOW": "#00C851",
        "MEDIUM": "#ffbb33",
        "HIGH": "#ff8800",
        "CRITICAL": "#ff4444"
    }
    return colors.get(risk_level, "#gray")


def show():
    """Display the Risk Register page"""
    st.header("⚠️ Risk Register Management")

    tab1, tab2, tab3 = st.tabs(["📋 Risk List", "➕ Create New Risk", "📊 Risk Matrix"])

    with tab1:
        st.subheader("Risk Register")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_category = st.selectbox(
                "Risk Category",
                options=["All", "OPERATIONAL", "STRATEGIC", "FINANCIAL", "COMPLIANCE", "TECHNICAL"],
                index=0
            )
        with col2:
            filter_status = st.selectbox(
                "Status",
                options=["All", "ACTIVE", "CLOSED", "MONITORING"],
                index=0
            )
        with col3:
            filter_level = st.selectbox(
                "Risk Level",
                options=["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
                index=0
            )

        # Fetch data button
        if st.button("🔄 Refresh Risks", key="refresh_risks"):
            try:
                params = {}
                if filter_category != "All":
                    params["risk_category"] = filter_category
                if filter_status != "All":
                    params["status"] = filter_status
                if filter_level != "All":
                    params["risk_level"] = filter_level

                response = requests.get(f"{API_URL}/risks", params=params)
                if response.status_code == 200:
                    risks = response.json()
                    if risks:
                        st.success(f"Found {len(risks)} risk(s)")
                        for risk in risks:
                            risk_level = risk.get('residual_risk_level', 'UNKNOWN')
                            level_emoji = {
                                "LOW": "🟢",
                                "MEDIUM": "🟡",
                                "HIGH": "🟠",
                                "CRITICAL": "🔴"
                            }.get(risk_level, "⚪")

                            with st.expander(
                                f"{level_emoji} {risk['risk_number']} - {risk['risk_category']} ({risk_level})"
                            ):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Category:** {risk['risk_category']}")
                                    st.write(f"**Department:** {risk.get('department', 'N/A')}")
                                    st.write(f"**Process Area:** {risk.get('process_area', 'N/A')}")
                                with col2:
                                    st.write(f"**Risk Owner:** {risk.get('risk_owner', 'N/A')}")
                                    st.write(f"**Status:** {risk['status']}")
                                    st.write(f"**Treatment:** {risk.get('risk_treatment', 'N/A')}")
                                with col3:
                                    st.write(f"**Inherent Risk:** {risk['inherent_risk_score']} ({risk['inherent_risk_level']})")
                                    st.write(f"**Residual Risk:** {risk['residual_risk_score']} ({risk['residual_risk_level']})")
                                    st.write(f"**Review Frequency:** {risk.get('review_frequency', 'N/A')}")

                                st.write("**Risk Description:**")
                                st.write(risk['risk_description'])

                                st.write("**Risk Source:**")
                                st.write(risk.get('risk_source', 'N/A'))

                                st.write("**Consequences:**")
                                st.write(risk.get('consequences', 'N/A'))

                                st.write("**Existing Controls:**")
                                st.write(risk.get('existing_controls', 'N/A'))

                                if risk.get('treatment_plan'):
                                    st.write("**Treatment Plan:**")
                                    st.write(risk['treatment_plan'])

                                # Risk Matrix visualization for this risk
                                st.write("**Risk Assessment:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"Inherent: L={risk['inherent_likelihood']} × I={risk['inherent_impact']} = {risk['inherent_risk_score']}")
                                with col2:
                                    st.write(f"Residual: L={risk['residual_likelihood']} × I={risk['residual_impact']} = {risk['residual_risk_score']}")
                    else:
                        st.info("No risks found")
                else:
                    st.error(f"Error fetching risks: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab2:
        st.subheader("Create New Risk")

        st.info("""
        **5x5 Risk Matrix Legend:**
        - **Likelihood:** 1=Rare, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain
        - **Impact:** 1=Insignificant, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic
        - **Risk Score:** Likelihood × Impact (1-25)
        - **Risk Level:** LOW (1-4), MEDIUM (5-12), HIGH (13-16), CRITICAL (17-25)
        """)

        with st.form("create_risk_form"):
            col1, col2 = st.columns(2)

            with col1:
                risk_category = st.selectbox(
                    "Risk Category",
                    options=["OPERATIONAL", "STRATEGIC", "FINANCIAL", "COMPLIANCE", "TECHNICAL"]
                )
                department = st.text_input("Department")
                process_area = st.text_input("Process Area")
                risk_owner = st.text_input("Risk Owner")

            with col2:
                risk_treatment = st.selectbox(
                    "Risk Treatment",
                    options=["MITIGATE", "ACCEPT", "TRANSFER", "AVOID"]
                )
                review_frequency = st.selectbox(
                    "Review Frequency",
                    options=["MONTHLY", "QUARTERLY", "ANNUALLY"]
                )
                target_date = st.date_input(
                    "Target Date",
                    value=date.today() + timedelta(days=90)
                )
                status = st.selectbox(
                    "Status",
                    options=["ACTIVE", "CLOSED", "MONITORING"],
                    index=0
                )

            risk_description = st.text_area(
                "Risk Description",
                height=80,
                help="Describe the risk in detail"
            )

            risk_source = st.text_area(
                "Risk Source",
                height=60,
                help="What causes this risk?"
            )

            consequences = st.text_area(
                "Consequences",
                height=60,
                help="What could happen if this risk materializes?"
            )

            existing_controls = st.text_area(
                "Existing Controls",
                height=80,
                help="Current mitigation measures in place"
            )

            treatment_plan = st.text_area(
                "Treatment Plan",
                height=80,
                help="Additional actions to reduce risk"
            )

            st.write("**Inherent Risk Assessment** (before controls)")
            col1, col2 = st.columns(2)
            with col1:
                inherent_likelihood = st.slider(
                    "Inherent Likelihood",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="1=Rare, 5=Almost Certain"
                )
            with col2:
                inherent_impact = st.slider(
                    "Inherent Impact",
                    min_value=1,
                    max_value=5,
                    value=3,
                    help="1=Insignificant, 5=Catastrophic"
                )

            inherent_score = inherent_likelihood * inherent_impact
            st.write(f"**Inherent Risk Score:** {inherent_score}")

            st.write("**Residual Risk Assessment** (after controls)")
            col1, col2 = st.columns(2)
            with col1:
                residual_likelihood = st.slider(
                    "Residual Likelihood",
                    min_value=1,
                    max_value=5,
                    value=2,
                    help="1=Rare, 5=Almost Certain"
                )
            with col2:
                residual_impact = st.slider(
                    "Residual Impact",
                    min_value=1,
                    max_value=5,
                    value=2,
                    help="1=Insignificant, 5=Catastrophic"
                )

            residual_score = residual_likelihood * residual_impact
            st.write(f"**Residual Risk Score:** {residual_score}")

            remarks = st.text_area("Remarks (optional)")

            submitted = st.form_submit_button("✅ Create Risk")

            if submitted:
                try:
                    data = {
                        "risk_category": risk_category,
                        "process_area": process_area,
                        "department": department,
                        "risk_description": risk_description,
                        "risk_source": risk_source,
                        "consequences": consequences,
                        "existing_controls": existing_controls,
                        "inherent_likelihood": inherent_likelihood,
                        "inherent_impact": inherent_impact,
                        "residual_likelihood": residual_likelihood,
                        "residual_impact": residual_impact,
                        "risk_treatment": risk_treatment,
                        "treatment_plan": treatment_plan,
                        "risk_owner": risk_owner,
                        "target_date": target_date.isoformat(),
                        "review_frequency": review_frequency,
                        "status": status,
                        "remarks": remarks,
                    }

                    response = requests.post(f"{API_URL}/risks", json=data)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(
                            f"✅ Risk created successfully! Risk Number: {result['risk_number']}"
                        )
                    else:
                        st.error(f"Error creating risk: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Please ensure the backend is running.")

    with tab3:
        st.subheader("📊 5x5 Risk Matrix Visualization")

        st.info("""
        **How to read the Risk Matrix:**
        - X-axis: Likelihood (1=Rare to 5=Almost Certain)
        - Y-axis: Impact (1=Insignificant to 5=Catastrophic)
        - Color coding: Green=Low, Yellow=Medium, Orange=High, Red=Critical
        """)

        # Placeholder for risk matrix visualization
        st.write("Risk matrix visualization will be displayed here using the fetched risks data")

        # Create a simple matrix display
        matrix_data = []
        for impact in range(5, 0, -1):
            row = []
            for likelihood in range(1, 6):
                score = likelihood * impact
                if score <= 4:
                    color = "🟢"
                elif score <= 12:
                    color = "🟡"
                elif score <= 16:
                    color = "🟠"
                else:
                    color = "🔴"
                row.append(f"{color} {score}")
            matrix_data.append(row)

        df = pd.DataFrame(
            matrix_data,
            columns=[f"L{i}" for i in range(1, 6)],
            index=[f"I{i}" for i in range(5, 0, -1)]
        )

        st.table(df)
