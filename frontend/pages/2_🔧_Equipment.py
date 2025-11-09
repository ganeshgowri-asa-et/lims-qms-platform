"""Equipment Calibration & Maintenance Management UI."""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from utils.api_client import APIClient

st.set_page_config(page_title="Equipment Management", page_icon="🔧", layout="wide")

# Initialize API client
api = APIClient()

st.title("🔧 Equipment Calibration & Maintenance")
st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Equipment List",
    "➕ Add Equipment",
    "📅 Calibration",
    "🔧 Maintenance",
    "🔔 Alerts"
])

# Tab 1: Equipment List
with tab1:
    st.header("Equipment List")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        equipment_list = api.get_equipment_list()

        if equipment_list and not isinstance(equipment_list, dict):
            df = pd.DataFrame(equipment_list)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Equipment", len(df))
            with col2:
                operational = len(df[df['status'] == 'operational']) if 'status' in df.columns else 0
                st.metric("Operational", operational)
            with col3:
                requires_cal = len(df[df['requires_calibration'] == True]) if 'requires_calibration' in df.columns else 0
                st.metric("Requires Calibration", requires_cal)
            with col4:
                avg_oee = df['oee_percentage'].mean() if 'oee_percentage' in df.columns else 0
                st.metric("Average OEE", f"{avg_oee:.1f}%")

            st.markdown("---")

            # Display table
            display_cols = [
                'equipment_id', 'name', 'manufacturer', 'model_number',
                'status', 'location', 'next_calibration_date', 'oee_percentage'
            ]
            available_cols = [col for col in display_cols if col in df.columns]

            if available_cols:
                st.dataframe(
                    df[available_cols],
                    use_container_width=True,
                    hide_index=True,
                )

                # Equipment details
                st.markdown("---")
                st.subheader("Equipment Details")

                equipment_ids = df['equipment_id'].tolist() if 'equipment_id' in df.columns else []
                selected_eq = st.selectbox("Select equipment to view details:", equipment_ids)

                if selected_eq:
                    eq_data = df[df['equipment_id'] == selected_eq].iloc[0]

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"Equipment ID: {eq_data.get('equipment_id', 'N/A')}")
                        st.write(f"Name: {eq_data.get('name', 'N/A')}")
                        st.write(f"Manufacturer: {eq_data.get('manufacturer', 'N/A')}")
                        st.write(f"Model: {eq_data.get('model_number', 'N/A')}")
                        st.write(f"Serial: {eq_data.get('serial_number', 'N/A')}")

                    with col2:
                        st.write("**Location & Status**")
                        st.write(f"Location: {eq_data.get('location', 'N/A')}")
                        st.write(f"Department: {eq_data.get('department', 'N/A')}")
                        st.write(f"Status: {eq_data.get('status', 'N/A')}")
                        st.write(f"Responsible: {eq_data.get('responsible_person', 'N/A')}")

                    with col3:
                        st.write("**Calibration & Maintenance**")
                        st.write(f"Requires Calibration: {eq_data.get('requires_calibration', False)}")
                        st.write(f"Next Calibration: {eq_data.get('next_calibration_date', 'N/A')}")
                        st.write(f"Next Maintenance: {eq_data.get('next_maintenance_date', 'N/A')}")
                        st.write(f"OEE: {eq_data.get('oee_percentage', 0):.1f}%")
        else:
            st.info("No equipment found. Add your first equipment using the 'Add Equipment' tab.")
    except Exception as e:
        st.error(f"Error loading equipment: {str(e)}")
        st.info("Make sure the backend API is running at http://localhost:8000")

# Tab 2: Add Equipment
with tab2:
    st.header("Add New Equipment")

    with st.form("create_equipment_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Basic Information")
            name = st.text_input("Equipment Name*", placeholder="Enter equipment name")
            manufacturer = st.text_input("Manufacturer", placeholder="Manufacturer name")
            model_number = st.text_input("Model Number", placeholder="Model number")
            serial_number = st.text_input("Serial Number", placeholder="Serial number")
            category = st.text_input("Category", placeholder="e.g., Testing Equipment")
            equipment_type = st.text_input("Equipment Type", placeholder="e.g., Spectrometer")

        with col2:
            st.subheader("Location & Ownership")
            location = st.text_input("Location", placeholder="Lab location")
            department = st.text_input("Department", placeholder="Department name")
            responsible_person = st.text_input("Responsible Person", placeholder="Person in charge")

            st.subheader("Calibration Settings")
            requires_calibration = st.checkbox("Requires Calibration", value=True)
            calibration_frequency = st.number_input(
                "Calibration Frequency (days)",
                min_value=1,
                value=365,
                help="Number of days between calibrations"
            )
            maintenance_frequency = st.number_input(
                "Maintenance Frequency (days)",
                min_value=1,
                value=180,
                help="Number of days between maintenance"
            )

        description = st.text_area("Description", placeholder="Equipment description")

        submitted = st.form_submit_button("Add Equipment")

        if submitted:
            if not name:
                st.error("Please enter equipment name")
            else:
                equipment_data = {
                    "name": name,
                    "description": description,
                    "manufacturer": manufacturer,
                    "model_number": model_number,
                    "serial_number": serial_number,
                    "category": category,
                    "equipment_type": equipment_type,
                    "location": location,
                    "department": department,
                    "responsible_person": responsible_person,
                    "requires_calibration": requires_calibration,
                    "calibration_frequency_days": calibration_frequency,
                    "maintenance_frequency_days": maintenance_frequency,
                }

                try:
                    result = api.create_equipment(equipment_data)

                    if "error" in result:
                        st.error(f"Error creating equipment: {result['error']}")
                    else:
                        st.success(f"✅ Equipment created successfully! Equipment ID: {result.get('equipment_id', 'N/A')}")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 3: Calibration
with tab3:
    st.header("Calibration Management")

    try:
        equipment_list = api.get_equipment_list()

        if equipment_list and not isinstance(equipment_list, dict):
            df = pd.DataFrame(equipment_list)
            equipment_ids = df['equipment_id'].tolist() if 'equipment_id' in df.columns else []

            selected_equipment = st.selectbox("Select Equipment:", equipment_ids, key="cal_equipment")

            if selected_equipment:
                eq_data = df[df['equipment_id'] == selected_equipment].iloc[0]
                eq_id = eq_data['id']

                # Show calibration history
                st.subheader("Calibration History")

                try:
                    calibrations = api.get_calibrations(eq_id)

                    if calibrations and not isinstance(calibrations, dict):
                        cal_df = pd.DataFrame(calibrations)
                        st.dataframe(
                            cal_df[['calibration_date', 'next_calibration_date', 'performed_by', 'result', 'calibration_status']],
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.info("No calibration records found")
                except:
                    st.info("No calibration records found")

                # Add new calibration
                st.markdown("---")
                st.subheader("Record New Calibration")

                with st.form("calibration_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        calibration_date = st.date_input("Calibration Date*", value=datetime.now())
                        performed_by = st.text_input("Performed By*", placeholder="Technician name")
                        calibration_agency = st.text_input("Calibration Agency", placeholder="Agency name")
                        certificate_number = st.text_input("Certificate Number", placeholder="Certificate #")

                    with col2:
                        next_cal_date = st.date_input(
                            "Next Calibration Date*",
                            value=datetime.now() + timedelta(days=eq_data.get('calibration_frequency_days', 365))
                        )
                        result = st.selectbox("Result", ["pass", "fail", "conditional"])
                        accuracy = st.number_input("Accuracy Achieved (%)", min_value=0.0, max_value=100.0, value=100.0)

                    notes = st.text_area("Notes", placeholder="Additional notes")

                    submitted = st.form_submit_button("Record Calibration")

                    if submitted:
                        if not performed_by:
                            st.error("Please enter who performed the calibration")
                        else:
                            cal_data = {
                                "calibration_date": calibration_date.isoformat(),
                                "next_calibration_date": next_cal_date.isoformat(),
                                "performed_by": performed_by,
                                "calibration_agency": calibration_agency,
                                "certificate_number": certificate_number,
                                "result": result,
                                "accuracy_achieved": accuracy,
                                "notes": notes,
                            }

                            result = api.create_calibration(eq_id, cal_data)

                            if "error" not in result:
                                st.success("✅ Calibration recorded successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")
        else:
            st.info("No equipment available. Please add equipment first.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 4: Maintenance
with tab4:
    st.header("Preventive Maintenance")

    try:
        equipment_list = api.get_equipment_list()

        if equipment_list and not isinstance(equipment_list, dict):
            df = pd.DataFrame(equipment_list)
            equipment_ids = df['equipment_id'].tolist() if 'equipment_id' in df.columns else []

            selected_equipment = st.selectbox("Select Equipment:", equipment_ids, key="maint_equipment")

            if selected_equipment:
                eq_data = df[df['equipment_id'] == selected_equipment].iloc[0]
                eq_id = eq_data['id']

                # Show maintenance history
                st.subheader("Maintenance History")

                try:
                    maintenance = api.get_maintenance(eq_id)

                    if maintenance and not isinstance(maintenance, dict):
                        maint_df = pd.DataFrame(maintenance)
                        st.dataframe(
                            maint_df[[
                                'scheduled_date', 'maintenance_type', 'is_completed',
                                'performed_by', 'total_cost'
                            ]],
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.info("No maintenance records found")
                except:
                    st.info("No maintenance records found")

                # Schedule new maintenance
                st.markdown("---")
                st.subheader("Schedule Maintenance")

                with st.form("maintenance_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        maintenance_type = st.selectbox(
                            "Maintenance Type*",
                            ["preventive", "corrective", "breakdown", "calibration"]
                        )
                        scheduled_date = st.date_input(
                            "Scheduled Date*",
                            value=datetime.now() + timedelta(days=7)
                        )
                        assigned_to = st.text_input("Assigned To", placeholder="Technician name")

                    with col2:
                        maintenance_desc = st.text_area(
                            "Maintenance Description*",
                            placeholder="Describe the maintenance work"
                        )

                    submitted = st.form_submit_button("Schedule Maintenance")

                    if submitted:
                        if not maintenance_desc:
                            st.error("Please enter maintenance description")
                        else:
                            maint_data = {
                                "maintenance_type": maintenance_type,
                                "scheduled_date": scheduled_date.isoformat(),
                                "maintenance_description": maintenance_desc,
                                "assigned_to": assigned_to,
                            }

                            result = api.create_maintenance(eq_id, maint_data)

                            if "error" not in result:
                                st.success("✅ Maintenance scheduled successfully!")
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")
        else:
            st.info("No equipment available. Please add equipment first.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Tab 5: Alerts
with tab5:
    st.header("Calibration Alerts")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 Critical (7 days)", use_container_width=True):
            st.session_state['alert_days'] = 7

    with col2:
        if st.button("🟡 Warning (15 days)", use_container_width=True):
            st.session_state['alert_days'] = 15

    with col3:
        if st.button("🟢 Info (30 days)", use_container_width=True):
            st.session_state['alert_days'] = 30

    # Get alerts
    days_threshold = st.session_state.get('alert_days', 30)

    st.markdown("---")
    st.subheader(f"Calibrations Due in Next {days_threshold} Days")

    try:
        alerts = api.get_calibration_alerts(days=days_threshold)

        if alerts and not isinstance(alerts, dict):
            if len(alerts) > 0:
                alert_df = pd.DataFrame(alerts)

                # Color code by alert level
                for idx, alert in alert_df.iterrows():
                    alert_level = alert.get('alert_level', 'info')

                    if alert_level == 'overdue':
                        icon = "🔴"
                        color = "red"
                    elif alert_level == 'critical':
                        icon = "🔴"
                        color = "orange"
                    elif alert_level == 'warning':
                        icon = "🟡"
                        color = "yellow"
                    else:
                        icon = "🟢"
                        color = "green"

                    with st.expander(f"{icon} {alert.get('equipment_id', 'N/A')} - {alert.get('equipment_name', 'N/A')}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Equipment ID:** {alert.get('equipment_id', 'N/A')}")
                            st.write(f"**Equipment Name:** {alert.get('equipment_name', 'N/A')}")

                        with col2:
                            st.write(f"**Next Calibration:** {alert.get('next_calibration_date', 'N/A')}")
                            st.write(f"**Days Remaining:** {alert.get('days_remaining', 'N/A')}")
                            st.write(f"**Alert Level:** {alert.get('alert_level', 'N/A').upper()}")
            else:
                st.success("✅ No calibrations due in this period!")
        else:
            st.info("No alerts available")
    except Exception as e:
        st.error(f"Error loading alerts: {str(e)}")
