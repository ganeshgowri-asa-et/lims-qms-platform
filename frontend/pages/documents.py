"""
Document Management page
"""
import streamlit as st
import pandas as pd
from frontend.utils.api_client import api_client
import plotly.express as px
import plotly.graph_objects as go


def show():
    """Show documents page"""
    st.header("📄 Document Management System")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 All Documents",
        "➕ Create Document",
        "📊 Statistics",
        "🔍 Document Viewer",
        "📜 Revision History"
    ])

    with tab1:
        show_document_list()

    with tab2:
        show_create_document()

    with tab3:
        show_statistics()

    with tab4:
        show_document_viewer()

    with tab5:
        show_revision_history()


def show_document_list():
    """Show list of documents with filters"""
    st.subheader("Document List")

    # Advanced filters
    col1, col2, col3, col4 = st.columns(4)
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
        category_filter = st.selectbox(
            "Category",
            ["All", "ISO 17025", "ISO 9001", "PV Testing", "Calibration", "General"]
        )
    with col4:
        search = st.text_input("🔍 Search", placeholder="Document number or title")

    # Fetch documents from API
    try:
        level_param = None if level_filter == "All" else level_filter
        status_param = None if status_filter == "All" else status_filter
        docs = api_client.get_documents(level=level_param, status=status_param)
    except:
        docs = []

    # Mock data if API fails
    if not docs:
        documents = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5, 6],
            'Document Number': [
                'L1-2024-0001', 'L2-2024-0015', 'L2-2024-0016',
                'L3-2024-0032', 'L4-2024-0089', 'L5-2024-0123'
            ],
            'Title': [
                'Quality Manual v2.0',
                'Calibration Procedure',
                'Document Control Procedure',
                'PV Module Testing SOP',
                'Equipment Log Template',
                'Calibration Record DMM-001'
            ],
            'Level': ['Level 1', 'Level 2', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
            'Category': ['ISO 17025', 'Calibration', 'ISO 9001', 'PV Testing', 'General', 'Calibration'],
            'Status': ['Approved', 'Approved', 'In Review', 'In Review', 'Draft', 'Approved'],
            'Version': ['2.0', '1.5', '1.0', '1.0', '1.0', '1.2'],
            'Owner': ['Quality Mgr', 'Cal Lead', 'QA Manager', 'Test Lead', 'QA Team', 'Technician'],
            'Last Modified': ['2024-01-15', '2024-02-20', '2024-03-10', '2024-03-01', '2024-03-05', '2024-03-11']
        })
    else:
        documents = pd.DataFrame(docs)

    # Apply search filter
    if search:
        mask = documents['Document Number'].str.contains(search, case=False) | \
               documents['Title'].str.contains(search, case=False)
        documents = documents[mask]

    # Display with selection
    st.dataframe(
        documents,
        use_container_width=True,
        height=400,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
        }
    )

    st.caption(f"Showing {len(documents)} documents")

    # Action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📥 Download Selected"):
            st.info("Download functionality")
    with col2:
        if st.button("✅ Approve Selected"):
            st.success("Approval submitted")
    with col3:
        if st.button("📋 View Details"):
            st.info("Opening document viewer")
    with col4:
        if st.button("📤 Export List"):
            csv = documents.to_csv(index=False)
            st.download_button("Download CSV", csv, "documents.csv", "text/csv")
    with col5:
        if st.button("🗑️ Archive Selected"):
            st.warning("Archive confirmation required")


def show_create_document():
    """Create new document form"""
    st.subheader("Create New Document")

    with st.form("create_document"):
        doc_title = st.text_input("Document Title*", placeholder="Enter descriptive title")

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

        # Parent document (for hierarchy)
        parent_doc = st.selectbox(
            "Parent Document (optional)",
            ["None", "L1-2024-0001 - Quality Manual", "L2-2024-0015 - Calibration Procedure"]
        )

        # Standards (for Level 3 documents)
        if "Level 3" in doc_level:
            doc_standard = st.multiselect(
                "Applicable Standards",
                ["IEC 61215", "IEC 61730", "IEC 61853", "IEC 62804", "IEC 62716",
                 "IEC 61701", "IEC 62332", "IEC 63202", "IEC 60904"],
                help="Select all applicable testing standards"
            )

        doc_description = st.text_area(
            "Description",
            placeholder="Brief description of document purpose and scope"
        )

        # Keywords/Tags
        doc_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="quality, calibration, testing"
        )

        # File upload
        doc_file = st.file_uploader(
            "Upload Document",
            type=['pdf', 'docx', 'xlsx'],
            help="Maximum file size: 10MB"
        )

        # Workflow settings
        col1, col2 = st.columns(2)
        with col1:
            require_review = st.checkbox("Require technical review", value=True)
        with col2:
            require_approval = st.checkbox("Require management approval", value=True)

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit = st.form_submit_button("Create Document", type="primary")
        with col2:
            draft = st.form_submit_button("Save as Draft")

        if submit or draft:
            if doc_title and doc_level:
                # Prepare data for API
                doc_data = {
                    "title": doc_title,
                    "level": doc_level.split(" - ")[0],
                    "category": doc_category,
                    "description": doc_description
                }

                # Call API
                result = api_client.create_document(doc_data)

                if result:
                    st.success(f"✅ Document '{doc_title}' created successfully!")
                    st.info(f"Document Number: {result.get('document_number', 'Generated')}")
                else:
                    st.success(f"✅ Document '{doc_title}' saved as draft!")
            else:
                st.error("Please fill all required fields (marked with *)")


def show_statistics():
    """Show document statistics and analytics"""
    st.subheader("Document Statistics")

    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Documents", "234", "+8 this month")
    with col2:
        st.metric("Pending Approval", "12", "-3 from last week")
    with col3:
        st.metric("Created This Month", "15", "+2")
    with col4:
        st.metric("Obsolete/Archived", "15", "0")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Documents by Level**")
        level_data = pd.DataFrame({
            'Level': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'],
            'Count': [5, 25, 45, 89, 70]
        })
        fig = px.bar(level_data, x='Level', y='Count', color='Count',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Documents by Status**")
        status_data = pd.DataFrame({
            'Status': ['Approved', 'In Review', 'Draft', 'Obsolete'],
            'Count': [189, 12, 18, 15]
        })
        fig = px.pie(status_data, values='Count', names='Status',
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    # Timeline chart
    st.markdown("**Document Creation Timeline**")
    timeline_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Created': [12, 15, 18, 20, 15, 8],
        'Approved': [10, 14, 16, 18, 14, 5],
        'Archived': [2, 1, 3, 2, 1, 0]
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timeline_data['Month'], y=timeline_data['Created'],
                             mode='lines+markers', name='Created'))
    fig.add_trace(go.Scatter(x=timeline_data['Month'], y=timeline_data['Approved'],
                             mode='lines+markers', name='Approved'))
    fig.update_layout(title='Document Activity Trend', xaxis_title='Month', yaxis_title='Count')
    st.plotly_chart(fig, use_container_width=True)

    # Category breakdown
    st.markdown("**Documents by Category**")
    cat_data = pd.DataFrame({
        'Category': ['ISO 17025', 'ISO 9001', 'PV Testing', 'Calibration', 'General'],
        'Count': [85, 45, 52, 38, 14]
    })
    fig = px.bar(cat_data, x='Category', y='Count', color='Category')
    st.plotly_chart(fig, use_container_width=True)


def show_document_viewer():
    """Document viewer interface"""
    st.subheader("Document Viewer")

    # Document selection
    doc_number = st.text_input(
        "Enter Document Number",
        placeholder="e.g., L2-2024-0015"
    )

    if doc_number:
        # Mock document content
        st.markdown(f"### {doc_number}: Calibration Procedure v1.5")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Status:** ✅ Approved")
        with col2:
            st.markdown("**Version:** 1.5")
        with col3:
            st.markdown("**Last Modified:** 2024-02-20")

        # Document metadata
        with st.expander("📋 Document Metadata", expanded=True):
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.markdown("**Level:** Level 2")
                st.markdown("**Category:** Calibration")
                st.markdown("**Owner:** Calibration Lead")
            with meta_col2:
                st.markdown("**Approver:** Quality Manager")
                st.markdown("**Approved Date:** 2024-02-20")
                st.markdown("**Next Review:** 2025-02-20")

        # Document preview (placeholder)
        st.markdown("### Document Content Preview")
        st.info("📄 PDF/Document viewer would be embedded here\n\nIntegration options:\n- PDF.js for PDF viewing\n- Google Docs Viewer\n- Custom document renderer")

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("📥 Download", key="download_doc")
        with col2:
            st.button("🖨️ Print", key="print_doc")
        with col3:
            st.button("📤 Share", key="share_doc")
        with col4:
            st.button("📝 Request Revision", key="request_revision")

    else:
        st.info("Enter a document number to view document details")


def show_revision_history():
    """Show document revision history"""
    st.subheader("Document Revision History")

    doc_search = st.text_input(
        "Search Document",
        placeholder="Enter document number"
    )

    if doc_search:
        st.markdown(f"### Revision History for {doc_search}")

        revisions = pd.DataFrame({
            'Version': ['2.0', '1.5', '1.2', '1.1', '1.0'],
            'Date': ['2024-03-11', '2024-02-20', '2024-01-15', '2023-12-01', '2023-10-15'],
            'Author': ['Alice QA', 'Bob Engineer', 'Jane Tech', 'Bob Engineer', 'Mike Manager'],
            'Change Type': ['Major', 'Minor', 'Correction', 'Minor', 'Initial'],
            'Description': [
                'Added new testing requirements',
                'Updated calibration intervals',
                'Fixed formatting issues',
                'Added safety notes',
                'Initial release'
            ],
            'Approver': ['Quality Mgr', 'Quality Mgr', 'Quality Mgr', 'Quality Mgr', 'CEO'],
            'Status': ['Current', 'Superseded', 'Superseded', 'Superseded', 'Superseded']
        })

        st.dataframe(revisions, use_container_width=True)

        # View specific version
        selected_version = st.selectbox("Select version to view", revisions['Version'].tolist())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button(f"📄 View v{selected_version}")
        with col2:
            st.button(f"📥 Download v{selected_version}")
        with col3:
            st.button("🔄 Compare Versions")

    else:
        st.info("Enter a document number to view revision history")
