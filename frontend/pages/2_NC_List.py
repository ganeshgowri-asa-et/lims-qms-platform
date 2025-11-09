"""Non-Conformance List and Management Page."""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.api_client import APIClient

st.set_page_config(page_title="NC List", page_icon="📋", layout="wide")

st.title("📋 Non-Conformance List")
st.markdown("---")

# Initialize API client
api = APIClient()

# Filters
st.subheader("🔍 Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    status_filter = st.selectbox(
        "Status",
        options=["All", "open", "under_investigation", "rca_in_progress", "capa_assigned", "closed", "verified"],
        format_func=lambda x: x.replace("_", " ").title() if x != "All" else "All"
    )

with col2:
    severity_filter = st.selectbox(
        "Severity",
        options=["All", "critical", "major", "minor"],
        format_func=lambda x: x.upper() if x != "All" else "All"
    )

with col3:
    limit = st.number_input("Results per page", min_value=10, max_value=500, value=50, step=10)

with col4:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown("---")

# Fetch NCs
try:
    with st.spinner("Loading Non-Conformances..."):
        ncs = api.get_ncs(
            limit=limit,
            status=None if status_filter == "All" else status_filter,
            severity=None if severity_filter == "All" else severity_filter
        )

    if not ncs:
        st.info("📭 No non-conformances found matching the filters.")
    else:
        # Display count
        st.success(f"✅ Found {len(ncs)} non-conformance(s)")

        # Convert to DataFrame for better display
        df_data = []
        for nc in ncs:
            df_data.append({
                "NC Number": nc["nc_number"],
                "Title": nc["title"],
                "Severity": nc["severity"].upper(),
                "Status": nc["status"].replace("_", " ").title(),
                "Source": nc["source"].replace("_", " ").title(),
                "Detected Date": datetime.fromisoformat(nc["detected_date"].replace("Z", "")).strftime("%Y-%m-%d"),
                "Detected By": nc["detected_by"],
                "Department": nc.get("department", "N/A"),
                "ID": nc["id"]
            })

        df = pd.DataFrame(df_data)

        # Display as table with row selection
        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("📝 NC Details")

        # NC selection
        selected_nc_number = st.selectbox(
            "Select NC to view details:",
            options=[nc["nc_number"] for nc in ncs],
            format_func=lambda x: f"{x} - {next(nc['title'] for nc in ncs if nc['nc_number'] == x)}"
        )

        if selected_nc_number:
            selected_nc = next(nc for nc in ncs if nc["nc_number"] == selected_nc_number)

            # Display detailed information
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Basic Information")
                st.write(f"**NC Number:** {selected_nc['nc_number']}")
                st.write(f"**Title:** {selected_nc['title']}")
                st.write(f"**Status:** {selected_nc['status'].replace('_', ' ').title()}")
                st.write(f"**Severity:** {selected_nc['severity'].upper()}")
                st.write(f"**Source:** {selected_nc['source'].replace('_', ' ').title()}")

                st.markdown("#### Detection")
                st.write(f"**Detected By:** {selected_nc['detected_by']}")
                st.write(f"**Detected Date:** {datetime.fromisoformat(selected_nc['detected_date'].replace('Z', '')).strftime('%Y-%m-%d %H:%M')}")
                if selected_nc.get('department'):
                    st.write(f"**Department:** {selected_nc['department']}")
                if selected_nc.get('location'):
                    st.write(f"**Location:** {selected_nc['location']}")

            with col2:
                st.markdown("#### Assignment & Timeline")
                if selected_nc.get('assigned_to'):
                    st.write(f"**Assigned To:** {selected_nc['assigned_to']}")
                if selected_nc.get('target_closure_date'):
                    st.write(f"**Target Closure:** {selected_nc['target_closure_date']}")
                if selected_nc.get('actual_closure_date'):
                    st.write(f"**Actual Closure:** {selected_nc['actual_closure_date']}")

                st.markdown("#### Impact")
                if selected_nc.get('quantity_affected'):
                    st.write(f"**Quantity Affected:** {selected_nc['quantity_affected']}")
                if selected_nc.get('cost_impact'):
                    st.write(f"**Cost Impact:** ${selected_nc['cost_impact']:.2f}")

            st.markdown("#### Description")
            st.text_area("", value=selected_nc['description'], height=100, disabled=True)

            if selected_nc.get('impact_description'):
                st.markdown("#### Impact Description")
                st.text_area("", value=selected_nc['impact_description'], height=80, disabled=True, key="impact")

            if selected_nc.get('immediate_action'):
                st.markdown("#### Immediate Action")
                st.text_area("", value=selected_nc['immediate_action'], height=80, disabled=True, key="action")

            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🔍 Perform RCA", use_container_width=True):
                    st.session_state['selected_nc_id'] = selected_nc['id']
                    st.switch_page("pages/3_RCA_Analysis.py")

            with col2:
                if st.button("✅ Manage CAPA", use_container_width=True):
                    st.session_state['selected_nc_id'] = selected_nc['id']
                    st.switch_page("pages/4_CAPA_Management.py")

            with col3:
                if st.button("✏️ Edit NC", use_container_width=True):
                    st.session_state['edit_nc_id'] = selected_nc['id']
                    st.info("Edit functionality - Update NC status, assignment, etc.")

                    # Simple status update
                    with st.form("update_status_form"):
                        new_status = st.selectbox(
                            "Update Status",
                            options=["open", "under_investigation", "rca_in_progress", "capa_assigned", "closed", "verified"],
                            index=["open", "under_investigation", "rca_in_progress", "capa_assigned", "closed", "verified"].index(selected_nc['status']),
                            format_func=lambda x: x.replace("_", " ").title()
                        )

                        updated_by = st.text_input("Updated By", key="update_by")

                        if st.form_submit_button("Update Status"):
                            if updated_by:
                                try:
                                    api.update_nc(
                                        selected_nc['id'],
                                        {"status": new_status, "updated_by": updated_by}
                                    )
                                    st.success("✅ Status updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating status: {str(e)}")
                            else:
                                st.error("Please enter your name")

except Exception as e:
    st.error(f"❌ Error loading NCs: {str(e)}")
    st.exception(e)

# Sidebar - Statistics
with st.sidebar:
    st.markdown("### 📊 Statistics")

    try:
        stats = api.get_nc_statistics()

        st.metric("Total NCs", stats["total"])
        st.metric("Open NCs", stats["open"])
        st.metric("Closed NCs", stats["closed"])

        if stats.get("by_severity"):
            st.markdown("#### By Severity")
            for severity, count in stats["by_severity"].items():
                st.write(f"**{severity.upper()}:** {count}")

    except Exception as e:
        st.warning("Unable to load statistics")
