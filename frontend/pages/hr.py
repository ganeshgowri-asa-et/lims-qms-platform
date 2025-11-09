"""
HR Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show HR page"""
    st.header("👥 HR Management")

    tab1, tab2, tab3, tab4 = st.tabs(["👤 Employees", "📅 Leave", "📚 Training", "📊 Performance"])

    with tab1:
        st.subheader("Employee Directory")

        employees = pd.DataFrame({
            'Employee ID': ['EMP001', 'EMP002', 'EMP003', 'EMP004'],
            'Name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Williams'],
            'Department': ['Testing', 'Calibration', 'Quality', 'Admin'],
            'Designation': ['Senior Engineer', 'Technician', 'QA Manager', 'HR Manager'],
            'Email': ['john@company.com', 'jane@company.com', 'bob@company.com', 'alice@company.com'],
            'Status': ['Active', 'Active', 'Active', 'Active']
        })

        st.dataframe(employees, use_container_width=True)

    with tab2:
        st.subheader("Leave Management")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 Apply for Leave")

            with st.form("leave_request"):
                leave_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Earned Leave", "Unpaid Leave"])

                col_a, col_b = st.columns(2)
                with col_a:
                    start_date = st.date_input("Start Date")
                with col_b:
                    end_date = st.date_input("End Date")

                num_days = st.number_input("Number of Days", min_value=0.5, value=1.0, step=0.5)

                reason = st.text_area("Reason")

                submit = st.form_submit_button("Submit Leave Request")

                if submit:
                    st.success("✅ Leave request submitted successfully!")

        with col2:
            st.markdown("### 📊 Leave Balance")

            leave_balance = pd.DataFrame({
                'Leave Type': ['Casual Leave', 'Sick Leave', 'Earned Leave'],
                'Total': [10, 7, 15],
                'Used': [3, 2, 5],
                'Balance': [7, 5, 10]
            })

            st.dataframe(leave_balance, use_container_width=True)

            st.markdown("### 📅 Leave History")
            leave_history = pd.DataFrame({
                'Date': ['2024-02-15 to 2024-02-16', '2024-01-10 to 2024-01-11'],
                'Type': ['Casual Leave', 'Sick Leave'],
                'Days': [2, 2],
                'Status': ['Approved', 'Approved']
            })
            st.dataframe(leave_history, use_container_width=True)

    with tab3:
        st.subheader("Training Management")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📚 Upcoming Trainings")

            trainings = pd.DataFrame({
                'Training': ['ISO 17025 Awareness', 'Calibration Techniques', 'Safety Training'],
                'Date': ['2024-03-20', '2024-04-05', '2024-03-25'],
                'Duration': ['2 days', '3 days', '1 day'],
                'Enrolled': ['Yes', 'No', 'Yes']
            })

            st.dataframe(trainings, use_container_width=True)

        with col2:
            st.markdown("### 🎓 My Certifications")

            certifications = pd.DataFrame({
                'Certification': ['ISO 17025 Internal Auditor', 'Six Sigma Green Belt'],
                'Issue Date': ['2023-06-15', '2022-11-20'],
                'Valid Until': ['2026-06-15', '2025-11-20']
            })

            st.dataframe(certifications, use_container_width=True)

    with tab4:
        st.subheader("Performance Management")

        st.markdown("### 🎯 Goals & KPIs")

        goals = pd.DataFrame({
            'Goal': ['Complete 50 calibrations', 'Achieve 95% on-time delivery', 'Reduce NC by 20%'],
            'Target': ['50', '95%', '20%'],
            'Achieved': ['35', '92%', '15%'],
            'Progress': ['70%', '97%', '75%']
        })

        st.dataframe(goals, use_container_width=True)

        st.markdown("### 📊 Performance Rating")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Rating", "4.5/5")
        with col2:
            st.metric("Last Review", "Q4 2023")
        with col3:
            st.metric("Next Review", "Q1 2024")
