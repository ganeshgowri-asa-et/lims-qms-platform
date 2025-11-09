"""
Dashboard Page
"""
import streamlit as st
from utils.api_client import APIClient


def show():
    """Main dashboard page"""
    st.title("📊 LIMS/QMS Dashboard")

    st.markdown("---")

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Get test requests
        all_requests = APIClient.get_test_requests()
        draft_requests = [r for r in all_requests if r['status'] == 'draft']
        submitted_requests = [r for r in all_requests if r['status'] == 'submitted']
        in_progress_requests = [r for r in all_requests if r['status'] in ['approved', 'in_progress']]

        # Get samples
        all_samples = APIClient.get_samples()
        pending_samples = [s for s in all_samples if s['status'] == 'pending']
        in_testing_samples = [s for s in all_samples if s['status'] == 'in_testing']

        with col1:
            st.metric("Total Test Requests", len(all_requests))
            st.caption(f"📝 {len(draft_requests)} Draft")

        with col2:
            st.metric("Pending Approval", len(submitted_requests))
            st.caption(f"⏳ Awaiting approval")

        with col3:
            st.metric("In Progress", len(in_progress_requests))
            st.caption(f"🔄 Active tests")

        with col4:
            st.metric("Total Samples", len(all_samples))
            st.caption(f"🧪 {len(in_testing_samples)} In Testing")

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")

    st.markdown("---")

    # Recent activity section
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📋 Recent Test Requests")
        try:
            recent_requests = APIClient.get_test_requests()[:5]  # Get last 5

            if recent_requests:
                for req in recent_requests:
                    status_color = {
                        'draft': '🟡',
                        'submitted': '🟠',
                        'approved': '🟢',
                        'in_progress': '🔵',
                        'completed': '✅',
                        'on_hold': '⏸️',
                        'cancelled': '❌'
                    }.get(req['status'], '⚪')

                    st.write(f"{status_color} **{req['trq_number']}** - {req['project_name']}")
                    st.caption(f"Priority: {req['priority'].upper()} | Created: {req['created_at'][:10]}")
                    st.markdown("---")
            else:
                st.info("No test requests yet.")

        except Exception as e:
            st.error(f"Error: {e}")

    with col_right:
        st.subheader("🧪 Recent Samples")
        try:
            recent_samples = APIClient.get_samples()[:5]  # Get last 5

            if recent_samples:
                for sample in recent_samples:
                    status_color = {
                        'pending': '🟡',
                        'received': '🟢',
                        'in_testing': '🔵',
                        'completed': '✅',
                        'rejected': '❌'
                    }.get(sample['status'], '⚪')

                    st.write(f"{status_color} **{sample['sample_number']}** - {sample['sample_name']}")
                    st.caption(f"Type: {sample['sample_type']} | Created: {sample['created_at'][:10]}")
                    st.markdown("---")
            else:
                st.info("No samples yet.")

        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")

    # Status distribution
    st.subheader("📈 Status Distribution")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Test Request Status**")
        try:
            status_counts = {}
            for req in all_requests:
                status = req['status']
                status_counts[status] = status_counts.get(status, 0) + 1

            for status, count in status_counts.items():
                st.write(f"- {status.upper()}: {count}")
        except:
            st.info("No data available")

    with col2:
        st.write("**Sample Status**")
        try:
            sample_status_counts = {}
            for sample in all_samples:
                status = sample['status']
                sample_status_counts[status] = sample_status_counts.get(status, 0) + 1

            for status, count in sample_status_counts.items():
                st.write(f"- {status.upper()}: {count}")
        except:
            st.info("No data available")

    st.markdown("---")

    # Quick stats
    st.subheader("📊 Quick Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            high_priority = len([r for r in all_requests if r['priority'] == 'high'])
            urgent_priority = len([r for r in all_requests if r['priority'] == 'urgent'])
            st.metric("High Priority Requests", high_priority + urgent_priority)
        except:
            st.metric("High Priority Requests", 0)

    with col2:
        try:
            quotes_generated = len([r for r in all_requests if r.get('quote_number')])
            st.metric("Quotes Generated", quotes_generated)
        except:
            st.metric("Quotes Generated", 0)

    with col3:
        try:
            completed_samples = len([s for s in all_samples if s['status'] == 'completed'])
            st.metric("Completed Samples", completed_samples)
        except:
            st.metric("Completed Samples", 0)
