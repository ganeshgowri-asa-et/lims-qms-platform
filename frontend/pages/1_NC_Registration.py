"""Non-Conformance Registration Page."""

import streamlit as st
from datetime import datetime, date
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.api_client import APIClient
from config import settings

st.set_page_config(page_title="NC Registration", page_icon="📝", layout="wide")

st.title("📝 Non-Conformance Registration")
st.markdown("---")

# Initialize API client
api = APIClient()

# Registration form
with st.form("nc_registration_form"):
    st.subheader("Basic Information")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input(
            "NC Title *",
            placeholder="Brief description of the non-conformance",
            help="Short title describing the non-conformance"
        )

        source = st.selectbox(
            "Source *",
            options=[
                "internal_audit",
                "customer_complaint",
                "process_monitoring",
                "calibration",
                "testing",
                "supplier",
                "external_audit",
                "other"
            ],
            format_func=lambda x: x.replace("_", " ").title(),
            help="Source of the non-conformance"
        )

        detected_by = st.text_input("Detected By *", help="Name of person who detected the NC")

        department = st.text_input("Department", help="Department where NC was detected")

    with col2:
        severity = st.selectbox(
            "Severity *",
            options=["critical", "major", "minor"],
            format_func=lambda x: x.upper(),
            help="Severity level of the non-conformance"
        )

        detected_date = st.date_input(
            "Detected Date *",
            value=date.today(),
            help="Date when NC was detected"
        )

        location = st.text_input("Location", help="Physical location where NC occurred")

    st.markdown("---")
    st.subheader("Detailed Description")

    description = st.text_area(
        "NC Description *",
        placeholder="Detailed description of what happened, conditions observed, etc.",
        height=150,
        help="Comprehensive description of the non-conformance"
    )

    st.markdown("---")
    st.subheader("Related Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        related_document = st.text_input(
            "Related Document",
            placeholder="e.g., QSF-2024-001",
            help="Related QMS document reference"
        )

    with col2:
        related_equipment = st.text_input(
            "Related Equipment",
            placeholder="e.g., EQP-001",
            help="Equipment ID if applicable"
        )

    with col3:
        related_test_request = st.text_input(
            "Related Test Request",
            placeholder="e.g., TRQ-2024-001",
            help="Test request number if applicable"
        )

    related_batch = st.text_input(
        "Related Batch/Lot",
        placeholder="Batch or lot number",
        help="Batch or lot number affected"
    )

    st.markdown("---")
    st.subheader("Impact Assessment")

    col1, col2 = st.columns(2)

    with col1:
        quantity_affected = st.number_input(
            "Quantity Affected",
            min_value=0,
            value=0,
            help="Number of units/items affected"
        )

    with col2:
        cost_impact = st.number_input(
            "Cost Impact (USD)",
            min_value=0.0,
            value=0.0,
            format="%.2f",
            help="Estimated financial impact"
        )

    impact_description = st.text_area(
        "Impact Description",
        placeholder="Describe the impact on quality, delivery, customer satisfaction, etc.",
        help="Detailed impact assessment"
    )

    st.markdown("---")
    st.subheader("Immediate Actions")

    immediate_action = st.text_area(
        "Immediate/Containment Action",
        placeholder="Describe any immediate actions taken to contain the issue",
        help="Actions taken immediately to prevent further issues"
    )

    st.markdown("---")
    st.subheader("Assignment")

    col1, col2 = st.columns(2)

    with col1:
        assigned_to = st.text_input(
            "Assigned To",
            help="Person responsible for resolving the NC"
        )

        created_by = st.text_input(
            "Registered By *",
            help="Your name (person registering this NC)"
        )

    with col2:
        target_closure_date = st.date_input(
            "Target Closure Date",
            value=None,
            help="Expected date for NC closure"
        )

    st.markdown("---")

    # Submit button
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        submit_button = st.form_submit_button("🚀 Register NC", use_container_width=True, type="primary")

    with col2:
        clear_button = st.form_submit_button("🔄 Clear Form", use_container_width=True)

# Handle form submission
if submit_button:
    # Validation
    if not all([title, description, source, severity, detected_by, created_by]):
        st.error("⚠️ Please fill in all required fields (marked with *)!")
    elif len(title) < 5:
        st.error("⚠️ Title must be at least 5 characters long!")
    elif len(description) < 10:
        st.error("⚠️ Description must be at least 10 characters long!")
    else:
        # Prepare data
        nc_data = {
            "title": title,
            "description": description,
            "source": source,
            "severity": severity,
            "detected_by": detected_by,
            "detected_date": datetime.combine(detected_date, datetime.min.time()).isoformat(),
            "created_by": created_by
        }

        # Add optional fields
        if department:
            nc_data["department"] = department
        if location:
            nc_data["location"] = location
        if related_document:
            nc_data["related_document"] = related_document
        if related_equipment:
            nc_data["related_equipment"] = related_equipment
        if related_test_request:
            nc_data["related_test_request"] = related_test_request
        if related_batch:
            nc_data["related_batch"] = related_batch
        if impact_description:
            nc_data["impact_description"] = impact_description
        if quantity_affected > 0:
            nc_data["quantity_affected"] = quantity_affected
        if cost_impact > 0:
            nc_data["cost_impact"] = cost_impact
        if immediate_action:
            nc_data["immediate_action"] = immediate_action
        if assigned_to:
            nc_data["assigned_to"] = assigned_to
        if target_closure_date:
            nc_data["target_closure_date"] = target_closure_date.isoformat()

        # Submit to API
        try:
            with st.spinner("Registering Non-Conformance..."):
                result = api.create_nc(nc_data)

            st.success(f"✅ Non-Conformance registered successfully!")
            st.info(f"**NC Number:** {result['nc_number']}")

            # Show details
            with st.expander("📋 View NC Details"):
                st.json(result)

            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Register Another NC"):
                    st.rerun()
            with col2:
                if st.button("📋 View All NCs"):
                    st.switch_page("pages/2_NC_List.py")

        except Exception as e:
            st.error(f"❌ Error registering NC: {str(e)}")
            st.exception(e)

if clear_button:
    st.rerun()

# Sidebar - Help
with st.sidebar:
    st.markdown("### 📖 Help")
    st.info("""
    **NC Severity Levels:**
    - **CRITICAL**: Major impact on safety, compliance, or customer satisfaction
    - **MAJOR**: Significant impact on quality or operations
    - **MINOR**: Limited impact, can be easily corrected

    **Required Fields:**
    - NC Title
    - Description
    - Source
    - Severity
    - Detected By
    - Registered By
    """)

    st.markdown("### 💡 Tips")
    st.success("""
    - Be specific in your description
    - Include all relevant details
    - Document immediate actions taken
    - Assign to appropriate person
    - Set realistic closure dates
    """)
