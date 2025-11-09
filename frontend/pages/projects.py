"""
Project Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show projects page"""
    st.header("📊 Project Management")

    tab1, tab2, tab3 = st.tabs(["📋 All Projects", "➕ Create Project", "📈 Gantt Chart"])

    with tab1:
        st.subheader("Projects List")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Planning", "In Progress", "Completed", "On Hold"])
        with col2:
            customer_filter = st.selectbox("Customer", ["All", "Customer A", "Customer B", "Customer C"])
        with col3:
            search = st.text_input("Search", placeholder="Project name or number")

        # Sample data
        projects = pd.DataFrame({
            'Project Number': ['PRJ-2024-0001', 'PRJ-2024-0002', 'PRJ-2024-0003', 'PRJ-2024-0004'],
            'Project Name': ['PV Module Testing - Batch A', 'Inverter Certification', 'Lab Expansion', 'ISO 17025 Accreditation'],
            'Customer': ['Solar Corp', 'Power Systems Inc', 'Internal', 'Internal'],
            'Status': ['In Progress', 'Planning', 'Completed', 'In Progress'],
            'Progress': ['65%', '20%', '100%', '80%'],
            'Start Date': ['2024-01-15', '2024-03-01', '2023-10-01', '2023-11-15'],
            'End Date': ['2024-04-30', '2024-05-15', '2024-02-28', '2024-04-10']
        })

        st.dataframe(projects, use_container_width=True)

        # Project details
        selected_project = st.selectbox("View Details", projects['Project Name'].tolist())

        if selected_project:
            st.subheader(f"Project: {selected_project}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Budget", "$50,000")
            with col2:
                st.metric("Actual Cost", "$32,500")
            with col3:
                st.metric("Tasks", "15")
            with col4:
                st.metric("Team Size", "5")

    with tab2:
        st.subheader("Create New Project")

        with st.form("create_project"):
            proj_name = st.text_input("Project Name*")

            col1, col2 = st.columns(2)
            with col1:
                customer = st.selectbox("Customer", ["Internal", "Customer A", "Customer B", "Customer C"])
            with col2:
                proj_manager = st.selectbox("Project Manager", ["John Doe", "Jane Smith", "Bob Johnson"])

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")

            budget = st.number_input("Budget ($)", min_value=0, value=10000)

            description = st.text_area("Description")

            submit = st.form_submit_button("Create Project")

            if submit:
                if proj_name:
                    st.success(f"✅ Project '{proj_name}' created successfully!")
                else:
                    st.error("Please fill all required fields")

    with tab3:
        st.subheader("Project Gantt Chart")
        st.info("📊 Gantt chart visualization will be displayed here")
        st.image("https://via.placeholder.com/800x400.png?text=Gantt+Chart+Placeholder")
