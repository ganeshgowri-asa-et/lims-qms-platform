"""
Analytics and BI page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def show():
    """Show analytics page"""
    st.header("📊 Analytics & Business Intelligence")

    tab1, tab2, tab3 = st.tabs(["📈 KPIs", "📊 Reports", "🎯 Custom Analytics"])

    with tab1:
        st.subheader("Key Performance Indicators")

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Project Completion Rate", "87%", "+5%")
        with col2:
            st.metric("On-Time Delivery", "92%", "+3%")
        with col3:
            st.metric("Customer Satisfaction", "4.5/5", "+0.2")
        with col4:
            st.metric("NC Closure Rate", "95%", "+2%")

        st.divider()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Monthly Revenue Trend")
            revenue_data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [95000, 108000, 125000, 135000, 142000, 158000]
            })
            fig = px.line(revenue_data, x='Month', y='Revenue', markers=True)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🎯 Task Completion")
            task_data = pd.DataFrame({
                'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'Completed': [45, 52, 48, 55],
                'Target': [50, 50, 50, 50]
            })
            fig = px.bar(task_data, x='Week', y=['Completed', 'Target'], barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        # More charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏢 Projects by Status")
            project_status = pd.DataFrame({
                'Status': ['Planning', 'In Progress', 'Completed', 'On Hold'],
                'Count': [3, 7, 15, 2]
            })
            fig = px.pie(project_status, values='Count', names='Status', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("✅ Quality Metrics")
            quality_data = pd.DataFrame({
                'Metric': ['NC Opened', 'NC Closed', 'CAPA Completed', 'Audits Done'],
                'Value': [12, 15, 8, 3]
            })
            fig = px.bar(quality_data, x='Metric', y='Value', color='Metric')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Predefined Reports")

        report_type = st.selectbox(
            "Select Report",
            [
                "Monthly Financial Summary",
                "Project Performance Report",
                "Quality Metrics Report",
                "HR Analytics Report",
                "Equipment Utilization Report",
                "Customer Activity Report"
            ]
        )

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

        if st.button("Generate Report"):
            st.success(f"✅ Generating {report_type}...")

            # Sample report data
            report_data = pd.DataFrame({
                'Category': ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5'],
                'Value': [1250, 2340, 1890, 2100, 1670],
                'Target': [2000, 2000, 2000, 2000, 2000],
                'Achievement': ['62.5%', '117%', '94.5%', '105%', '83.5%']
            })

            st.dataframe(report_data, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.button("📥 Download PDF")
            with col2:
                st.button("📊 Download Excel")

    with tab3:
        st.subheader("Custom Analytics Builder")

        st.info("🔧 Build custom analytics by selecting data sources and visualization types")

        col1, col2 = st.columns(2)

        with col1:
            data_source = st.selectbox(
                "Data Source",
                ["Projects", "Tasks", "Documents", "Quality", "Financial", "HR", "Equipment"]
            )

            metrics = st.multiselect(
                "Metrics",
                ["Count", "Sum", "Average", "Min", "Max", "Percentage"]
            )

        with col2:
            chart_type = st.selectbox(
                "Chart Type",
                ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot", "Heatmap", "Table"]
            )

            group_by = st.multiselect(
                "Group By",
                ["Status", "Category", "Priority", "Date", "Department", "User"]
            )

        if st.button("🎨 Build Visualization"):
            st.success("✅ Custom visualization created!")

            # Sample visualization
            sample_data = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D'],
                'Value': [45, 67, 89, 52]
            })
            fig = px.bar(sample_data, x='Category', y='Value')
            st.plotly_chart(fig, use_container_width=True)
