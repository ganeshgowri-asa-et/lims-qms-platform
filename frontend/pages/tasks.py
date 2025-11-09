"""
Task Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show tasks page"""
    st.header("✅ Task Management")

    tab1, tab2, tab3 = st.tabs(["📋 My Tasks", "➕ Create Task", "📊 Kanban Board"])

    with tab1:
        st.subheader("Task List")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "To Do", "In Progress", "In Review", "Completed"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "Low", "Medium", "High", "Critical"])
        with col3:
            project_filter = st.selectbox("Project", ["All", "Project A", "Project B", "Project C"])

        # Sample data
        tasks = pd.DataFrame({
            'Task Number': ['TASK-2024-0045', 'TASK-2024-0046', 'TASK-2024-0047', 'TASK-2024-0048'],
            'Title': ['Complete calibration', 'Review test report', 'Update documentation', 'Equipment maintenance'],
            'Status': ['In Progress', 'To Do', 'In Review', 'Completed'],
            'Priority': ['High', 'Medium', 'Low', 'Critical'],
            'Assigned To': ['John Doe', 'Me', 'Jane Smith', 'Bob Johnson'],
            'Due Date': ['2024-03-15', '2024-03-20', '2024-03-18', '2024-03-10'],
            'Progress': ['60%', '0%', '90%', '100%']
        })

        st.dataframe(tasks, use_container_width=True)

    with tab2:
        st.subheader("Create New Task")

        with st.form("create_task"):
            task_title = st.text_input("Task Title*")

            col1, col2 = st.columns(2)
            with col1:
                project = st.selectbox("Project", ["None", "Project A", "Project B", "Project C"])
            with col2:
                assigned_to = st.selectbox("Assign To", ["Me", "John Doe", "Jane Smith", "Bob Johnson"])

            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
            with col2:
                due_date = st.date_input("Due Date")

            description = st.text_area("Description")

            submit = st.form_submit_button("Create Task")

            if submit:
                if task_title:
                    st.success(f"✅ Task '{task_title}' created successfully!")
                else:
                    st.error("Please enter task title")

    with tab3:
        st.subheader("Kanban Board")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("### 📝 To Do")
            st.info("TASK-0046: Review test report")
            st.info("TASK-0049: Prepare training material")

        with col2:
            st.markdown("### 🔄 In Progress")
            st.warning("TASK-0045: Complete calibration")
            st.warning("TASK-0050: Update procedures")

        with col3:
            st.markdown("### 👀 In Review")
            st.success("TASK-0047: Update documentation")

        with col4:
            st.markdown("### ✅ Completed")
            st.success("TASK-0048: Equipment maintenance")
            st.success("TASK-0044: Audit preparation")
