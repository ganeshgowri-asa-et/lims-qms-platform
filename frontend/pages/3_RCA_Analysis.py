"""Root Cause Analysis Page with 5-Why and Fishbone methodologies."""

import streamlit as st
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.api_client import APIClient

st.set_page_config(page_title="Root Cause Analysis", page_icon="🎯", layout="wide")

st.title("🎯 Root Cause Analysis")
st.markdown("---")

# Initialize API client
api = APIClient()

# NC Selection
st.subheader("1️⃣ Select Non-Conformance")

try:
    ncs = api.get_ncs(limit=100)

    if not ncs:
        st.warning("⚠️ No non-conformances found. Please register a NC first.")
        if st.button("📝 Register NC"):
            st.switch_page("pages/1_NC_Registration.py")
        st.stop()

    # Check if NC is pre-selected from session state
    default_nc_id = st.session_state.get('selected_nc_id')
    default_index = 0

    if default_nc_id:
        try:
            default_index = next(i for i, nc in enumerate(ncs) if nc['id'] == default_nc_id)
        except StopIteration:
            pass

    selected_nc_number = st.selectbox(
        "Select NC for Root Cause Analysis:",
        options=[nc["nc_number"] for nc in ncs],
        index=default_index,
        format_func=lambda x: f"{x} - {next(nc['title'] for nc in ncs if nc['nc_number'] == x)}"
    )

    selected_nc = next(nc for nc in ncs if nc["nc_number"] == selected_nc_number)

    # Display NC summary
    with st.expander("📋 NC Summary", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**NC Number:** {selected_nc['nc_number']}")
            st.write(f"**Title:** {selected_nc['title']}")
        with col2:
            st.write(f"**Severity:** {selected_nc['severity'].upper()}")
            st.write(f"**Status:** {selected_nc['status'].replace('_', ' ').title()}")
        with col3:
            st.write(f"**Source:** {selected_nc['source'].replace('_', ' ').title()}")

        st.markdown("**Description:**")
        st.info(selected_nc['description'])

    st.markdown("---")

    # Check existing RCAs
    existing_rcas = api.get_rcas_by_nc(selected_nc['id'])

    if existing_rcas:
        st.subheader("📚 Existing Root Cause Analyses")
        for rca in existing_rcas:
            with st.expander(f"RCA #{rca['id']} - {rca['method'].upper()} - {rca['analysis_date'][:10]}"):
                st.write(f"**Analyzed By:** {rca['analyzed_by']}")
                st.write(f"**Method:** {rca['method'].upper()}")
                st.write(f"**Root Cause:** {rca['root_cause']}")

                if rca.get('approved_by'):
                    st.success(f"✅ Approved by {rca['approved_by']} on {rca['approval_date'][:10]}")
                else:
                    st.warning("⏳ Pending Approval")
        st.markdown("---")

    # RCA Method Selection
    st.subheader("2️⃣ Select RCA Method")

    rca_method = st.radio(
        "Choose Root Cause Analysis Method:",
        options=["5-why", "fishbone"],
        format_func=lambda x: "5-Why Analysis" if x == "5-why" else "Fishbone (Ishikawa) Diagram",
        horizontal=True
    )

    st.markdown("---")

    # AI Suggestions Section
    st.subheader("🤖 AI-Powered Root Cause Suggestions")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.info("Get AI-powered suggestions to help identify potential root causes based on the NC description.")

    with col2:
        if st.button("🚀 Get AI Suggestions", use_container_width=True, type="primary"):
            with st.spinner("Analyzing and generating suggestions..."):
                try:
                    ai_result = api.get_ai_suggestions(
                        nc_description=selected_nc['title'],
                        problem_details=selected_nc['description'],
                        context=selected_nc.get('impact_description', '')
                    )

                    st.session_state['ai_suggestions'] = ai_result
                except Exception as e:
                    st.error(f"Error getting AI suggestions: {str(e)}")

    # Display AI suggestions if available
    if 'ai_suggestions' in st.session_state:
        ai_result = st.session_state['ai_suggestions']

        st.markdown("#### 💡 Suggested Root Causes")
        st.caption(f"Model: {ai_result['model_used']} | Confidence: {ai_result['confidence_score']:.0%}")

        for i, suggestion in enumerate(ai_result['suggestions'], 1):
            with st.expander(f"Suggestion {i}: {suggestion['cause']}", expanded=i <= 3):
                st.write(f"**Category:** {suggestion['category']}")
                st.write(f"**Reasoning:** {suggestion['reasoning']}")
                st.write(f"**Likelihood:** {suggestion['likelihood'].upper()}")

    st.markdown("---")

    # =================== 5-WHY ANALYSIS ===================
    if rca_method == "5-why":
        st.subheader("3️⃣ 5-Why Analysis")

        st.info("""
        **5-Why Methodology:** Ask "Why?" five times to drill down to the root cause.
        - Start with the problem statement
        - For each answer, ask "Why did this happen?"
        - Continue until you reach the root cause (usually 5 levels)
        """)

        # Initialize 5-Why data
        if '5why_data' not in st.session_state:
            st.session_state['5why_data'] = api.get_5why_template()

        # 5-Why form
        with st.form("five_why_form"):
            five_why_steps = []

            for i in range(1, 6):
                st.markdown(f"#### Why {i}?")
                col1, col2 = st.columns([1, 2])

                with col1:
                    why_question = st.text_input(
                        "Question",
                        value=f"Why did this non-conformance occur?" if i == 1 else f"Why {i}?",
                        key=f"why_q_{i}",
                        label_visibility="collapsed"
                    )

                with col2:
                    answer = st.text_area(
                        "Answer",
                        placeholder=f"Answer to Why {i}...",
                        key=f"why_a_{i}",
                        height=80,
                        label_visibility="collapsed"
                    )

                five_why_steps.append({
                    "level": i,
                    "why": why_question,
                    "answer": answer
                })

            st.markdown("---")

            st.markdown("#### Root Cause Conclusion")
            root_cause = st.text_area(
                "Based on the 5-Why analysis, what is the root cause?",
                placeholder="State the root cause identified through this analysis...",
                height=100
            )

            contributing_factors = st.text_area(
                "Contributing Factors (one per line)",
                placeholder="List any contributing factors...",
                height=80
            )

            analyzed_by = st.text_input("Analyzed By *", help="Your name")

            submit_5why = st.form_submit_button("💾 Save 5-Why Analysis", use_container_width=True, type="primary")

        if submit_5why:
            if not root_cause or not analyzed_by:
                st.error("⚠️ Please provide root cause and analyzer name!")
            else:
                # Prepare data
                rca_data = {
                    "nc_id": selected_nc['id'],
                    "method": "5-why",
                    "analyzed_by": analyzed_by,
                    "five_why_data": five_why_steps,
                    "root_cause": root_cause,
                    "contributing_factors": [f.strip() for f in contributing_factors.split('\n') if f.strip()]
                }

                # Add AI suggestions if available
                if 'ai_suggestions' in st.session_state:
                    rca_data["ai_suggestions"] = st.session_state['ai_suggestions']['suggestions']
                    rca_data["ai_model_used"] = st.session_state['ai_suggestions']['model_used']
                    rca_data["ai_confidence_score"] = st.session_state['ai_suggestions']['confidence_score']

                try:
                    with st.spinner("Saving RCA..."):
                        result = api.create_rca(rca_data)

                    st.success("✅ 5-Why Analysis saved successfully!")

                    # Update NC status
                    api.update_nc(selected_nc['id'], {
                        "status": "rca_in_progress",
                        "updated_by": analyzed_by
                    })

                    st.balloons()

                    if st.button("➡️ Create CAPA Action"):
                        st.session_state['selected_nc_id'] = selected_nc['id']
                        st.switch_page("pages/4_CAPA_Management.py")

                except Exception as e:
                    st.error(f"❌ Error saving RCA: {str(e)}")

    # =================== FISHBONE ANALYSIS ===================
    elif rca_method == "fishbone":
        st.subheader("3️⃣ Fishbone (Ishikawa) Diagram")

        st.info("""
        **Fishbone Methodology:** Identify potential causes across 6M categories:
        - **Man** (People): Human factors, training, competency
        - **Machine** (Equipment): Equipment, tools, technology
        - **Method** (Process): Procedures, work instructions
        - **Material**: Raw materials, components
        - **Measurement**: Testing, inspection, accuracy
        - **Environment**: Workplace conditions, surroundings
        """)

        with st.form("fishbone_form"):
            fishbone_data = {}

            categories = [
                ("man", "👤 Man (People)", "Training, competency, human error, etc."),
                ("machine", "⚙️ Machine (Equipment)", "Equipment, calibration, maintenance, etc."),
                ("method", "📋 Method (Process)", "Procedures, work instructions, process control, etc."),
                ("material", "📦 Material", "Raw materials, components, specifications, etc."),
                ("measurement", "📏 Measurement", "Testing methods, instruments, accuracy, etc."),
                ("environment", "🌍 Environment", "Temperature, humidity, cleanliness, etc.")
            ]

            for key, label, placeholder in categories:
                st.markdown(f"#### {label}")
                causes_text = st.text_area(
                    f"{label} causes",
                    placeholder=f"{placeholder}\n(Enter one cause per line)",
                    height=100,
                    key=f"fishbone_{key}",
                    label_visibility="collapsed"
                )
                fishbone_data[key] = [c.strip() for c in causes_text.split('\n') if c.strip()]

            st.markdown("---")

            st.markdown("#### Root Cause Conclusion")
            root_cause_fishbone = st.text_area(
                "Based on the Fishbone analysis, what is the root cause?",
                placeholder="State the root cause identified through this analysis...",
                height=100
            )

            contributing_factors_fishbone = st.text_area(
                "Contributing Factors (one per line)",
                placeholder="List any contributing factors...",
                height=80
            )

            analyzed_by_fishbone = st.text_input("Analyzed By *", help="Your name", key="fishbone_analyzed_by")

            submit_fishbone = st.form_submit_button("💾 Save Fishbone Analysis", use_container_width=True, type="primary")

        if submit_fishbone:
            if not root_cause_fishbone or not analyzed_by_fishbone:
                st.error("⚠️ Please provide root cause and analyzer name!")
            else:
                # Prepare data
                rca_data = {
                    "nc_id": selected_nc['id'],
                    "method": "fishbone",
                    "analyzed_by": analyzed_by_fishbone,
                    "fishbone_data": fishbone_data,
                    "root_cause": root_cause_fishbone,
                    "contributing_factors": [f.strip() for f in contributing_factors_fishbone.split('\n') if f.strip()]
                }

                # Add AI suggestions if available
                if 'ai_suggestions' in st.session_state:
                    rca_data["ai_suggestions"] = st.session_state['ai_suggestions']['suggestions']
                    rca_data["ai_model_used"] = st.session_state['ai_suggestions']['model_used']
                    rca_data["ai_confidence_score"] = st.session_state['ai_suggestions']['confidence_score']

                try:
                    with st.spinner("Saving RCA..."):
                        result = api.create_rca(rca_data)

                    st.success("✅ Fishbone Analysis saved successfully!")

                    # Update NC status
                    api.update_nc(selected_nc['id'], {
                        "status": "rca_in_progress",
                        "updated_by": analyzed_by_fishbone
                    })

                    st.balloons()

                    if st.button("➡️ Create CAPA Action"):
                        st.session_state['selected_nc_id'] = selected_nc['id']
                        st.switch_page("pages/4_CAPA_Management.py")

                except Exception as e:
                    st.error(f"❌ Error saving RCA: {str(e)}")

except Exception as e:
    st.error(f"❌ Error loading page: {str(e)}")
    st.exception(e)

# Sidebar - Help
with st.sidebar:
    st.markdown("### 📖 RCA Methods")

    with st.expander("5-Why Analysis"):
        st.write("""
        **When to use:**
        - Simple to moderate complexity problems
        - Linear cause-effect relationships
        - Quick analysis needed

        **How it works:**
        1. State the problem
        2. Ask "Why?" it happened
        3. For each answer, ask "Why?" again
        4. Repeat 5 times or until root cause
        """)

    with st.expander("Fishbone Diagram"):
        st.write("""
        **When to use:**
        - Complex problems with multiple factors
        - Need structured approach
        - Team brainstorming

        **6M Categories:**
        - Man: People, skills, training
        - Machine: Equipment, tools
        - Method: Processes, procedures
        - Material: Inputs, components
        - Measurement: Testing, inspection
        - Environment: Conditions, surroundings
        """)
