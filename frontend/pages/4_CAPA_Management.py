"""CAPA (Corrective and Preventive Action) Management Page."""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.api_client import APIClient

st.set_page_config(page_title="CAPA Management", page_icon="✅", layout="wide")

st.title("✅ CAPA Management")
st.markdown("Corrective and Preventive Action Tracking & Effectiveness Verification")
st.markdown("---")

# Initialize API client
api = APIClient()

# Tab selection
tab1, tab2, tab3 = st.tabs(["➕ Create CAPA", "📋 CAPA List", "📊 CAPA Dashboard"])

# =================== TAB 1: CREATE CAPA ===================
with tab1:
    st.subheader("Create New CAPA Action")

    # NC Selection
    try:
        ncs = api.get_ncs(limit=100)

        if not ncs:
            st.warning("⚠️ No non-conformances found. Please register a NC first.")
        else:
            # Check if NC is pre-selected
            default_nc_id = st.session_state.get('selected_nc_id')
            default_index = 0

            if default_nc_id:
                try:
                    default_index = next(i for i, nc in enumerate(ncs) if nc['id'] == default_nc_id)
                except StopIteration:
                    pass

            selected_nc_number = st.selectbox(
                "Select Related NC:",
                options=[nc["nc_number"] for nc in ncs],
                index=default_index,
                format_func=lambda x: f"{x} - {next(nc['title'] for nc in ncs if nc['nc_number'] == x)}"
            )

            selected_nc = next(nc for nc in ncs if nc["nc_number"] == selected_nc_number)

            # Display NC info
            with st.expander("📋 NC Information", expanded=False):
                st.write(f"**NC:** {selected_nc['nc_number']} - {selected_nc['title']}")
                st.write(f"**Description:** {selected_nc['description']}")

            # CAPA Form
            with st.form("capa_creation_form"):
                st.markdown("#### CAPA Details")

                col1, col2 = st.columns(2)

                with col1:
                    capa_type = st.selectbox(
                        "CAPA Type *",
                        options=["corrective", "preventive"],
                        format_func=lambda x: "Corrective Action (Fix the problem)" if x == "corrective" else "Preventive Action (Prevent recurrence)",
                        help="Corrective: Eliminate the cause of detected non-conformance\nPreventive: Eliminate the cause of potential non-conformance"
                    )

                with col2:
                    due_date = st.date_input(
                        "Due Date *",
                        value=date.today() + timedelta(days=30),
                        min_value=date.today(),
                        help="Target completion date for this CAPA"
                    )

                title = st.text_input(
                    "CAPA Title *",
                    placeholder="Brief description of the action to be taken",
                    help="Short title describing the CAPA action"
                )

                description = st.text_area(
                    "Detailed Description *",
                    placeholder="Detailed description of the corrective/preventive action...",
                    height=120,
                    help="Comprehensive description of what needs to be done"
                )

                st.markdown("---")
                st.markdown("#### Assignment")

                col1, col2 = st.columns(2)

                with col1:
                    assigned_to = st.text_input(
                        "Assigned To *",
                        help="Person responsible for completing this CAPA"
                    )

                with col2:
                    assigned_by = st.text_input(
                        "Assigned By *",
                        help="Your name (person creating this CAPA)"
                    )

                st.markdown("---")
                st.markdown("#### Implementation Plan")

                implementation_plan = st.text_area(
                    "Implementation Plan",
                    placeholder="Describe the steps needed to implement this CAPA...",
                    height=100,
                    help="Detailed plan for implementing the action"
                )

                col1, col2 = st.columns(2)

                with col1:
                    estimated_cost = st.number_input(
                        "Estimated Cost (USD)",
                        min_value=0.0,
                        value=0.0,
                        format="%.2f",
                        help="Estimated cost for implementation"
                    )

                with col2:
                    st.markdown("**Resources Required**")

                resources_text = st.text_area(
                    "Resources (one per line)",
                    placeholder="List required resources:\n- Personnel\n- Equipment\n- Materials\n- Time",
                    height=100,
                    help="List all resources needed",
                    label_visibility="collapsed"
                )

                st.markdown("---")
                st.markdown("#### Verification Plan")

                verification_method = st.text_area(
                    "Verification Method",
                    placeholder="How will effectiveness be verified? (e.g., Follow-up audit, testing, monitoring)",
                    height=80,
                    help="Method to verify that the CAPA was effective"
                )

                verification_criteria = st.text_area(
                    "Verification Criteria",
                    placeholder="What criteria will determine if CAPA is effective? (e.g., No recurrence for 90 days, test results within spec)",
                    height=80,
                    help="Criteria for determining effectiveness"
                )

                created_by = st.text_input("Created By *", value=assigned_by, help="Your name")

                st.markdown("---")

                submit_capa = st.form_submit_button("🚀 Create CAPA Action", use_container_width=True, type="primary")

            if submit_capa:
                if not all([title, description, assigned_to, assigned_by, created_by]):
                    st.error("⚠️ Please fill in all required fields (marked with *)!")
                else:
                    # Prepare data
                    capa_data = {
                        "nc_id": selected_nc['id'],
                        "capa_type": capa_type,
                        "title": title,
                        "description": description,
                        "assigned_to": assigned_to,
                        "assigned_by": assigned_by,
                        "due_date": due_date.isoformat(),
                        "created_by": created_by
                    }

                    if implementation_plan:
                        capa_data["implementation_plan"] = implementation_plan
                    if estimated_cost > 0:
                        capa_data["estimated_cost"] = estimated_cost
                    if resources_text:
                        capa_data["resources_required"] = [r.strip() for r in resources_text.split('\n') if r.strip()]
                    if verification_method:
                        capa_data["verification_method"] = verification_method
                    if verification_criteria:
                        capa_data["verification_criteria"] = verification_criteria

                    try:
                        with st.spinner("Creating CAPA..."):
                            result = api.create_capa(capa_data)

                        st.success(f"✅ CAPA Action created successfully!")
                        st.info(f"**CAPA Number:** {result['capa_number']}")

                        # Update NC status
                        api.update_nc(selected_nc['id'], {
                            "status": "capa_assigned",
                            "updated_by": created_by
                        })

                        st.balloons()

                        with st.expander("📋 View CAPA Details"):
                            st.json(result)

                    except Exception as e:
                        st.error(f"❌ Error creating CAPA: {str(e)}")

    except Exception as e:
        st.error(f"Error loading NCs: {str(e)}")

# =================== TAB 2: CAPA LIST ===================
with tab2:
    st.subheader("CAPA Action List")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            options=["All", "pending", "in_progress", "completed", "verified", "closed"],
            format_func=lambda x: x.replace("_", " ").title() if x != "All" else "All",
            key="capa_status_filter"
        )

    with col2:
        type_filter = st.selectbox(
            "Type",
            options=["All", "corrective", "preventive"],
            format_func=lambda x: x.title() if x != "All" else "All",
            key="capa_type_filter"
        )

    with col3:
        if st.button("🔄 Refresh", key="refresh_capa_list"):
            st.rerun()

    # Fetch CAPAs
    try:
        capas = api.get_capas(
            limit=100,
            status=None if status_filter == "All" else status_filter,
            capa_type=None if type_filter == "All" else type_filter
        )

        if not capas:
            st.info("📭 No CAPA actions found matching the filters.")
        else:
            st.success(f"✅ Found {len(capas)} CAPA action(s)")

            # Convert to DataFrame
            df_data = []
            for capa in capas:
                is_overdue = (
                    capa['status'] in ['pending', 'in_progress'] and
                    datetime.strptime(capa['due_date'], '%Y-%m-%d').date() < date.today()
                )

                df_data.append({
                    "CAPA Number": capa["capa_number"],
                    "Title": capa["title"],
                    "Type": capa["capa_type"].title(),
                    "Status": capa["status"].replace("_", " ").title(),
                    "Assigned To": capa["assigned_to"],
                    "Due Date": capa["due_date"],
                    "Overdue": "⚠️ Yes" if is_overdue else "No",
                    "ID": capa["id"]
                })

            df = pd.DataFrame(df_data)

            # Highlight overdue
            st.dataframe(
                df.drop(columns=["ID"]),
                use_container_width=True,
                hide_index=True
            )

            # CAPA Details
            st.markdown("---")
            selected_capa_number = st.selectbox(
                "Select CAPA to view/update:",
                options=[capa["capa_number"] for capa in capas],
                format_func=lambda x: f"{x} - {next(capa['title'] for capa in capas if capa['capa_number'] == x)}"
            )

            if selected_capa_number:
                selected_capa = next(capa for capa in capas if capa["capa_number"] == selected_capa_number)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### CAPA Information")
                    st.write(f"**CAPA Number:** {selected_capa['capa_number']}")
                    st.write(f"**Type:** {selected_capa['capa_type'].title()}")
                    st.write(f"**Status:** {selected_capa['status'].replace('_', ' ').title()}")
                    st.write(f"**Title:** {selected_capa['title']}")

                    st.markdown("**Description:**")
                    st.text_area("", value=selected_capa['description'], height=100, disabled=True, key="capa_desc_view")

                with col2:
                    st.markdown("#### Assignment & Timeline")
                    st.write(f"**Assigned To:** {selected_capa['assigned_to']}")
                    st.write(f"**Assigned By:** {selected_capa['assigned_by']}")
                    st.write(f"**Due Date:** {selected_capa['due_date']}")

                    if selected_capa.get('completed_date'):
                        st.write(f"**Completed:** {selected_capa['completed_date']}")

                    # Check if overdue
                    if selected_capa['status'] in ['pending', 'in_progress']:
                        due = datetime.strptime(selected_capa['due_date'], '%Y-%m-%d').date()
                        days_remaining = (due - date.today()).days
                        if days_remaining < 0:
                            st.error(f"⚠️ Overdue by {abs(days_remaining)} days!")
                        elif days_remaining <= 7:
                            st.warning(f"⏰ Due in {days_remaining} days")
                        else:
                            st.info(f"📅 {days_remaining} days remaining")

                # Update CAPA Status
                st.markdown("---")
                st.markdown("#### Update CAPA")

                with st.form(f"update_capa_{selected_capa['id']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_status = st.selectbox(
                            "Update Status",
                            options=["pending", "in_progress", "completed", "verified", "closed"],
                            index=["pending", "in_progress", "completed", "verified", "closed"].index(selected_capa['status']),
                            format_func=lambda x: x.replace("_", " ").title()
                        )

                    with col2:
                        if new_status == "completed":
                            completed_date = st.date_input("Completion Date", value=date.today())

                    action_taken = st.text_area(
                        "Action Taken",
                        placeholder="Describe what actions were taken...",
                        value=selected_capa.get('action_taken', '') or ''
                    )

                    if new_status in ["verified", "closed"]:
                        st.markdown("#### Effectiveness Verification")

                        verification_result = st.radio(
                            "Verification Result",
                            options=[True, False],
                            format_func=lambda x: "✅ Effective" if x else "❌ Not Effective"
                        )

                        effectiveness_rating = st.slider(
                            "Effectiveness Rating",
                            min_value=1,
                            max_value=5,
                            value=3,
                            help="1 = Not effective, 5 = Highly effective"
                        )

                        verification_comments = st.text_area(
                            "Verification Comments",
                            placeholder="Comments on effectiveness verification..."
                        )

                        verified_by = st.text_input("Verified By")

                    updated_by = st.text_input("Updated By *")

                    if st.form_submit_button("💾 Update CAPA", use_container_width=True):
                        if not updated_by:
                            st.error("Please enter your name")
                        else:
                            update_data = {
                                "status": new_status,
                                "updated_by": updated_by
                            }

                            if action_taken:
                                update_data["action_taken"] = action_taken

                            if new_status == "completed":
                                update_data["completed_date"] = completed_date.isoformat()

                            if new_status in ["verified", "closed"]:
                                update_data["verification_result"] = verification_result
                                update_data["effectiveness_rating"] = effectiveness_rating
                                update_data["verification_comments"] = verification_comments
                                update_data["verified_by"] = verified_by
                                update_data["verification_date"] = date.today().isoformat()

                            try:
                                api.update_capa(selected_capa['id'], update_data)
                                st.success("✅ CAPA updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error loading CAPAs: {str(e)}")

# =================== TAB 3: DASHBOARD ===================
with tab3:
    st.subheader("CAPA Dashboard & Statistics")

    try:
        stats = api.get_capa_statistics()

        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total CAPAs", stats["total"])

        with col2:
            st.metric("Pending", stats["pending"], delta=None)

        with col3:
            st.metric("In Progress", stats["in_progress"])

        with col4:
            st.metric("Completed", stats["completed"])

        with col5:
            st.metric("Overdue", stats["overdue"], delta=-stats["overdue"] if stats["overdue"] > 0 else 0)

        st.markdown("---")

        # By Type
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### By Type")
            if stats.get("by_type"):
                for capa_type, count in stats["by_type"].items():
                    st.write(f"**{capa_type.title()}:** {count}")

        with col2:
            st.markdown("#### Overdue Actions")
            overdue = api.get_overdue_capas()
            if overdue:
                for capa in overdue[:5]:
                    st.warning(f"⚠️ {capa['capa_number']} - {capa['title']} (Due: {capa['due_date']})")
            else:
                st.success("✅ No overdue CAPA actions!")

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("### 💡 CAPA Types")

    with st.expander("Corrective Action"):
        st.write("""
        **Purpose:** Eliminate the cause of detected non-conformance

        **When to use:**
        - Problem has already occurred
        - Need to prevent recurrence
        - Address root cause

        **Example:** Update work instruction after procedure was not followed
        """)

    with st.expander("Preventive Action"):
        st.write("""
        **Purpose:** Eliminate the cause of potential non-conformance

        **When to use:**
        - Prevent future problems
        - Identified potential risk
        - Proactive improvement

        **Example:** Improve training program to prevent future errors
        """)
