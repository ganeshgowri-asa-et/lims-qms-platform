"""
Main Streamlit application for Document Management System
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import hashlib

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="QMS Document Management",
    page_icon="📄",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("📄 QMS Document Management")
page = st.sidebar.radio(
    "Navigation",
    ["📝 Create Document", "📋 Document List", "✅ Approval Queue", "🔍 Search Documents"]
)

# Helper functions
def create_signature_hash(signer_name: str, signer_email: str) -> str:
    """Create a simple signature hash"""
    data = f"{signer_name}{signer_email}{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


# Page: Create Document
if page == "📝 Create Document":
    st.title("📝 Create New Document")

    with st.form("create_document_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Document Title *", placeholder="Enter document title")
            doc_type = st.selectbox(
                "Document Type *",
                ["PROCEDURE", "WORK_INSTRUCTION", "FORM", "SPECIFICATION",
                 "MANUAL", "POLICY", "RECORD", "REPORT"]
            )
            owner = st.text_input("Document Owner *", placeholder="Enter owner name")

        with col2:
            department = st.text_input("Department", placeholder="Enter department")
            description = st.text_area("Description", placeholder="Enter document description")

        content_text = st.text_area(
            "Document Content",
            placeholder="Enter document content for full-text search",
            height=200
        )

        submitted = st.form_submit_button("Create Document", type="primary")

        if submitted:
            if not title or not owner:
                st.error("Title and Owner are required fields")
            else:
                payload = {
                    "title": title,
                    "type": doc_type,
                    "owner": owner,
                    "department": department if department else None,
                    "description": description if description else None,
                    "content_text": content_text if content_text else None
                }

                try:
                    response = requests.post(f"{API_BASE_URL}/documents/", json=payload)
                    if response.status_code == 201:
                        doc = response.json()
                        st.success(f"✅ Document created successfully!")
                        st.info(f"Document Number: **{doc['doc_number']}**")
                        st.info(f"Version: **{doc['version_string']}**")
                    else:
                        st.error(f"Failed to create document: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# Page: Document List
elif page == "📋 Document List":
    st.title("📋 Document List")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "DRAFT", "PENDING_REVIEW", "PENDING_APPROVAL",
             "APPROVED", "EFFECTIVE", "OBSOLETE"]
        )

    with col2:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All", "PROCEDURE", "WORK_INSTRUCTION", "FORM",
             "SPECIFICATION", "MANUAL", "POLICY", "RECORD", "REPORT"]
        )

    with col3:
        owner_filter = st.text_input("Filter by Owner")

    # Build query parameters
    params = {}
    if status_filter != "All":
        params["status"] = status_filter
    if type_filter != "All":
        params["doc_type"] = type_filter
    if owner_filter:
        params["owner"] = owner_filter

    # Fetch documents
    try:
        response = requests.get(f"{API_BASE_URL}/documents/", params=params)
        if response.status_code == 200:
            documents = response.json()

            if documents:
                # Convert to DataFrame
                df = pd.DataFrame(documents)

                # Format dates
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

                # Select and rename columns for display
                display_columns = {
                    'doc_number': 'Doc Number',
                    'title': 'Title',
                    'type': 'Type',
                    'version_string': 'Version',
                    'status': 'Status',
                    'owner': 'Owner',
                    'created_at': 'Created'
                }

                df_display = df[list(display_columns.keys())].rename(columns=display_columns)

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )

                # Document details expander
                st.subheader("Document Actions")
                doc_id = st.number_input("Enter Document ID for details", min_value=1, step=1)

                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("View Details"):
                        detail_response = requests.get(f"{API_BASE_URL}/documents/{doc_id}")
                        if detail_response.status_code == 200:
                            doc_detail = detail_response.json()
                            st.json(doc_detail)
                        else:
                            st.error("Document not found")

                with col2:
                    if st.button("View Revisions"):
                        rev_response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/revisions")
                        if rev_response.status_code == 200:
                            revisions = rev_response.json()
                            if revisions:
                                st.write(pd.DataFrame(revisions))
                            else:
                                st.info("No revisions found")
                        else:
                            st.error("Failed to fetch revisions")

                with col3:
                    if st.button("View Signatures"):
                        sig_response = requests.get(f"{API_BASE_URL}/documents/{doc_id}/signatures")
                        if sig_response.status_code == 200:
                            signatures = sig_response.json()
                            if signatures:
                                st.write(pd.DataFrame(signatures))
                            else:
                                st.info("No signatures found")
                        else:
                            st.error("Failed to fetch signatures")

            else:
                st.info("No documents found")
        else:
            st.error(f"Failed to fetch documents: {response.text}")
    except Exception as e:
        st.error(f"Error: {str(e)}")


# Page: Approval Queue
elif page == "✅ Approval Queue":
    st.title("✅ Approval Queue")

    st.info("📋 Documents pending your review and approval")

    # Get pending documents
    try:
        # Get documents pending review
        pending_review = requests.get(
            f"{API_BASE_URL}/documents/",
            params={"status": "PENDING_REVIEW"}
        ).json()

        # Get documents pending approval
        pending_approval = requests.get(
            f"{API_BASE_URL}/documents/",
            params={"status": "PENDING_APPROVAL"}
        ).json()

        # Tabs for different approval stages
        tab1, tab2, tab3 = st.tabs(["Pending Review (Checker)", "Pending Approval (Approver)", "Sign Document"])

        with tab1:
            st.subheader("Documents Pending Review")
            if pending_review:
                df = pd.DataFrame(pending_review)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df[['doc_number', 'title', 'type', 'version_string', 'owner']], use_container_width=True)
            else:
                st.info("No documents pending review")

        with tab2:
            st.subheader("Documents Pending Approval")
            if pending_approval:
                df = pd.DataFrame(pending_approval)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df[['doc_number', 'title', 'type', 'version_string', 'owner']], use_container_width=True)
            else:
                st.info("No documents pending approval")

        with tab3:
            st.subheader("Add Signature to Document")

            with st.form("signature_form"):
                doc_id = st.number_input("Document ID", min_value=1, step=1)

                col1, col2 = st.columns(2)

                with col1:
                    role = st.selectbox("Your Role", ["DOER", "CHECKER", "APPROVER"])
                    signer_name = st.text_input("Your Name *")

                with col2:
                    signer_email = st.text_input("Your Email *", placeholder="name@example.com")
                    is_approved = st.checkbox("Approve Document", value=True)

                comments = st.text_area("Comments", placeholder="Enter any comments")

                submitted = st.form_submit_button("Add Signature", type="primary")

                if submitted:
                    if not signer_name or not signer_email:
                        st.error("Name and Email are required")
                    else:
                        # Generate signature hash
                        signature_hash = create_signature_hash(signer_name, signer_email)

                        payload = {
                            "role": role,
                            "signer": signer_name,
                            "signer_email": signer_email,
                            "signature_hash": signature_hash,
                            "comments": comments if comments else None,
                            "is_approved": is_approved
                        }

                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/documents/{doc_id}/approve",
                                json=payload
                            )
                            if response.status_code == 200:
                                st.success("✅ Signature added successfully!")
                                sig = response.json()
                                st.info(f"Role: {sig['role']} | Timestamp: {sig['signature_timestamp']}")
                            else:
                                st.error(f"Failed to add signature: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")


# Page: Search Documents
elif page == "🔍 Search Documents":
    st.title("🔍 Search Documents")

    search_query = st.text_input(
        "Search",
        placeholder="Enter search terms (title, description, content)",
        help="Full-text search across all documents"
    )

    if st.button("Search", type="primary"):
        if search_query:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/documents/search/",
                    params={"q": search_query, "limit": 100}
                )

                if response.status_code == 200:
                    results = response.json()

                    if results:
                        st.success(f"Found {len(results)} documents")

                        # Display results
                        for result in results:
                            with st.expander(f"📄 {result['doc_number']} - {result['title']}"):
                                st.write(f"**Score:** {result.get('score', 'N/A'):.2f}")
                                st.write(f"**Document ID:** {result['doc_id']}")

                                # Get full document details
                                doc_response = requests.get(
                                    f"{API_BASE_URL}/documents/{result['doc_id']}"
                                )
                                if doc_response.status_code == 200:
                                    doc = doc_response.json()
                                    st.write(f"**Type:** {doc['type']}")
                                    st.write(f"**Version:** {doc['version_string']}")
                                    st.write(f"**Status:** {doc['status']}")
                                    st.write(f"**Owner:** {doc['owner']}")
                                    if doc.get('description'):
                                        st.write(f"**Description:** {doc['description']}")
                    else:
                        st.info("No documents found matching your search")
                else:
                    st.error(f"Search failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a search query")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **LIMS-QMS Platform**

    Document Management System

    Version 1.0.0
    """
)
