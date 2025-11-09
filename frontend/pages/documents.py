"""
Document Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show documents page"""
    st.header("📄 Document Management System")

    tab1, tab2, tab3 = st.tabs(["📋 All Documents", "➕ Create Document", "📊 Statistics"])

    with tab1:
        st.subheader("Document List")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            level_filter = st.selectbox(
                "Level",
                ["All", "Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
            )
        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Draft", "In Review", "Approved", "Obsolete"]
            )
        with col3:
            search = st.text_input("Search", placeholder="Document number or title")

        # Sample data
        documents = pd.DataFrame({
            'Document Number': ['L1-2024-0001', 'L2-2024-0015', 'L3-2024-0032', 'L4-2024-0089'],
            'Title': ['Quality Manual', 'Calibration Procedure', 'PV Module Testing SOP', 'Equipment Log Template'],
            'Level': ['Level 1', 'Level 2', 'Level 3', 'Level 4'],
            'Status': ['Approved', 'Approved', 'In Review', 'Draft'],
            'Version': ['2.0', '1.5', '1.0', '1.0'],
            'Last Modified': ['2024-01-15', '2024-02-20', '2024-03-01', '2024-03-05']
        })

        st.dataframe(documents, use_container_width=True)

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("📥 Download Selected")
        with col2:
            st.button("✅ Approve Selected")
        with col3:
            st.button("🗑️ Archive Selected")

    with tab2:
        st.subheader("Create New Document")

        with st.form("create_document"):
            doc_title = st.text_input("Document Title*")

            col1, col2 = st.columns(2)
            with col1:
                doc_level = st.selectbox(
                    "Level*",
                    ["Level 1 - Quality Manual, Policy",
                     "Level 2 - Quality System Procedures",
                     "Level 3 - Operation & Test Procedures",
                     "Level 4 - Templates, Formats",
                     "Level 5 - Records"]
                )
            with col2:
                doc_category = st.selectbox(
                    "Category",
                    ["ISO 17025", "ISO 9001", "PV Testing", "Calibration", "General"]
                )

            doc_standard = st.multiselect(
                "Standards (for Level 3)",
                ["IEC 61215", "IEC 61730", "IEC 61853", "IEC 62804", "IEC 62716",
                 "IEC 61701", "IEC 62332", "IEC 63202", "IEC 60904"]
            )

            doc_description = st.text_area("Description")

            doc_file = st.file_uploader("Upload Document", type=['pdf', 'docx', 'xlsx'])

            submit = st.form_submit_button("Create Document")

            if submit:
                if doc_title:
                    st.success(f"✅ Document '{doc_title}' created successfully!")
                else:
                    st.error("Please fill all required fields")

    with tab3:
        st.subheader("Document Statistics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Documents", "234")
        with col2:
            st.metric("Pending Approval", "12")
        with col3:
            st.metric("This Month", "8", "+2")
        with col4:
            st.metric("Obsolete", "15")

        # Chart
        import plotly.express as px
        level_data = pd.DataFrame({
            'Level': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
            'Count': [5, 25, 45, 89, 70]
        })
        fig = px.bar(level_data, x='Level', y='Count', title='Documents by Level')
        st.plotly_chart(fig, use_container_width=True)
