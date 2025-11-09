"""
Forms and Data Capture page
"""
import streamlit as st
import pandas as pd


def show():
    """Show forms page"""
    st.header("📝 Forms & Data Capture")

    tab1, tab2, tab3 = st.tabs(["📋 Form Templates", "📄 My Records", "➕ Create Form"])

    with tab1:
        st.subheader("Available Form Templates")

        # Sample templates
        templates = pd.DataFrame({
            'Template Code': ['CAL-LOG', 'TEST-REPORT', 'NC-FORM', 'EQ-CARD'],
            'Template Name': [
                'Calibration Log',
                'Test Report Format',
                'Non-Conformance Report',
                'Equipment History Card'
            ],
            'Category': ['Calibration', 'Testing', 'Quality', 'Equipment'],
            'Fields': [12, 25, 15, 18],
            'Records': [45, 123, 8, 67]
        })

        st.dataframe(templates, use_container_width=True)

        selected_template = st.selectbox("Select Template to Fill", templates['Template Name'].tolist())

        if st.button("📝 Fill Form"):
            st.info(f"Opening form: {selected_template}")

    with tab2:
        st.subheader("My Form Records")

        records = pd.DataFrame({
            'Record Number': ['CAL-LOG-2024-0045', 'TEST-REPORT-2024-0123', 'NC-FORM-2024-0008'],
            'Template': ['Calibration Log', 'Test Report Format', 'Non-Conformance Report'],
            'Status': ['Approved', 'Draft', 'In Review'],
            'Created': ['2024-03-01', '2024-03-05', '2024-03-03'],
            'Last Updated': ['2024-03-02', '2024-03-05', '2024-03-04']
        })

        st.dataframe(records, use_container_width=True)

    with tab3:
        st.subheader("Create New Form Template")

        with st.form("create_form_template"):
            form_name = st.text_input("Form Name*")
            form_code = st.text_input("Form Code*", help="Unique identifier, e.g., CAL-LOG")
            form_category = st.selectbox("Category", ["Calibration", "Testing", "Quality", "Equipment", "HR", "Other"])
            form_description = st.text_area("Description")

            st.subheader("Form Fields")

            num_fields = st.number_input("Number of fields", min_value=1, max_value=50, value=5)

            for i in range(int(num_fields)):
                st.markdown(f"**Field {i+1}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text_input(f"Field Name", key=f"field_name_{i}")
                with col2:
                    st.selectbox(f"Field Type", ["Text", "Number", "Date", "Dropdown", "File", "Table"], key=f"field_type_{i}")
                with col3:
                    st.checkbox(f"Required", key=f"field_required_{i}")

            submit = st.form_submit_button("Create Template")

            if submit:
                if form_name and form_code:
                    st.success(f"✅ Form template '{form_name}' created successfully!")
                else:
                    st.error("Please fill all required fields")
