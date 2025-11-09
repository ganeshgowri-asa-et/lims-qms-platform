"""
Traceability & Audit Trail page
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from frontend.utils.api_client import api_client


def show():
    """Show traceability and audit trail page"""
    st.header("🔍 Traceability & Audit Trail")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌳 Document Lineage",
        "📜 Audit Trail",
        "🔄 Change History",
        "📊 Traceability Matrix"
    ])

    with tab1:
        show_document_lineage()

    with tab2:
        show_audit_trail()

    with tab3:
        show_change_history()

    with tab4:
        show_traceability_matrix()


def show_document_lineage():
    """Show document lineage visualization"""
    st.subheader("Document Lineage & Relationships")

    # Search for document
    col1, col2 = st.columns([3, 1])
    with col1:
        search_doc = st.text_input(
            "Enter Document Number",
            placeholder="e.g., DOC-2024-0045"
        )
    with col2:
        entity_type = st.selectbox(
            "Type",
            ["Document", "Form", "Project", "Equipment"]
        )

    if search_doc:
        st.markdown("### Lineage Tree")

        # Create interactive lineage tree using plotly
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[
                    "Quality Manual v1.0",
                    "Quality Manual v2.0",
                    "Calibration Procedure v1.0",
                    "Calibration Procedure v1.5",
                    "Cal Log Template v1.0",
                    "Cal Record #123",
                    "Cal Record #124",
                    "PV Testing SOP v1.0"
                ],
                color=["#1f77b4", "#1f77b4", "#2ca02c", "#2ca02c",
                       "#ff7f0e", "#d62728", "#d62728", "#2ca02c"]
            ),
            link=dict(
                source=[0, 1, 2, 3, 4, 4, 1],
                target=[1, 2, 3, 4, 5, 6, 7],
                value=[1, 1, 1, 1, 1, 1, 1]
            )
        ))

        fig.update_layout(
            title="Document Lineage & Dependencies",
            font_size=10,
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Document relationships
        st.markdown("### Related Documents")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Parent Documents**")
            parents = pd.DataFrame({
                'Document': ['Quality Manual v2.0', 'ISO 17025 Requirements'],
                'Relationship': ['Derived From', 'Based On'],
                'Level': ['Level 1', 'Standard']
            })
            st.dataframe(parents, use_container_width=True)

        with col2:
            st.markdown("**Child Documents**")
            children = pd.DataFrame({
                'Document': ['Cal Log Template', 'Cal Record #123'],
                'Relationship': ['Template', 'Record'],
                'Level': ['Level 4', 'Level 5']
            })
            st.dataframe(children, use_container_width=True)

        # Cross-references
        st.markdown("### Cross-References")
        references = pd.DataFrame({
            'Referenced By': [
                'PV Testing SOP v1.0',
                'Equipment Manual DMM-001',
                'Training Material TRN-2024-001'
            ],
            'Section': ['Section 3.2', 'Appendix A', 'Module 2'],
            'Type': ['Procedure', 'Reference', 'Training']
        })
        st.dataframe(references, use_container_width=True)

    else:
        st.info("Enter a document number to view lineage and relationships")


def show_audit_trail():
    """Show audit trail"""
    st.subheader("Audit Trail Viewer")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        entity_filter = st.selectbox(
            "Entity Type",
            ["All", "Document", "Form", "User", "Equipment", "Project"]
        )

    with col2:
        action_filter = st.selectbox(
            "Action",
            ["All", "Create", "Update", "Delete", "Approve", "Reject", "Sign", "View"]
        )

    with col3:
        user_filter = st.text_input("User", placeholder="Filter by user")

    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", datetime(2024, 1, 1))
    with col2:
        end_date = st.date_input("To", datetime.now())

    # Fetch audit trail
    audit_data = pd.DataFrame({
        'Timestamp': [
            '2024-03-11 14:32:15',
            '2024-03-11 14:30:22',
            '2024-03-11 14:15:08',
            '2024-03-11 13:45:33',
            '2024-03-11 12:20:18',
            '2024-03-11 11:05:44',
            '2024-03-11 10:30:12',
            '2024-03-11 09:15:27'
        ],
        'User': [
            'alice.qa@company.com',
            'bob.engineer@company.com',
            'jane.tech@company.com',
            'alice.qa@company.com',
            'mike.manager@company.com',
            'jane.tech@company.com',
            'bob.engineer@company.com',
            'sarah.admin@company.com'
        ],
        'Action': [
            'Approve',
            'Update',
            'Create',
            'View',
            'Sign',
            'Upload',
            'Delete',
            'Create'
        ],
        'Entity Type': [
            'Document',
            'Form',
            'Document',
            'Form',
            'Document',
            'Document',
            'User',
            'Project'
        ],
        'Entity ID': [
            'DOC-2024-0045',
            'CAL-LOG-2024-0123',
            'DOC-2024-0046',
            'CAL-LOG-2024-0122',
            'DOC-2024-0044',
            'DOC-2024-0045',
            'USR-2024-0023',
            'PRJ-2024-0012'
        ],
        'IP Address': [
            '192.168.1.105',
            '192.168.1.110',
            '192.168.1.108',
            '192.168.1.105',
            '192.168.1.102',
            '192.168.1.108',
            '192.168.1.110',
            '192.168.1.101'
        ],
        'Details': [
            'Document approved for publication',
            'Updated field: Calibration Date',
            'New document created',
            'Document viewed/downloaded',
            'Management signature applied',
            'Uploaded file: procedure_v1.pdf',
            'User account deactivated',
            'New project created: PV Module Testing'
        ]
    })

    # Display audit trail
    st.dataframe(audit_data, use_container_width=True, height=400)

    # Summary statistics
    st.markdown("### Activity Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Actions", len(audit_data))
    with col2:
        st.metric("Unique Users", audit_data['User'].nunique())
    with col3:
        st.metric("Documents Modified", 5)
    with col4:
        st.metric("Approvals", len(audit_data[audit_data['Action'] == 'Approve']))

    # Export
    if st.button("📥 Export Audit Trail"):
        csv = audit_data.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv"
        )


def show_change_history():
    """Show change history with diff view"""
    st.subheader("Change History & Diff View")

    # Select document
    doc_number = st.text_input(
        "Document Number",
        placeholder="Enter document number to view change history"
    )

    if doc_number:
        # Version history
        st.markdown("### Version History")

        versions = pd.DataFrame({
            'Version': ['2.0', '1.5', '1.2', '1.1', '1.0'],
            'Date': [
                '2024-03-11',
                '2024-02-20',
                '2024-01-15',
                '2023-12-01',
                '2023-10-15'
            ],
            'Author': [
                'Alice QA',
                'Bob Engineer',
                'Jane Tech',
                'Bob Engineer',
                'Mike Manager'
            ],
            'Change Summary': [
                'Added new calibration requirements',
                'Updated measurement procedures',
                'Corrected typos and formatting',
                'Added safety warnings',
                'Initial version'
            ],
            'Status': [
                'Current',
                'Superseded',
                'Superseded',
                'Superseded',
                'Superseded'
            ]
        })

        st.dataframe(versions, use_container_width=True)

        # Compare versions
        st.markdown("### Compare Versions")

        col1, col2 = st.columns(2)
        with col1:
            ver1 = st.selectbox("Version A", versions['Version'].tolist(), index=1)
        with col2:
            ver2 = st.selectbox("Version B", versions['Version'].tolist(), index=0)

        if st.button("Show Differences"):
            st.markdown("### Changes Detected")

            # Mock diff view
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Version {ver1}**")
                st.text_area(
                    "",
                    value="""3.2 Calibration Procedure
- Calibrate equipment annually
- Use certified reference standards
- Record all measurements""",
                    height=200,
                    key="ver1_text"
                )

            with col2:
                st.markdown(f"**Version {ver2}**")
                st.text_area(
                    "",
                    value="""3.2 Calibration Procedure
- Calibrate equipment annually or as specified
- Use NABL certified reference standards
- Record all measurements with uncertainties
- Perform intermediate checks quarterly""",
                    height=200,
                    key="ver2_text"
                )

            # Highlighted changes
            st.markdown("**Summary of Changes:**")
            st.markdown("""
            - ✏️ Modified: "annually" → "annually or as specified"
            - ➕ Added: "NABL" certification requirement
            - ➕ Added: "with uncertainties" to measurement recording
            - ➕ Added: New requirement for quarterly intermediate checks
            """)

    else:
        st.info("Enter a document number to view change history")


def show_traceability_matrix():
    """Show traceability matrix"""
    st.subheader("Traceability Matrix")

    # Matrix type selection
    matrix_type = st.selectbox(
        "Matrix Type",
        [
            "Requirements → Documents",
            "Documents → Test Records",
            "Equipment → Calibration Records",
            "Standards → Procedures"
        ]
    )

    st.markdown(f"### {matrix_type}")

    # Generate matrix based on selection
    if "Requirements" in matrix_type:
        matrix_data = pd.DataFrame({
            'Requirement': [
                'ISO 17025 §5.6.1',
                'ISO 17025 §5.6.2',
                'ISO 17025 §6.4.1',
                'ISO 17025 §6.4.5',
                'ISO 9001 §7.1.5'
            ],
            'Description': [
                'Equipment shall be calibrated',
                'Calibration records maintained',
                'Measurement traceability',
                'Equipment verification',
                'Monitoring resources'
            ],
            'Document': [
                'CAL-PROC-001',
                'CAL-LOG-TEMP',
                'CAL-PROC-001',
                'EQ-VERIF-001',
                'EQ-MAINT-001'
            ],
            'Status': [
                '✅ Compliant',
                '✅ Compliant',
                '✅ Compliant',
                '⚠️ Partial',
                '✅ Compliant'
            ],
            'Last Verified': [
                '2024-03-01',
                '2024-03-01',
                '2024-02-15',
                '2024-01-20',
                '2024-03-05'
            ]
        })

    elif "Equipment" in matrix_type:
        matrix_data = pd.DataFrame({
            'Equipment': [
                'DMM-001',
                'DMM-002',
                'OSC-001',
                'PWR-001',
                'ENV-001'
            ],
            'Description': [
                'Digital Multimeter',
                'Digital Multimeter',
                'Oscilloscope',
                'Power Supply',
                'Environmental Chamber'
            ],
            'Last Calibration': [
                'CAL-2024-0123',
                'CAL-2024-0089',
                'CAL-2024-0105',
                'CAL-2024-0098',
                'CAL-2024-0112'
            ],
            'Cal Date': [
                '2024-03-01',
                '2024-02-15',
                '2024-02-20',
                '2024-02-18',
                '2024-02-25'
            ],
            'Next Due': [
                '2025-03-01',
                '2025-02-15',
                '2025-02-20',
                '2025-02-18',
                '2025-02-25'
            ],
            'Status': [
                '✅ Valid',
                '✅ Valid',
                '✅ Valid',
                '✅ Valid',
                '✅ Valid'
            ]
        })

    else:
        matrix_data = pd.DataFrame({
            'Standard': [
                'IEC 61215',
                'IEC 61730',
                'IEC 62804',
                'IEC 61701'
            ],
            'Procedure': [
                'PV-TEST-001',
                'PV-SAFETY-001',
                'PV-PID-001',
                'PV-CORR-001'
            ],
            'Test Records': [
                '45 records',
                '32 records',
                '12 records',
                '8 records'
            ],
            'Last Updated': [
                '2024-03-10',
                '2024-03-08',
                '2024-03-05',
                '2024-02-28'
            ]
        })

    st.dataframe(matrix_data, use_container_width=True)

    # Export matrix
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("📥 Export Matrix"):
            csv = matrix_data.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"traceability_matrix_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

    # Statistics
    st.markdown("### Coverage Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Items", len(matrix_data))
    with col2:
        compliant = len([x for x in matrix_data.iloc[:, -2] if '✅' in str(x)])
        st.metric("Compliant", compliant, f"{compliant/len(matrix_data)*100:.0f}%")
    with col3:
        st.metric("Coverage", "95%", "5%")
