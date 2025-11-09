"""
Test Request Management Page
"""
import streamlit as st
from datetime import date, datetime, timedelta
from utils.api_client import APIClient
import base64


def show():
    """Main test request page"""
    st.title("📝 Test Request Management (QSF0601)")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["➕ Create New", "📋 View All", "🔍 Search"])

    with tab1:
        show_create_form()

    with tab2:
        show_test_request_list()

    with tab3:
        show_search()


def show_create_form():
    """Form to create a new test request"""
    st.subheader("Create New Test Request")

    with st.form("test_request_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Get customers
            try:
                customers = APIClient.get_customers(is_active=True)
                customer_options = {f"{c['customer_name']} ({c['customer_code']})": c['id'] for c in customers}

                if not customer_options:
                    st.warning("⚠️ No customers found. Please create a customer first.")
                    selected_customer = None
                else:
                    selected_customer_name = st.selectbox("Customer *", list(customer_options.keys()))
                    selected_customer = customer_options[selected_customer_name]
            except Exception as e:
                st.error(f"Error loading customers: {e}")
                selected_customer = None

            project_name = st.text_input("Project Name *", placeholder="Enter project name")

            test_type = st.selectbox(
                "Test Type *",
                [
                    "Chemical Analysis",
                    "Microbiological Testing",
                    "Physical Testing",
                    "Mechanical Testing",
                    "Electrical Testing",
                    "Environmental Testing",
                    "Performance Testing",
                    "Safety Testing",
                    "Stability Testing"
                ]
            )

            priority = st.selectbox("Priority *", ["low", "medium", "high", "urgent"])

        with col2:
            request_date = st.date_input("Request Date *", value=date.today())
            due_date = st.date_input("Due Date", value=date.today() + timedelta(days=7))

            requested_by = st.text_input("Requested By *", placeholder="Name of requester")
            department = st.text_input("Department", placeholder="Department name")
            contact_number = st.text_input("Contact Number", placeholder="Phone number")

        description = st.text_area("Description", placeholder="Detailed description of test requirements")
        special_instructions = st.text_area("Special Instructions", placeholder="Any special handling or testing instructions")

        st.markdown("---")
        st.subheader("Test Parameters")

        # Test parameters
        num_parameters = st.number_input("Number of Test Parameters", min_value=1, max_value=20, value=1)

        test_parameters = []
        for i in range(num_parameters):
            st.markdown(f"**Parameter {i+1}**")
            pcol1, pcol2, pcol3 = st.columns(3)

            with pcol1:
                param_name = st.text_input(f"Parameter Name {i+1} *", key=f"param_name_{i}")
            with pcol2:
                param_code = st.text_input(f"Parameter Code {i+1}", key=f"param_code_{i}")
            with pcol3:
                test_method = st.text_input(f"Test Method {i+1}", key=f"test_method_{i}")

            if param_name:
                test_parameters.append({
                    "parameter_name": param_name,
                    "parameter_code": param_code if param_code else None,
                    "test_method": test_method if test_method else None,
                    "quantity": 1
                })

        quote_required = st.checkbox("Generate Quote")

        created_by = st.text_input("Created By *", placeholder="Your name")

        # Submit button
        submitted = st.form_submit_button("Create Test Request", type="primary")

        if submitted:
            # Validation
            if not all([selected_customer, project_name, requested_by, created_by]):
                st.error("❌ Please fill all required fields marked with *")
            elif not test_parameters:
                st.error("❌ Please add at least one test parameter")
            else:
                try:
                    # Create test request
                    request_data = {
                        "customer_id": selected_customer,
                        "project_name": project_name,
                        "test_type": test_type,
                        "priority": priority,
                        "request_date": str(request_date),
                        "due_date": str(due_date) if due_date else None,
                        "description": description if description else None,
                        "special_instructions": special_instructions if special_instructions else None,
                        "requested_by": requested_by,
                        "department": department if department else None,
                        "contact_number": contact_number if contact_number else None,
                        "quote_required": quote_required,
                        "created_by": created_by,
                        "test_parameters": test_parameters
                    }

                    result = APIClient.create_test_request(request_data)

                    st.success(f"✅ Test Request created successfully!")
                    st.success(f"**TRQ Number:** {result['trq_number']}")

                    # Show barcode if available
                    if result.get('barcode_data'):
                        st.image(result['barcode_data'], caption=f"Barcode: {result['trq_number']}")

                    # Generate quote if requested
                    if quote_required and result.get('trq_number'):
                        try:
                            quote = APIClient.generate_quote(result['trq_number'])
                            st.info(f"💰 Quote Generated: {quote['quote_number']}")
                            st.info(f"**Total Amount:** ₹{quote['total_amount']:.2f}")
                        except Exception as e:
                            st.warning(f"Quote generation failed: {e}")

                except Exception as e:
                    st.error(f"❌ Error creating test request: {e}")


def show_test_request_list():
    """Show list of all test requests"""
    st.subheader("All Test Requests")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "draft", "submitted", "approved", "in_progress", "completed", "on_hold", "cancelled"]
        )

    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "low", "medium", "high", "urgent"])

    with col3:
        st.write("")  # Spacing

    try:
        # Get test requests
        filters = {}
        if status_filter != "All":
            filters["status"] = status_filter
        if priority_filter != "All":
            filters["priority"] = priority_filter

        requests = APIClient.get_test_requests(**filters)

        if requests:
            st.write(f"**Total Records:** {len(requests)}")

            # Display as table
            for req in requests:
                with st.expander(f"**{req['trq_number']}** - {req['project_name']} ({req['status'].upper()})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Project:** {req['project_name']}")
                        st.write(f"**Test Type:** {req['test_type']}")
                        st.write(f"**Priority:** {req['priority']}")
                        st.write(f"**Status:** {req['status']}")
                        st.write(f"**Requested By:** {req['requested_by']}")

                    with col2:
                        st.write(f"**Request Date:** {req['request_date']}")
                        st.write(f"**Due Date:** {req.get('due_date', 'N/A')}")
                        if req.get('quote_number'):
                            st.write(f"**Quote:** {req['quote_number']}")
                            st.write(f"**Amount:** ₹{float(req.get('quote_amount', 0)):.2f}")

                    # Show barcode
                    if req.get('barcode_data'):
                        st.image(req['barcode_data'], width=300)

                    # Actions
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        if req['status'] == 'draft' and st.button(f"Submit", key=f"submit_{req['trq_number']}"):
                            try:
                                APIClient.submit_test_request(req['trq_number'], "admin")
                                st.success("Submitted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with action_col2:
                        if req['status'] == 'submitted' and st.button(f"Approve", key=f"approve_{req['trq_number']}"):
                            try:
                                APIClient.approve_test_request(req['trq_number'], "admin")
                                st.success("Approved!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                    with action_col3:
                        if not req.get('quote_number') and st.button(f"Generate Quote", key=f"quote_{req['trq_number']}"):
                            try:
                                quote = APIClient.generate_quote(req['trq_number'])
                                st.success(f"Quote Generated: {quote['quote_number']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        else:
            st.info("No test requests found.")

    except Exception as e:
        st.error(f"Error loading test requests: {e}")


def show_search():
    """Search for specific test request"""
    st.subheader("Search Test Request")

    trq_number = st.text_input("Enter TRQ Number", placeholder="TRQ-2025-00001")

    if st.button("Search", type="primary"):
        if trq_number:
            try:
                req = APIClient.get_test_request(trq_number)

                st.success(f"✅ Test Request Found: {req['trq_number']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Project:** {req['project_name']}")
                    st.write(f"**Test Type:** {req['test_type']}")
                    st.write(f"**Priority:** {req['priority']}")
                    st.write(f"**Status:** {req['status']}")
                    st.write(f"**Requested By:** {req['requested_by']}")
                    st.write(f"**Department:** {req.get('department', 'N/A')}")

                with col2:
                    st.write(f"**Request Date:** {req['request_date']}")
                    st.write(f"**Due Date:** {req.get('due_date', 'N/A')}")
                    st.write(f"**Created At:** {req['created_at']}")

                    if req.get('quote_number'):
                        st.write(f"**Quote Number:** {req['quote_number']}")
                        st.write(f"**Quote Amount:** ₹{float(req.get('quote_amount', 0)):.2f}")

                # Show barcode
                if req.get('barcode_data'):
                    st.image(req['barcode_data'], caption=f"Barcode: {req['trq_number']}")

                # Show test parameters
                if req.get('test_parameters'):
                    st.subheader("Test Parameters")
                    for param in req['test_parameters']:
                        st.write(f"- **{param['parameter_name']}** ({param.get('parameter_code', 'N/A')})")

            except Exception as e:
                st.error(f"❌ Test request not found: {e}")
        else:
            st.warning("Please enter a TRQ number")
