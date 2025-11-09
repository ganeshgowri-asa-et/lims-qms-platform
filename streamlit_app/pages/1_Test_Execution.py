"""
Test Execution Page
"""
import streamlit as st
import sys
from pathlib import Path
import requests
from datetime import datetime
import pandas as pd

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings

st.set_page_config(page_title="Test Execution", page_icon="🧪", layout="wide")

st.title("🧪 IEC Test Execution")
st.markdown("Create and execute IEC standard tests for PV modules")

st.markdown("---")

# API endpoint
API_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1"

# Session state initialization
if 'current_report_id' not in st.session_state:
    st.session_state.current_report_id = None

# Tab selection
tab1, tab2, tab3 = st.tabs(["📝 Create Test Report", "🔬 Execute Tests", "📊 View Results"])

with tab1:
    st.markdown("### Create New Test Report")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Report Information")

        report_number = st.text_input(
            "Report Number",
            value=f"RPT-{datetime.now().strftime('%Y%m%d')}-001",
            help="Unique report identifier"
        )

        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        customer_id = st.text_input("Customer ID (Optional)", placeholder="Customer ID")

        sample_id = st.text_input("Sample ID", placeholder="Sample identifier")
        module_serial = st.text_input("Module Serial Number", placeholder="Serial number")

    with col2:
        st.markdown("#### Test Configuration")

        iec_standard = st.selectbox(
            "IEC Standard",
            options=["IEC 61215", "IEC 61730", "IEC 61701"],
            help="Select the IEC standard for testing"
        )

        test_type = st.text_input(
            "Test Type",
            placeholder="e.g., Design Qualification",
            help="Specific test type"
        )

        module_model = st.text_input("Module Model", placeholder="PV module model")

        test_objective = st.text_area(
            "Test Objective",
            placeholder="Describe the purpose of this test...",
            height=100
        )

        tested_by = st.text_input("Tested By", placeholder="Technician name")

    st.markdown("---")

    st.markdown("#### Module Specifications")

    spec_col1, spec_col2, spec_col3 = st.columns(3)

    with spec_col1:
        manufacturer = st.text_input("Manufacturer", placeholder="Module manufacturer")
        technology_type = st.selectbox(
            "Technology Type",
            options=["Mono-Si", "Poly-Si", "Thin Film", "PERC", "HJT", "IBC"]
        )
        rated_power = st.number_input("Rated Power (W)", min_value=0.0, value=0.0, step=10.0)

    with spec_col2:
        voc = st.number_input("Voc (V)", min_value=0.0, value=0.0, step=0.1)
        isc = st.number_input("Isc (A)", min_value=0.0, value=0.0, step=0.1)
        vmp = st.number_input("Vmp (V)", min_value=0.0, value=0.0, step=0.1)

    with spec_col3:
        imp = st.number_input("Imp (A)", min_value=0.0, value=0.0, step=0.1)
        efficiency = st.number_input("Efficiency (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        cell_count = st.number_input("Cell Count", min_value=0, value=60, step=1)

    st.markdown("---")

    if st.button("🚀 Create Test Report", type="primary", use_container_width=True):
        # Prepare report data
        report_data = {
            "report_number": report_number,
            "customer_name": customer_name,
            "customer_id": customer_id if customer_id else None,
            "sample_id": sample_id,
            "module_model": module_model,
            "module_serial_number": module_serial if module_serial else None,
            "iec_standard": iec_standard,
            "test_type": test_type,
            "test_objective": test_objective,
            "tested_by": tested_by
        }

        module_data = {
            "manufacturer": manufacturer,
            "technology_type": technology_type,
            "rated_power_pmax": rated_power,
            "open_circuit_voltage_voc": voc,
            "short_circuit_current_isc": isc,
            "max_power_voltage_vmp": vmp,
            "max_power_current_imp": imp,
            "efficiency": efficiency,
            "cell_count": cell_count
        }

        try:
            # Create report
            response = requests.post(
                f"{API_BASE_URL}/iec-tests/reports",
                json=report_data
            )

            if response.status_code == 201:
                report = response.json()
                st.session_state.current_report_id = report["id"]

                # Add module specs
                module_response = requests.post(
                    f"{API_BASE_URL}/iec-tests/reports/{report['id']}/modules",
                    json=module_data
                )

                if module_response.status_code == 200:
                    st.success(f"✅ Test report created successfully! Report ID: {report['id']}")
                    st.info(f"Report Number: {report['report_number']}")
                else:
                    st.warning("Report created but module specs failed to save")
            else:
                st.error(f"Failed to create report: {response.text}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.markdown("### Execute Test Sequence")

    if st.session_state.current_report_id:
        st.info(f"Current Report ID: {st.session_state.current_report_id}")

        report_id = st.session_state.current_report_id

        # Test type selection
        selected_standard = st.selectbox(
            "Select Test Standard",
            options=["IEC 61215", "IEC 61730", "IEC 61701"]
        )

        if selected_standard == "IEC 61215":
            st.markdown("#### IEC 61215 Test Configuration")

            test_name = st.selectbox(
                "Test Name",
                options=[
                    "MST 01 - Visual Inspection",
                    "MST 05 - Maximum Power Determination",
                    "MST 06 - Insulation Test",
                    "MST 07 - Temperature Coefficient",
                    "MST 08 - NOCT Measurement",
                    "MST 09 - Performance at STC",
                    "MST 23 - Thermal Cycling"
                ]
            )

            test_col1, test_col2 = st.columns(2)

            with test_col1:
                initial_pmax = st.number_input("Initial Pmax (W)", min_value=0.0, value=0.0)
                final_pmax = st.number_input("Final Pmax (W)", min_value=0.0, value=0.0)

            with test_col2:
                temperature = st.number_input("Temperature (°C)", value=25.0)
                irradiance = st.number_input("Irradiance (W/m²)", value=1000.0)

            visual_pass = st.checkbox("Visual Inspection Passed", value=True)

            if st.button("Add Test", type="primary"):
                # Calculate degradation
                degradation = ((initial_pmax - final_pmax) / initial_pmax * 100) if initial_pmax > 0 else 0

                test_data = {
                    "test_name": test_name,
                    "temperature": temperature,
                    "irradiance": irradiance,
                    "initial_pmax": initial_pmax,
                    "final_pmax": final_pmax,
                    "power_degradation": degradation,
                    "visual_inspection_pass": visual_pass,
                    "result": "NOT_TESTED"
                }

                try:
                    response = requests.post(
                        f"{API_BASE_URL}/iec-tests/reports/{report_id}/iec-61215-tests",
                        json=test_data
                    )

                    if response.status_code == 200:
                        st.success("✅ Test added successfully!")
                    else:
                        st.error(f"Failed to add test: {response.text}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

        elif selected_standard == "IEC 61730":
            st.markdown("#### IEC 61730 Safety Test Configuration")
            # Similar implementation for IEC 61730
            st.info("IEC 61730 test configuration - Implementation similar to IEC 61215")

        elif selected_standard == "IEC 61701":
            st.markdown("#### IEC 61701 Salt Mist Test Configuration")
            # Similar implementation for IEC 61701
            st.info("IEC 61701 test configuration - Implementation similar to IEC 61215")

    else:
        st.warning("⚠️ Please create a test report first in the 'Create Test Report' tab")

with tab3:
    st.markdown("### Test Results")

    if st.session_state.current_report_id:
        report_id = st.session_state.current_report_id

        try:
            # Fetch report data
            response = requests.get(f"{API_BASE_URL}/iec-tests/reports/{report_id}")

            if response.status_code == 200:
                report = response.json()

                # Display report info
                st.markdown("#### Report Information")

                info_col1, info_col2, info_col3 = st.columns(3)

                with info_col1:
                    st.metric("Report Number", report["report_number"])
                    st.metric("Status", report["status"])

                with info_col2:
                    st.metric("Customer", report["customer_name"])
                    st.metric("Module Model", report["module_model"])

                with info_col3:
                    st.metric("Standard", report["iec_standard"])
                    st.metric("Overall Result", report["overall_result"])

                st.markdown("---")

                # Display tests
                if report.get("iec_61215_tests"):
                    st.markdown("#### IEC 61215 Tests")

                    tests_df = pd.DataFrame(report["iec_61215_tests"])
                    st.dataframe(tests_df, use_container_width=True)

                # Action buttons
                st.markdown("---")

                btn_col1, btn_col2, btn_col3 = st.columns(3)

                with btn_col1:
                    if st.button("📊 Generate Graphs"):
                        st.info("Graph generation feature - integrate with API")

                with btn_col2:
                    if st.button("📄 Generate PDF Report"):
                        try:
                            pdf_response = requests.post(
                                f"{API_BASE_URL}/iec-tests/reports/{report_id}/generate-pdf"
                            )
                            if pdf_response.status_code == 200:
                                result = pdf_response.json()
                                st.success(f"✅ PDF generated: {result['pdf_path']}")
                            else:
                                st.error("Failed to generate PDF")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

                with btn_col3:
                    if st.button("🎫 Generate Certificate"):
                        try:
                            cert_response = requests.post(
                                f"{API_BASE_URL}/iec-tests/reports/{report_id}/generate-certificate"
                            )
                            if cert_response.status_code == 200:
                                certificate = cert_response.json()
                                st.success(f"✅ Certificate generated: {certificate['certificate_number']}")
                            else:
                                st.error("Failed to generate certificate")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            else:
                st.error("Failed to fetch report data")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    else:
        st.warning("⚠️ No active report. Please create a test report first.")
