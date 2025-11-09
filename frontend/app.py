"""
LIMS-QMS Platform - Training & Competency Management Dashboard
Streamlit Application
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# Configure page
st.set_page_config(
    page_title="LIMS-QMS Training Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_URL = "http://localhost:8000/api/training"


def show_header():
    """Display application header"""
    st.title("🎓 Training & Competency Management System")
    st.markdown("---")


def main():
    """Main application"""
    show_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Module",
        [
            "📊 Dashboard",
            "📚 Training Programs",
            "👥 Training Matrix",
            "📝 Training Attendance",
            "🎯 Competency Gap Analysis",
            "📜 Certificates",
            "📄 QSF Forms"
        ]
    )

    # Route to pages
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📚 Training Programs":
        show_training_programs()
    elif page == "👥 Training Matrix":
        show_training_matrix()
    elif page == "📝 Training Attendance":
        show_training_attendance()
    elif page == "🎯 Competency Gap Analysis":
        show_competency_gaps()
    elif page == "📜 Certificates":
        show_certificates()
    elif page == "📄 QSF Forms":
        show_qsf_forms()


def show_dashboard():
    """Show training management dashboard"""
    st.header("Training Management Dashboard")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Training Programs", "0", "+0")
    with col2:
        st.metric("Active Employees", "0", "+0")
    with col3:
        st.metric("Completed Trainings (MTD)", "0", "+0")
    with col4:
        st.metric("Competency Compliance", "0%", "+0%")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Training by Category")
        # Placeholder chart
        categories = ["Technical", "Safety", "Quality", "Soft Skills"]
        counts = [12, 8, 15, 5]
        fig = px.pie(
            values=counts,
            names=categories,
            title="Training Distribution by Category"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Competency Gap Status")
        # Placeholder chart
        statuses = ["Competent", "Gap Exists", "Not Trained", "Expired"]
        status_counts = [45, 15, 8, 2]
        fig = px.bar(
            x=statuses,
            y=status_counts,
            labels={"x": "Status", "y": "Count"},
            title="Competency Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recent activities
    st.subheader("Recent Training Activities")
    st.info("📌 Connect to API to see recent training activities")


def show_training_programs():
    """Show training programs management"""
    st.header("Training Programs Management")

    tab1, tab2 = st.tabs(["📋 View Trainings", "➕ Add New Training"])

    with tab1:
        st.subheader("All Training Programs")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            category_filter = st.selectbox(
                "Category",
                ["All", "Technical", "Safety", "Quality", "Soft Skills", "Compliance"]
            )
        with col2:
            type_filter = st.selectbox(
                "Type",
                ["All", "Internal", "External", "On-the-job", "E-learning"]
            )
        with col3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Active", "Inactive"]
            )

        # Display trainings
        st.info("📌 Connect to API to fetch training programs")

        # Example table
        df = pd.DataFrame({
            "Code": ["TRN-001", "TRN-002"],
            "Training Name": ["Safety Awareness", "Quality Management"],
            "Category": ["Safety", "Quality"],
            "Type": ["Internal", "External"],
            "Duration (hrs)": [4, 8],
            "Status": ["Active", "Active"]
        })
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Add New Training Program")

        with st.form("new_training_form"):
            col1, col2 = st.columns(2)

            with col1:
                training_code = st.text_input("Training Code*", placeholder="TRN-XXX")
                training_name = st.text_input("Training Name*", placeholder="Enter training name")
                category = st.selectbox(
                    "Category*",
                    ["Technical", "Safety", "Quality", "Soft Skills", "Compliance", "Other"]
                )
                type_ = st.selectbox(
                    "Type*",
                    ["Internal", "External", "On-the-job", "E-learning"]
                )

            with col2:
                duration = st.number_input("Duration (hours)", min_value=0.5, value=4.0, step=0.5)
                validity = st.number_input("Validity (months)", min_value=0, value=12, step=1)
                trainer = st.text_input("Trainer", placeholder="Enter trainer name")
                competency_level = st.selectbox(
                    "Competency Level",
                    ["Basic", "Intermediate", "Advanced", "Expert"]
                )

            description = st.text_area("Description", placeholder="Enter training description")
            prerequisites = st.text_area("Prerequisites", placeholder="Enter prerequisites if any")

            submitted = st.form_submit_button("Create Training Program")

            if submitted:
                if training_code and training_name and category and type_:
                    st.success(f"✅ Training program '{training_name}' created successfully!")
                else:
                    st.error("❌ Please fill all required fields")


def show_training_matrix():
    """Show employee training matrix"""
    st.header("Employee Training Matrix")

    tab1, tab2 = st.tabs(["📋 View Matrix", "➕ Assign Training"])

    with tab1:
        st.subheader("Employee Training Requirements")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            employee_filter = st.text_input("Employee ID", placeholder="Search by employee ID")
        with col2:
            dept_filter = st.selectbox(
                "Department",
                ["All", "Testing", "R&D", "Quality", "Maintenance", "Admin"]
            )
        with col3:
            status_filter = st.selectbox(
                "Status",
                ["All", "Required", "In Progress", "Completed", "Expired"]
            )

        # Display matrix
        st.info("📌 Connect to API to fetch training matrix")

        df = pd.DataFrame({
            "Employee ID": ["EMP001", "EMP001", "EMP002"],
            "Employee Name": ["John Doe", "John Doe", "Jane Smith"],
            "Department": ["Testing", "Testing", "R&D"],
            "Training": ["Safety Awareness", "Quality Management", "Technical Skills"],
            "Required": ["Yes", "Yes", "Yes"],
            "Current Level": ["Basic", "Untrained", "Intermediate"],
            "Target Level": ["Basic", "Basic", "Advanced"],
            "Status": ["Completed", "Required", "Gap Exists"]
        })
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Assign Training to Employee")

        with st.form("assign_training_form"):
            col1, col2 = st.columns(2)

            with col1:
                employee_id = st.text_input("Employee ID*")
                employee_name = st.text_input("Employee Name*")
                department = st.selectbox(
                    "Department*",
                    ["Testing", "R&D", "Quality", "Maintenance", "Admin"]
                )
                job_role = st.text_input("Job Role*")

            with col2:
                training_id = st.number_input("Training ID*", min_value=1, value=1)
                required = st.checkbox("Required", value=True)
                target_level = st.selectbox(
                    "Target Level",
                    ["Basic", "Intermediate", "Advanced", "Expert"]
                )

            submitted = st.form_submit_button("Assign Training")

            if submitted:
                if employee_id and employee_name and department and job_role:
                    st.success("✅ Training assigned successfully!")
                else:
                    st.error("❌ Please fill all required fields")


def show_training_attendance():
    """Show training attendance records"""
    st.header("Training Attendance")

    tab1, tab2 = st.tabs(["📋 View Records", "➕ Record Attendance"])

    with tab1:
        st.subheader("Training Attendance Records")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        with col3:
            training_filter = st.text_input("Training ID", placeholder="Filter by training")

        st.info("📌 Connect to API to fetch attendance records")

        df = pd.DataFrame({
            "Date": ["2024-01-15", "2024-01-16"],
            "Training": ["Safety Awareness", "Quality Management"],
            "Employee": ["John Doe", "Jane Smith"],
            "Department": ["Testing", "R&D"],
            "Attendance": ["Present", "Present"],
            "Score": [85.5, 92.0],
            "Result": ["Pass", "Pass"]
        })
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Record Training Attendance")

        with st.form("attendance_form"):
            col1, col2 = st.columns(2)

            with col1:
                training_id = st.number_input("Training ID*", min_value=1)
                training_date = st.date_input("Training Date*", value=date.today())
                employee_id = st.text_input("Employee ID*")
                employee_name = st.text_input("Employee Name*")
                department = st.text_input("Department")

            with col2:
                attendance_status = st.selectbox(
                    "Attendance",
                    ["Present", "Absent", "Partial"]
                )
                pre_test = st.number_input("Pre-test Score", min_value=0.0, max_value=100.0, value=0.0)
                post_test = st.number_input("Post-test Score", min_value=0.0, max_value=100.0, value=0.0)
                practical = st.number_input("Practical Score", min_value=0.0, max_value=100.0, value=0.0)

            trainer_name = st.text_input("Trainer Name")
            feedback_rating = st.slider("Feedback Rating", 1, 5, 4)
            feedback_comments = st.text_area("Feedback Comments")

            submitted = st.form_submit_button("Record Attendance")

            if submitted:
                if training_id and employee_id and employee_name:
                    st.success("✅ Attendance recorded successfully!")
                else:
                    st.error("❌ Please fill all required fields")


def show_competency_gaps():
    """Show competency gap analysis"""
    st.header("🎯 Competency Gap Analysis")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        dept_filter = st.selectbox(
            "Department",
            ["All", "Testing", "R&D", "Quality", "Maintenance", "Admin"]
        )
    with col2:
        employee_filter = st.text_input("Employee ID", placeholder="Search by employee ID")
    with col3:
        gap_status = st.selectbox(
            "Gap Status",
            ["All", "Expired", "Expiring Soon", "Not Trained", "Gap Exists", "Competent"]
        )

    if st.button("🔍 Analyze Gaps"):
        st.info("📌 Connect to API to fetch competency gaps")

    # Summary metrics
    st.subheader("Gap Analysis Summary")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Not Trained", "8", delta="-2")
    with col2:
        st.metric("Expired", "2", delta="+1", delta_color="inverse")
    with col3:
        st.metric("Expiring Soon", "5", delta="+2", delta_color="inverse")
    with col4:
        st.metric("Gap Exists", "15", delta="-3")
    with col5:
        st.metric("Competent", "45", delta="+5")

    # Gap details table
    st.subheader("Detailed Gap Analysis")
    df = pd.DataFrame({
        "Employee": ["EMP001", "EMP002", "EMP003"],
        "Department": ["Testing", "R&D", "Quality"],
        "Training": ["Safety Training", "Technical Skills", "Quality Audit"],
        "Current Level": ["Untrained", "Basic", "Intermediate"],
        "Target Level": ["Basic", "Advanced", "Advanced"],
        "Gap Status": ["Not Trained", "Gap Exists", "Gap Exists"],
        "Valid Until": [None, "2024-06-30", "2024-05-15"]
    })
    st.dataframe(df, use_container_width=True)

    # Export
    if st.button("📥 Export Gap Analysis"):
        st.success("✅ Gap analysis exported successfully!")


def show_certificates():
    """Show certificate generation"""
    st.header("📜 Certificate Generation")

    tab1, tab2 = st.tabs(["🎓 Generate Certificate", "📋 Certificate History"])

    with tab1:
        st.subheader("Generate Training Certificate")

        with st.form("certificate_form"):
            attendance_id = st.number_input("Attendance Record ID*", min_value=1)
            template = st.selectbox(
                "Certificate Template",
                ["default", "professional", "modern"]
            )

            submitted = st.form_submit_button("🎓 Generate Certificate")

            if submitted:
                if attendance_id:
                    st.success(f"✅ Certificate generated for attendance record #{attendance_id}")
                    st.info("📄 Certificate saved at: /uploads/certificates/CERT_XXX.pdf")
                else:
                    st.error("❌ Please provide attendance record ID")

    with tab2:
        st.subheader("Certificate History")
        st.info("📌 Connect to API to fetch certificate history")


def show_qsf_forms():
    """Show QSF forms generation"""
    st.header("📄 QSF Forms Generation")

    form_type = st.selectbox(
        "Select QSF Form",
        [
            "QSF0203 - Training Attendance Record",
            "QSF0205 - Training Effectiveness Evaluation",
            "QSF0206 - Training Needs Assessment"
        ]
    )

    st.markdown("---")

    if "QSF0203" in form_type:
        st.subheader("QSF0203 - Training Attendance Record")

        with st.form("qsf0203_form"):
            col1, col2 = st.columns(2)
            with col1:
                training_id = st.number_input("Training ID*", min_value=1)
            with col2:
                training_date = st.date_input("Training Date*", value=date.today())

            st.write("Attendees (comma-separated employee IDs):")
            attendees_input = st.text_area("Employee IDs", placeholder="EMP001,EMP002,EMP003")

            submitted = st.form_submit_button("Generate QSF0203")

            if submitted:
                st.success("✅ QSF0203 form generated successfully!")

    elif "QSF0205" in form_type:
        st.subheader("QSF0205 - Training Effectiveness Evaluation")

        with st.form("qsf0205_form"):
            attendance_id = st.number_input("Attendance Record ID*", min_value=1)

            st.write("Evaluation Scores (1-5):")
            col1, col2 = st.columns(2)
            with col1:
                knowledge = st.slider("Knowledge Retention", 1, 5, 4)
                practical = st.slider("Practical Application", 1, 5, 4)
            with col2:
                behavior = st.slider("Behavior Change", 1, 5, 4)
                impact = st.slider("Business Impact", 1, 5, 4)

            comments = st.text_area("Evaluator Comments")

            submitted = st.form_submit_button("Generate QSF0205")

            if submitted:
                st.success("✅ QSF0205 form generated successfully!")

    elif "QSF0206" in form_type:
        st.subheader("QSF0206 - Training Needs Assessment")

        with st.form("qsf0206_form"):
            department = st.text_input("Department*")
            period = st.text_input("Assessment Period*", placeholder="Q1 2024")
            prepared_by = st.text_input("Prepared By*")

            st.write("Training Needs:")
            num_needs = st.number_input("Number of training needs", min_value=1, max_value=10, value=1)

            submitted = st.form_submit_button("Generate QSF0206")

            if submitted:
                st.success("✅ QSF0206 form generated successfully!")


if __name__ == "__main__":
    main()
