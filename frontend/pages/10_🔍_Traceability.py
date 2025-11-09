"""
Traceability & Audit Trail Dashboard
"""
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(
    page_title="Traceability & Audit Trail",
    page_icon="🔍",
    layout="wide"
)

# API base URL
API_URL = "http://localhost:8000/api/v1"

# Authentication
if "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}


def create_tree_visualization(tree_data, direction="downstream"):
    """Create an interactive tree visualization using Plotly"""
    if not tree_data:
        return None

    nodes = []
    edges = []
    node_ids = []

    def traverse_tree(node, parent_id=None, level=0):
        """Recursively traverse tree and collect nodes and edges"""
        node_id = f"{node.get('entity_type')}_{node.get('entity_id')}_{len(node_ids)}"
        node_ids.append(node_id)

        # Add node
        entity_details = node.get('entity_details', {})
        node_label = f"{node.get('entity_type')}\n#{node.get('entity_id')}"
        if entity_details and entity_details.get('name'):
            node_label += f"\n{entity_details['name'][:30]}"

        nodes.append({
            'id': node_id,
            'label': node_label,
            'level': level,
            'entity_type': node.get('entity_type'),
            'entity_id': node.get('entity_id')
        })

        # Add edge from parent
        if parent_id:
            edges.append({
                'source': parent_id if direction == "downstream" else node_id,
                'target': node_id if direction == "downstream" else parent_id,
                'link_type': node.get('link_type', 'related')
            })

        # Traverse children
        children_key = direction
        for child in node.get(children_key, []):
            traverse_tree(child, node_id, level + 1)

    traverse_tree(tree_data)

    if not nodes:
        return None

    # Create network graph using Plotly
    edge_trace = []
    for edge in edges:
        source_node = next(n for n in nodes if n['id'] == edge['source'])
        target_node = next(n for n in nodes if n['id'] == edge['target'])

        edge_trace.append(
            go.Scatter(
                x=[source_node['level'], target_node['level']],
                y=[node_ids.index(edge['source']), node_ids.index(edge['target'])],
                mode='lines',
                line=dict(width=2, color='#888'),
                hoverinfo='text',
                text=f"Link: {edge['link_type']}",
                showlegend=False
            )
        )

    # Node trace
    node_x = [n['level'] for n in nodes]
    node_y = [node_ids.index(n['id']) for n in nodes]
    node_text = [n['label'] for n in nodes]
    node_colors = [hash(n['entity_type']) % 10 for n in nodes]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            size=20,
            color=node_colors,
            colorscale='Viridis',
            showscale=True,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )

    fig = go.Figure(data=edge_trace + [node_trace])
    fig.update_layout(
        title=f"{direction.capitalize()} Traceability Tree",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(title='Depth Level', showgrid=False),
        yaxis=dict(title='', showgrid=False, showticklabels=False),
        height=600
    )

    return fig


# Main UI
st.title("🔍 Traceability & Audit Trail Engine")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Document Lineage",
    "📜 Audit Trail",
    "🔬 Data Lineage",
    "✅ Requirements Matrix",
    "🔗 Chain of Custody",
    "📝 Compliance Reports"
])

# Tab 1: Document Lineage & Traceability
with tab1:
    st.header("Document Lineage & Traceability")

    col1, col2, col3 = st.columns(3)

    with col1:
        entity_type = st.selectbox(
            "Entity Type",
            ["document", "form_record", "project", "task", "equipment", "non_conformance", "capa"],
            key="lineage_entity_type"
        )

    with col2:
        entity_id = st.number_input("Entity ID", min_value=1, value=1, key="lineage_entity_id")

    with col3:
        max_depth = st.slider("Max Depth", 1, 10, 5)

    col_forward, col_backward = st.columns(2)

    with col_forward:
        if st.button("Get Forward Traceability", use_container_width=True):
            try:
                response = requests.get(
                    f"{API_URL}/traceability/forward/{entity_type}/{entity_id}?max_depth={max_depth}",
                    headers=headers
                )
                if response.status_code == 200:
                    tree_data = response.json()
                    st.success(f"Found {tree_data.get('total_dependencies', 0)} downstream dependencies")

                    # Visualize tree
                    fig = create_tree_visualization(tree_data, "downstream")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    # Show raw data
                    with st.expander("View Raw Data"):
                        st.json(tree_data)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col_backward:
        if st.button("Get Backward Traceability", use_container_width=True):
            try:
                response = requests.get(
                    f"{API_URL}/traceability/backward/{entity_type}/{entity_id}?max_depth={max_depth}",
                    headers=headers
                )
                if response.status_code == 200:
                    tree_data = response.json()
                    st.success(f"Found {tree_data.get('total_dependencies', 0)} upstream dependencies")

                    # Visualize tree
                    fig = create_tree_visualization(tree_data, "upstream")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    # Show raw data
                    with st.expander("View Raw Data"):
                        st.json(tree_data)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Impact Analysis
    st.subheader("Impact Analysis")
    change_desc = st.text_area("Describe the proposed change", key="impact_change_desc")

    if st.button("Analyze Impact"):
        try:
            response = requests.post(
                f"{API_URL}/traceability/impact-analysis",
                headers=headers,
                json={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "change_description": change_desc
                }
            )
            if response.status_code == 200:
                impact = response.json()
                col_scope, col_affected = st.columns(2)

                with col_scope:
                    st.metric("Impact Scope", impact['impact_scope'].upper())

                with col_affected:
                    st.metric("Total Affected Entities", impact['total_affected'])

                if impact['affected_entities']:
                    st.dataframe(pd.DataFrame(impact['affected_entities']))
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Tab 2: Audit Trail
with tab2:
    st.header("Audit Trail")

    # Search filters
    col1, col2, col3 = st.columns(3)

    with col1:
        search_entity_type = st.selectbox(
            "Entity Type",
            ["", "document", "form_record", "project", "task", "equipment"],
            key="audit_entity_type"
        )

    with col2:
        search_entity_id = st.number_input(
            "Entity ID (optional)",
            min_value=0,
            value=0,
            key="audit_entity_id"
        )

    with col3:
        search_action = st.selectbox(
            "Action",
            ["", "create", "update", "delete", "approve", "submit"],
            key="audit_action"
        )

    # Date range
    col_start, col_end = st.columns(2)
    with col_start:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col_end:
        end_date = st.date_input("End Date", datetime.now())

    if st.button("Search Audit Logs"):
        try:
            search_data = {
                "limit": 100,
                "offset": 0
            }

            if search_entity_type:
                search_data["entity_type"] = search_entity_type
            if search_entity_id > 0:
                search_data["entity_id"] = search_entity_id
            if search_action:
                search_data["action"] = search_action
            if start_date:
                search_data["start_date"] = start_date.isoformat()
            if end_date:
                search_data["end_date"] = end_date.isoformat()

            response = requests.post(
                f"{API_URL}/traceability/audit-logs/search",
                headers=headers,
                json=search_data
            )

            if response.status_code == 200:
                results = response.json()
                st.success(f"Found {results['total']} audit records")

                if results['results']:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(results['results'])
                    st.dataframe(df, use_container_width=True)

                    # Export option
                    if st.button("Export Audit Logs"):
                        export_response = requests.post(
                            f"{API_URL}/traceability/audit-logs/export",
                            headers=headers,
                            params={
                                "entity_type": search_entity_type if search_entity_type else None,
                                "start_date": start_date.isoformat() if start_date else None,
                                "end_date": end_date.isoformat() if end_date else None,
                                "format": "json"
                            }
                        )
                        if export_response.status_code == 200:
                            export_data = export_response.json()
                            st.download_button(
                                "Download Audit Log",
                                data=json.dumps(export_data, indent=2),
                                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.json",
                                mime="application/json"
                            )
                else:
                    st.info("No audit records found")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Verify Audit Chain Integrity
    st.subheader("Verify Audit Chain Integrity")
    if st.button("Verify Integrity"):
        try:
            response = requests.get(
                f"{API_URL}/traceability/audit-logs/verify-integrity",
                headers=headers
            )
            if response.status_code == 200:
                integrity = response.json()

                if integrity['integrity_intact']:
                    st.success(f"✅ Audit chain integrity verified! Checked {integrity['total_events_checked']} events.")
                else:
                    st.error(f"❌ Integrity issues found: {integrity['issues_found']}")
                    st.json(integrity['issues'])
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Tab 3: Data Lineage
with tab3:
    st.header("Data Lineage (Medallion Architecture)")
    st.caption("Track data transformations: Bronze → Silver → Gold")

    col1, col2 = st.columns(2)

    with col1:
        lineage_entity_type = st.selectbox(
            "Entity Type",
            ["data_point", "test_result", "form_record"],
            key="lineage_data_entity_type"
        )

    with col2:
        lineage_entity_id = st.number_input(
            "Entity ID",
            min_value=1,
            value=1,
            key="lineage_data_entity_id"
        )

    if st.button("Get Data Lineage Path"):
        try:
            response = requests.get(
                f"{API_URL}/traceability/data-lineage/{lineage_entity_type}/{lineage_entity_id}",
                headers=headers
            )
            if response.status_code == 200:
                lineage_data = response.json()

                st.success(f"Found {lineage_data['total_stages']} transformation stages")

                if lineage_data['lineage_path']:
                    # Create flow diagram
                    stages = lineage_data['lineage_path']

                    # Display as timeline
                    for i, stage in enumerate(stages):
                        col_a, col_b, col_c = st.columns([1, 2, 1])

                        with col_a:
                            st.info(f"**{stage['source']['stage'].upper()}**")
                            st.caption(f"{stage['source']['entity_type']} #{stage['source']['entity_id']}")

                        with col_b:
                            st.write(f"➡️ **{stage['transformation_type']}**")
                            if stage['transformation_logic']:
                                st.caption(stage['transformation_logic'][:100])
                            if stage['data_quality_score']:
                                st.progress(stage['data_quality_score'] / 100)

                        with col_c:
                            st.success(f"**{stage['target']['stage'].upper()}**")
                            st.caption(f"{stage['target']['entity_type']} #{stage['target']['entity_id']}")

                        if i < len(stages) - 1:
                            st.write("↓")
                else:
                    st.info("No lineage path found")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Tab 4: Requirements Traceability Matrix
with tab4:
    st.header("Requirements Traceability Matrix (RTM)")

    if st.button("Generate RTM Coverage Report"):
        try:
            response = requests.get(
                f"{API_URL}/traceability/requirements/coverage",
                headers=headers
            )
            if response.status_code == 200:
                rtm = response.json()

                # Display summary metrics
                summary = rtm['summary']
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Requirements", summary['total_requirements'])
                with col2:
                    st.metric("Verified", summary['verified'], delta=None)
                with col3:
                    st.metric("Coverage %", f"{summary['coverage_percentage']}%")
                with col4:
                    st.metric("Not Verified", summary['not_verified'])

                # Coverage chart
                fig = px.pie(
                    values=[summary['verified'], summary['partially_verified'], summary['not_verified']],
                    names=['Verified', 'Partially Verified', 'Not Verified'],
                    title='Requirements Verification Status'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Requirements by category
                st.subheader("Requirements by Category")
                for category, reqs in rtm['by_category'].items():
                    with st.expander(f"{category} ({len(reqs)} requirements)"):
                        st.dataframe(pd.DataFrame(reqs))

                # Gaps
                if rtm['gaps']:
                    st.subheader("⚠️ Requirements Without Evidence")
                    st.dataframe(pd.DataFrame(rtm['gaps']))
                else:
                    st.success("✅ All requirements have evidence!")

            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Tab 5: Chain of Custody
with tab5:
    st.header("Chain of Custody")

    col1, col2 = st.columns(2)

    with col1:
        custody_entity_type = st.selectbox(
            "Entity Type",
            ["sample", "equipment"],
            key="custody_entity_type"
        )

    with col2:
        custody_entity_id = st.number_input(
            "Entity ID",
            min_value=1,
            value=1,
            key="custody_entity_id"
        )

    if st.button("Get Chain of Custody"):
        try:
            response = requests.get(
                f"{API_URL}/traceability/chain-of-custody/{custody_entity_type}/{custody_entity_id}",
                headers=headers
            )
            if response.status_code == 200:
                custody_chain = response.json()

                st.success(f"Found {len(custody_chain)} custody events")

                if custody_chain:
                    # Timeline visualization
                    for event in custody_chain:
                        col_time, col_event, col_details = st.columns([1, 2, 2])

                        with col_time:
                            timestamp = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                            st.caption(timestamp.strftime("%Y-%m-%d %H:%M"))

                        with col_event:
                            st.write(f"**{event['event_type'].upper()}**")
                            if event['from_location'] and event['to_location']:
                                st.write(f"📍 {event['from_location']} → {event['to_location']}")

                        with col_details:
                            if event['condition_before']:
                                st.caption(f"Before: {event['condition_before']}")
                            if event['condition_after']:
                                st.caption(f"After: {event['condition_after']}")
                            if event['notes']:
                                st.caption(f"Notes: {event['notes']}")

                        st.divider()
                else:
                    st.info("No custody events found")
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Tab 6: Compliance Reports
with tab6:
    st.header("Compliance Reports (ISO 17025 / ISO 9001)")

    # Filter options
    selected_standards = st.multiselect(
        "Compliance Standards",
        ["ISO 17025", "ISO 9001", "GLP", "FDA 21 CFR Part 11"],
        default=["ISO 17025"]
    )

    col_start, col_end = st.columns(2)
    with col_start:
        comp_start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365), key="comp_start")
    with col_end:
        comp_end_date = st.date_input("End Date", datetime.now(), key="comp_end")

    if st.button("Generate Compliance Report"):
        try:
            response = requests.post(
                f"{API_URL}/traceability/compliance-reports",
                headers=headers,
                json={
                    "standards": selected_standards if selected_standards else None,
                    "start_date": comp_start_date.isoformat() if comp_start_date else None,
                    "end_date": comp_end_date.isoformat() if comp_end_date else None
                }
            )
            if response.status_code == 200:
                report = response.json()

                # Summary
                summary = report['summary']
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Evidence", summary['total_evidence'])
                with col2:
                    st.metric("Valid", summary['valid'])
                with col3:
                    st.metric("Expired", summary['expired'])
                with col4:
                    st.metric("Superseded", summary['superseded'])

                # Evidence by type
                st.subheader("Evidence by Type")
                type_counts = {k: len(v) for k, v in report['by_type'].items()}
                fig = px.bar(
                    x=list(type_counts.keys()),
                    y=list(type_counts.values()),
                    title="Evidence Count by Type"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Evidence by standard
                st.subheader("Evidence by Standard")
                for standard, evidence_numbers in report['by_standard'].items():
                    with st.expander(f"{standard} ({len(evidence_numbers)} items)"):
                        st.write(evidence_numbers)

                # Download report
                st.download_button(
                    "Download Compliance Report",
                    data=json.dumps(report, indent=2),
                    file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Footer
st.divider()
st.caption("🔍 Traceability & Audit Trail Engine - Production Ready")
