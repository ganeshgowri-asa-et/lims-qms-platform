"""
Workflow and Approvals page
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from frontend.utils.api_client import api_client


def show():
    """Show workflow and approvals page"""
    st.header("⚡ Workflow & Approvals")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔔 My Tasks",
        "✅ Pending Approvals",
        "📊 Workflow Status",
        "📜 Approval History"
    ])

    with tab1:
        show_my_tasks()

    with tab2:
        show_pending_approvals()

    with tab3:
        show_workflow_status()

    with tab4:
        show_approval_history()


def show_my_tasks():
    """Show user's pending tasks"""
    st.subheader("My Pending Tasks")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "Critical", "High", "Medium", "Low"]
        )
    with col2:
        type_filter = st.selectbox(
            "Type",
            ["All", "Review", "Approve", "Sign", "Verify", "Acknowledge"]
        )
    with col3:
        due_filter = st.selectbox(
            "Due Date",
            ["All", "Overdue", "Today", "This Week", "This Month"]
        )

    # Fetch tasks from API
    try:
        tasks = api_client.get_tasks(assigned_to_me=True)
    except:
        tasks = []

    # Mock data if API fails
    if not tasks:
        tasks = [
            {
                "id": 1,
                "task_number": "TASK-2024-0123",
                "title": "Review Calibration Procedure",
                "type": "Review",
                "priority": "High",
                "due_date": "2024-03-15",
                "status": "Pending",
                "assigned_by": "John Manager"
            },
            {
                "id": 2,
                "task_number": "TASK-2024-0124",
                "title": "Approve Test Report DOC-2024-0045",
                "type": "Approve",
                "priority": "Critical",
                "due_date": "2024-03-12",
                "status": "Pending",
                "assigned_by": "Sarah Lead"
            },
            {
                "id": 3,
                "task_number": "TASK-2024-0125",
                "title": "Sign Equipment Qualification Protocol",
                "type": "Sign",
                "priority": "Medium",
                "due_date": "2024-03-20",
                "status": "Pending",
                "assigned_by": "Mike QA"
            }
        ]

    # Display tasks
    if tasks:
        for task in tasks:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 2])

                with col1:
                    priority_emoji = {
                        "Critical": "🔴",
                        "High": "🟠",
                        "Medium": "🟡",
                        "Low": "🟢"
                    }.get(task.get("priority", "Medium"), "⚪")

                    st.markdown(f"**{priority_emoji} {task.get('title', 'Untitled')}**")
                    st.caption(f"#{task.get('task_number', 'N/A')} • Assigned by: {task.get('assigned_by', 'Unknown')}")

                with col2:
                    st.caption(f"Type: {task.get('type', 'N/A')}")
                    st.caption(f"Due: {task.get('due_date', 'N/A')}")

                with col3:
                    status_color = {
                        "Pending": "🟡",
                        "In Progress": "🔵",
                        "Completed": "🟢"
                    }.get(task.get("status", "Pending"), "⚪")
                    st.caption(status_color + " " + task.get("status", "Unknown"))

                with col4:
                    if st.button("📝 Open", key=f"open_task_{task['id']}"):
                        st.session_state.selected_task = task
                        st.info(f"Opening task: {task.get('title')}")

                st.divider()
    else:
        st.info("✅ No pending tasks")


def show_pending_approvals():
    """Show pending approval items"""
    st.subheader("Items Pending Your Approval")

    # Fetch pending approvals
    try:
        approvals = api_client.get_pending_approvals()
    except:
        approvals = []

    # Mock data
    if not approvals:
        approvals = [
            {
                "id": 1,
                "item_type": "Document",
                "item_number": "DOC-2024-0045",
                "item_title": "PV Module Testing SOP",
                "submitted_by": "Jane Technician",
                "submitted_date": "2024-03-10",
                "current_step": "Quality Manager Approval",
                "urgency": "Normal"
            },
            {
                "id": 2,
                "item_type": "Form",
                "item_number": "CAL-LOG-2024-0123",
                "item_title": "Equipment Calibration Log - DMM-001",
                "submitted_by": "Bob Calibrator",
                "submitted_date": "2024-03-11",
                "current_step": "Technical Approval",
                "urgency": "High"
            },
            {
                "id": 3,
                "item_type": "Document",
                "item_number": "DOC-2024-0046",
                "item_title": "Quality Manual Update v2.1",
                "submitted_by": "Alice QA Lead",
                "submitted_date": "2024-03-09",
                "current_step": "Management Review",
                "urgency": "Critical"
            }
        ]

    if approvals:
        for item in approvals:
            with st.expander(
                f"{'🔴' if item.get('urgency') == 'Critical' else '🟡' if item.get('urgency') == 'High' else '🟢'} "
                f"{item.get('item_type', 'Item')}: {item.get('item_title', 'Untitled')}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Number:** {item.get('item_number', 'N/A')}")
                    st.markdown(f"**Type:** {item.get('item_type', 'N/A')}")
                    st.markdown(f"**Submitted by:** {item.get('submitted_by', 'Unknown')}")

                with col2:
                    st.markdown(f"**Submitted:** {item.get('submitted_date', 'N/A')}")
                    st.markdown(f"**Current step:** {item.get('current_step', 'N/A')}")
                    st.markdown(f"**Urgency:** {item.get('urgency', 'Normal')}")

                st.divider()

                # Review section
                st.markdown("### Review & Decision")

                review_comment = st.text_area(
                    "Comments",
                    key=f"comment_{item['id']}",
                    placeholder="Enter your review comments..."
                )

                col1, col2, col3 = st.columns([2, 2, 6])

                with col1:
                    if st.button("✅ Approve", key=f"approve_{item['id']}", type="primary"):
                        success = api_client.approve_item(
                            item.get('item_type', 'document').lower(),
                            item['id'],
                            review_comment
                        )
                        if success:
                            st.success(f"✅ {item.get('item_title')} approved successfully!")
                            st.rerun()

                with col2:
                    if st.button("❌ Reject", key=f"reject_{item['id']}"):
                        if review_comment:
                            success = api_client.reject_item(
                                item.get('item_type', 'document').lower(),
                                item['id'],
                                review_comment
                            )
                            if success:
                                st.warning(f"❌ {item.get('item_title')} rejected")
                                st.rerun()
                        else:
                            st.error("Please provide rejection comments")

                with col3:
                    if st.button("📋 View Details", key=f"view_{item['id']}"):
                        st.info(f"Opening detailed view for {item.get('item_number')}")

    else:
        st.info("✅ No items pending approval")


def show_workflow_status():
    """Show workflow status tracking"""
    st.subheader("Workflow Status Tracking")

    # Search
    search_query = st.text_input(
        "Search by document/form number",
        placeholder="Enter number to track..."
    )

    if search_query:
        st.markdown("### Workflow Progress")

        # Mock workflow stages
        stages = [
            {"stage": "Submission", "status": "Completed", "user": "Jane Technician", "date": "2024-03-10 10:30", "comment": "Initial submission"},
            {"stage": "Technical Review", "status": "Completed", "user": "Bob Engineer", "date": "2024-03-11 14:20", "comment": "Technical review passed"},
            {"stage": "Quality Review", "status": "In Progress", "user": "Alice QA", "date": "-", "comment": "Pending"},
            {"stage": "Management Approval", "status": "Pending", "user": "-", "date": "-", "comment": "Awaiting previous step"},
            {"stage": "Final Release", "status": "Pending", "user": "-", "date": "-", "comment": "Awaiting previous steps"}
        ]

        # Visual workflow
        for i, stage in enumerate(stages):
            col1, col2, col3, col4 = st.columns([2, 2, 2, 4])

            with col1:
                status_icon = {
                    "Completed": "✅",
                    "In Progress": "🔄",
                    "Pending": "⏳"
                }.get(stage["status"], "⚪")

                st.markdown(f"**{i+1}. {stage['stage']}**")

            with col2:
                st.markdown(f"{status_icon} {stage['status']}")

            with col3:
                st.markdown(f"👤 {stage['user']}")

            with col4:
                st.caption(f"📅 {stage['date']} • {stage['comment']}")

            if i < len(stages) - 1:
                st.markdown("↓")

    else:
        st.info("Enter a document/form number to track workflow status")


def show_approval_history():
    """Show approval history"""
    st.subheader("Approval History")

    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", datetime(2024, 1, 1))
    with col2:
        end_date = st.date_input("To Date", datetime(2024, 12, 31))

    # Mock approval history
    history = pd.DataFrame({
        'Date': ['2024-03-11', '2024-03-10', '2024-03-09', '2024-03-08'],
        'Item Number': ['DOC-2024-0044', 'CAL-LOG-2024-0122', 'DOC-2024-0043', 'TEST-REP-2024-0089'],
        'Item Title': [
            'Calibration Procedure v1.5',
            'Equipment Cal Log - DMM-001',
            'Safety Procedure Update',
            'PV Module Test Report'
        ],
        'Action': ['Approved', 'Approved', 'Rejected', 'Approved'],
        'Comment': [
            'All requirements met',
            'Verified calibration data',
            'Missing safety requirements',
            'Test results acceptable'
        ]
    })

    # Style the dataframe
    def color_action(val):
        color = 'green' if val == 'Approved' else 'red' if val == 'Rejected' else 'black'
        return f'color: {color}'

    styled_df = history.style.applymap(color_action, subset=['Action'])
    st.dataframe(styled_df, use_container_width=True)

    # Export option
    if st.button("📥 Export History"):
        csv = history.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"approval_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
