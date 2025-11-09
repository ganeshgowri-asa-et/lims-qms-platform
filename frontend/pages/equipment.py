"""
Equipment Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show equipment page"""
    st.header("🔧 Equipment Management")

    tab1, tab2, tab3 = st.tabs(["📋 Equipment List", "📅 Calibration Schedule", "🔧 Maintenance"])

    with tab1:
        st.subheader("Equipment Inventory")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox("Category", ["All", "Test Equipment", "Calibration", "IT", "Other"])
        with col2:
            status_filter = st.selectbox("Status", ["All", "Active", "Under Calibration", "Under Maintenance"])
        with col3:
            search = st.text_input("Search", placeholder="Equipment ID or name")

        equipment = pd.DataFrame({
            'Equipment ID': ['EQ-2024-0001', 'EQ-2024-0002', 'EQ-2024-0003', 'EQ-2024-0004'],
            'Name': ['Digital Multimeter', 'Temperature Chamber', 'Solar Simulator', 'Oscilloscope'],
            'Category': ['Test Equipment', 'Test Equipment', 'Test Equipment', 'Test Equipment'],
            'Manufacturer': ['Fluke', 'Espec', 'Newport', 'Tektronix'],
            'Status': ['Active', 'Active', 'Under Calibration', 'Active'],
            'Last Calibration': ['2024-01-15', '2024-02-20', '2024-03-01', '2023-12-10'],
            'Next Calibration': ['2024-07-15', '2025-02-20', '2024-09-01', '2024-06-10']
        })

        st.dataframe(equipment, use_container_width=True)

        if st.button("➕ Register New Equipment"):
            st.info("Equipment registration form will open here")

    with tab2:
        st.subheader("Calibration Schedule")

        # Due calibrations
        st.warning("⚠️ 3 equipments have calibration due in next 30 days")

        cal_schedule = pd.DataFrame({
            'Equipment ID': ['EQ-2024-0004', 'EQ-2024-0005', 'EQ-2024-0008'],
            'Name': ['Oscilloscope', 'Power Analyzer', 'Data Logger'],
            'Last Calibration': ['2023-12-10', '2023-11-25', '2024-01-05'],
            'Due Date': ['2024-06-10', '2024-05-25', '2024-07-05'],
            'Days Remaining': [15, 45, 85],
            'Status': ['Overdue', 'Due Soon', 'Scheduled']
        })

        st.dataframe(cal_schedule, use_container_width=True)

        if st.button("📅 Schedule Calibration"):
            st.info("Calibration scheduling form will open here")

    with tab3:
        st.subheader("Maintenance Records")

        maintenance = pd.DataFrame({
            'Maintenance ID': ['MAINT-2024-0005', 'MAINT-2024-0006', 'MAINT-2024-0007'],
            'Equipment': ['Temperature Chamber', 'Solar Simulator', 'Digital Multimeter'],
            'Type': ['Preventive', 'Corrective', 'Preventive'],
            'Date': ['2024-03-01', '2024-02-28', '2024-02-15'],
            'Performed By': ['Tech Team', 'Vendor', 'Tech Team'],
            'Status': ['Completed', 'Completed', 'Completed']
        })

        st.dataframe(maintenance, use_container_width=True)

        if st.button("➕ Add Maintenance Record"):
            st.info("Maintenance record form will open here")
