"""Document Management System UI."""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
sys.path.append('..')
from utils.api_client import APIClient

st.set_page_config(page_title="Document Management", page_icon="📄", layout="wide")

# Initialize API client
api = APIClient()

st.title("📄 Document Management System")
st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["📋 Document List", "➕ Create Document", "🔍 Search", "✅ Approval Queue"])

# Tab 1: Document List
with tab1:
    st.header("Document List")

    # Refresh button
    if st.button("🔄 Refresh"):
        st.rerun()

    # Fetch documents
    try:
        documents = api.get_documents()

        if documents and not isinstance(documents, dict):
            # Convert to DataFrame
            df = pd.DataFrame(documents)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Documents", len(df))
            with col2:
                approved = len(df[df['status'] == 'approved']) if 'status' in df.columns else 0
                st.metric("Approved", approved)
            with col3:
                draft = len(df[df['status'] == 'draft']) if 'status' in df.columns else 0
                st.metric("Draft", draft)
            with col4:
                pending = len(df[df['status'].str.contains('pending', case=False)]) if 'status' in df.columns else 0
                st.metric("Pending Approval", pending)

            st.markdown("---")

            # Display table
            display_cols = ['doc_number', 'title', 'type', 'current_revision', 'status', 'owner', 'created_at']
            available_cols = [col for col in display_cols if col in df.columns]

            if available_cols:
                st.dataframe(
                    df[available_cols],
                    use_container_width=True,
                    hide_index=True,
                )

                # Document details
                st.markdown("---")
                st.subheader("Document Details")

                doc_numbers = df['doc_number'].tolist() if 'doc_number' in df.columns else []
                selected_doc = st.selectbox("Select document to view details:", doc_numbers)

                if selected_doc:
                    doc_data = df[df['doc_number'] == selected_doc].iloc[0]
                    doc_id = doc_data['id']

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Document Number:** {doc_data.get('doc_number', 'N/A')}")
                        st.write(f"**Title:** {doc_data.get('title', 'N/A')}")
                        st.write(f"**Type:** {doc_data.get('type', 'N/A')}")
                        st.write(f"**Revision:** {doc_data.get('current_revision', 'N/A')}")
                        st.write(f"**Status:** {doc_data.get('status', 'N/A')}")

                    with col2:
                        st.write(f"**Owner:** {doc_data.get('owner', 'N/A')}")
                        st.write(f"**Department:** {doc_data.get('department', 'N/A')}")
                        st.write(f"**Created By:** {doc_data.get('created_by', 'N/A')}")
                        st.write(f"**Approved By:** {doc_data.get('approved_by', 'N/A')}")

                    if doc_data.get('description'):
                        st.write(f"**Description:** {doc_data.get('description')}")
        else:
            st.info("No documents found. Create your first document using the 'Create Document' tab.")
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")
        st.info("Make sure the backend API is running at http://localhost:8000")

# Tab 2: Create Document
with tab2:
    st.header("Create New Document")

    with st.form("create_document_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Document Title*", placeholder="Enter document title")
            doc_type = st.selectbox(
                "Document Type*",
                ["procedure", "form", "policy", "manual", "work_instruction", "specification", "record"]
            )
            owner = st.text_input("Owner*", placeholder="Document owner name")
            department = st.text_input("Department", placeholder="Department name")

        with col2:
            created_by = st.text_input("Created By*", placeholder="Your name")
            keywords = st.text_input("Keywords", placeholder="Comma-separated keywords")
            description = st.text_area("Description", placeholder="Document description")

        submitted = st.form_submit_button("Create Document")

        if submitted:
            if not title or not doc_type or not owner or not created_by:
                st.error("Please fill in all required fields marked with *")
            else:
                document_data = {
                    "title": title,
                    "type": doc_type,
                    "owner": owner,
                    "department": department,
                    "created_by": created_by,
                    "keywords": keywords,
                    "description": description,
                }

                try:
                    result = api.create_document(document_data)

                    if "error" in result:
                        st.error(f"Error creating document: {result['error']}")
                    else:
                        st.success(f"✅ Document created successfully! Document Number: {result.get('doc_number', 'N/A')}")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 3: Search
with tab3:
    st.header("Search Documents")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("🔍 Search term", placeholder="Enter search term")

    with col2:
        search_type = st.selectbox(
            "Document Type",
            ["All", "procedure", "form", "policy", "manual", "work_instruction", "specification", "record"]
        )

    with col3:
        search_status = st.selectbox(
            "Status",
            ["All", "draft", "pending_review", "pending_approval", "approved", "obsolete"]
        )

    if st.button("🔍 Search"):
        try:
            results = api.search_documents(
                search_term=search_term if search_term else None,
                doc_type=search_type if search_type != "All" else None,
                status=search_status if search_status != "All" else None,
            )

            if results and not isinstance(results, dict):
                st.success(f"Found {len(results)} documents")
                df = pd.DataFrame(results)
                display_cols = ['doc_number', 'title', 'type', 'current_revision', 'status', 'owner']
                available_cols = [col for col in display_cols if col in df.columns]
                st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
            else:
                st.info("No documents found matching your criteria")
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")

# Tab 4: Approval Queue
with tab4:
    st.header("Document Approval Queue")

    try:
        documents = api.get_documents()

        if documents and not isinstance(documents, dict):
            df = pd.DataFrame(documents)

            # Filter pending documents
            if 'status' in df.columns:
                pending_docs = df[df['status'].str.contains('pending', case=False)]

                if not pending_docs.empty:
                    st.write(f"**{len(pending_docs)} documents pending approval**")

                    for idx, doc in pending_docs.iterrows():
                        with st.expander(f"{doc.get('doc_number', 'N/A')} - {doc.get('title', 'N/A')}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**Status:** {doc.get('status', 'N/A')}")
                                st.write(f"**Owner:** {doc.get('owner', 'N/A')}")
                                st.write(f"**Created By:** {doc.get('created_by', 'N/A')}")

                            with col2:
                                st.write(f"**Type:** {doc.get('type', 'N/A')}")
                                st.write(f"**Revision:** {doc.get('current_revision', 'N/A')}")
                                st.write(f"**Department:** {doc.get('department', 'N/A')}")

                            # Approval actions
                            st.markdown("---")
                            action_col1, action_col2, action_col3 = st.columns(3)

                            with action_col1:
                                reviewer_name = st.text_input(
                                    "Your Name",
                                    key=f"reviewer_{doc['id']}",
                                    placeholder="Enter your name"
                                )

                            with action_col2:
                                action = st.selectbox(
                                    "Action",
                                    ["Select", "review", "approve", "reject"],
                                    key=f"action_{doc['id']}"
                                )

                            with action_col3:
                                if st.button("Submit", key=f"submit_{doc['id']}"):
                                    if action != "Select" and reviewer_name:
                                        approval_data = {
                                            "action": action,
                                            "reviewer_name": reviewer_name,
                                        }
                                        result = api.approve_document(doc['id'], approval_data)

                                        if "error" not in result:
                                            st.success(f"✅ Document {action}ed successfully!")
                                            st.rerun()
                                        else:
                                            st.error(f"Error: {result['error']}")
                                    else:
                                        st.warning("Please enter your name and select an action")
                else:
                    st.info("No documents pending approval")
            else:
                st.info("No documents available")
    except Exception as e:
        st.error(f"Error loading approval queue: {str(e)}")
