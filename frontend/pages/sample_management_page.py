"""
Sample Management Page
"""
import streamlit as st
from datetime import date
from decimal import Decimal
from utils.api_client import APIClient


def show():
    """Main sample management page"""
    st.title("🧪 Sample Management")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["➕ Create Sample", "📋 Track Samples", "🔍 Search"])

    with tab1:
        show_create_sample_form()

    with tab2:
        show_sample_tracking()

    with tab3:
        show_search()


def show_create_sample_form():
    """Form to create a new sample"""
    st.subheader("Register New Sample")

    with st.form("sample_form"):
        # Get test requests
        try:
            test_requests = APIClient.get_test_requests(status="approved")
            trq_options = {f"{tr['trq_number']} - {tr['project_name']}": tr['id'] for tr in test_requests}

            if not trq_options:
                st.warning("⚠️ No approved test requests found. Please approve a test request first.")
                selected_trq = None
            else:
                selected_trq_name = st.selectbox("Test Request *", list(trq_options.keys()))
                selected_trq = trq_options[selected_trq_name]
        except Exception as e:
            st.error(f"Error loading test requests: {e}")
            selected_trq = None

        col1, col2 = st.columns(2)

        with col1:
            sample_name = st.text_input("Sample Name *", placeholder="e.g., Water Sample, Steel Rod")
            sample_type = st.selectbox(
                "Sample Type *",
                ["Solid", "Liquid", "Gas", "Powder", "Semi-Solid", "Other"]
            )
            sample_description = st.text_area("Sample Description", placeholder="Detailed description")

        with col2:
            quantity = st.number_input("Quantity *", min_value=0.01, value=1.0, step=0.01)
            unit = st.selectbox(
                "Unit *",
                ["mg", "g", "kg", "ml", "L", "pieces", "units", "samples"]
            )

        st.markdown("---")
        st.subheader("Additional Information")

        col3, col4 = st.columns(2)

        with col3:
            batch_number = st.text_input("Batch Number", placeholder="Batch/Lot number")
            lot_number = st.text_input("Lot Number", placeholder="Lot number")
            manufacturing_date = st.date_input("Manufacturing Date", value=None)

        with col4:
            expiry_date = st.date_input("Expiry Date", value=None)
            condition_on_receipt = st.text_input("Condition on Receipt", placeholder="e.g., Good, Damaged")
            storage_condition = st.text_input("Storage Condition", placeholder="e.g., Room temp, Refrigerated")
            storage_location = st.text_input("Storage Location", placeholder="e.g., Rack A1, Freezer 2")

        remarks = st.text_area("Remarks", placeholder="Any additional notes")

        created_by = st.text_input("Created By *", placeholder="Your name")

        # Submit button
        submitted = st.form_submit_button("Register Sample", type="primary")

        if submitted:
            # Validation
            if not all([selected_trq, sample_name, sample_type, quantity, unit, created_by]):
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    # Create sample
                    sample_data = {
                        "test_request_id": selected_trq,
                        "sample_name": sample_name,
                        "sample_type": sample_type,
                        "sample_description": sample_description if sample_description else None,
                        "quantity": str(quantity),
                        "unit": unit,
                        "condition_on_receipt": condition_on_receipt if condition_on_receipt else None,
                        "storage_condition": storage_condition if storage_condition else None,
                        "expiry_date": str(expiry_date) if expiry_date else None,
                        "batch_number": batch_number if batch_number else None,
                        "lot_number": lot_number if lot_number else None,
                        "manufacturing_date": str(manufacturing_date) if manufacturing_date else None,
                        "storage_location": storage_location if storage_location else None,
                        "remarks": remarks if remarks else None,
                        "created_by": created_by
                    }

                    result = APIClient.create_sample(sample_data)

                    st.success(f"✅ Sample registered successfully!")
                    st.success(f"**Sample Number:** {result['sample_number']}")

                    # Show barcode
                    if result.get('barcode_data'):
                        st.image(result['barcode_data'], caption=f"Barcode: {result['sample_number']}")

                except Exception as e:
                    st.error(f"❌ Error creating sample: {e}")


def show_sample_tracking():
    """Show sample tracking and status updates"""
    st.subheader("Sample Tracking")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "received", "in_testing", "tested", "completed", "rejected", "archived"]
        )

    with col2:
        sample_type_filter = st.selectbox(
            "Filter by Type",
            ["All", "Solid", "Liquid", "Gas", "Powder", "Semi-Solid", "Other"]
        )

    try:
        # Get samples
        filters = {}
        if status_filter != "All":
            filters["status"] = status_filter
        if sample_type_filter != "All":
            filters["sample_type"] = sample_type_filter

        samples = APIClient.get_samples(**filters)

        if samples:
            st.write(f"**Total Samples:** {len(samples)}")

            # Display as cards
            for sample in samples:
                with st.expander(f"**{sample['sample_number']}** - {sample['sample_name']} ({sample['status'].upper()})"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Sample Name:** {sample['sample_name']}")
                        st.write(f"**Type:** {sample['sample_type']}")
                        st.write(f"**Quantity:** {sample['quantity']} {sample['unit']}")
                        st.write(f"**Status:** {sample['status']}")

                    with col2:
                        st.write(f"**Batch:** {sample.get('batch_number', 'N/A')}")
                        st.write(f"**Storage:** {sample.get('storage_location', 'N/A')}")
                        st.write(f"**Condition:** {sample.get('storage_condition', 'N/A')}")

                    with col3:
                        st.write(f"**Created:** {sample['created_at']}")
                        if sample.get('received_date'):
                            st.write(f"**Received:** {sample['received_date']}")
                        if sample.get('testing_start_date'):
                            st.write(f"**Testing Started:** {sample['testing_start_date']}")
                        if sample.get('testing_end_date'):
                            st.write(f"**Testing Ended:** {sample['testing_end_date']}")

                    # Show barcode
                    if sample.get('barcode_data'):
                        st.image(sample['barcode_data'], width=300)

                    # Status update buttons
                    st.markdown("**Actions:**")
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if sample['status'] == 'pending' and st.button(f"Mark Received", key=f"receive_{sample['sample_number']}"):
                            try:
                                APIClient.receive_sample(sample['sample_number'], "admin")
                                st.success("Sample received!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with action_col2:
                        if sample['status'] == 'received' and st.button(f"Start Testing", key=f"start_{sample['sample_number']}"):
                            try:
                                APIClient.start_testing(sample['sample_number'])
                                st.success("Testing started!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with action_col3:
                        if sample['status'] == 'in_testing' and st.button(f"Complete Testing", key=f"complete_{sample['sample_number']}"):
                            try:
                                APIClient.complete_testing(sample['sample_number'])
                                st.success("Testing completed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        else:
            st.info("No samples found.")

    except Exception as e:
        st.error(f"Error loading samples: {e}")


def show_search():
    """Search for specific sample"""
    st.subheader("Search Sample")

    sample_number = st.text_input("Enter Sample Number", placeholder="SMP-2025-00001")

    if st.button("Search", type="primary"):
        if sample_number:
            try:
                sample = APIClient.get_sample(sample_number)

                st.success(f"✅ Sample Found: {sample['sample_number']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Sample Name:** {sample['sample_name']}")
                    st.write(f"**Type:** {sample['sample_type']}")
                    st.write(f"**Quantity:** {sample['quantity']} {sample['unit']}")
                    st.write(f"**Status:** {sample['status']}")
                    st.write(f"**Batch Number:** {sample.get('batch_number', 'N/A')}")
                    st.write(f"**Lot Number:** {sample.get('lot_number', 'N/A')}")

                with col2:
                    st.write(f"**Storage Location:** {sample.get('storage_location', 'N/A')}")
                    st.write(f"**Storage Condition:** {sample.get('storage_condition', 'N/A')}")
                    st.write(f"**Manufacturing Date:** {sample.get('manufacturing_date', 'N/A')}")
                    st.write(f"**Expiry Date:** {sample.get('expiry_date', 'N/A')}")
                    st.write(f"**Created At:** {sample['created_at']}")

                # Show barcode
                if sample.get('barcode_data'):
                    st.image(sample['barcode_data'], caption=f"Barcode: {sample['sample_number']}")

                # Show description and remarks
                if sample.get('sample_description'):
                    st.write(f"**Description:** {sample['sample_description']}")
                if sample.get('remarks'):
                    st.write(f"**Remarks:** {sample['remarks']}")

            except Exception as e:
                st.error(f"❌ Sample not found: {e}")
        else:
            st.warning("Please enter a sample number")
