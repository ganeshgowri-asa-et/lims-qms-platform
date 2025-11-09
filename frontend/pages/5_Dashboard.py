"""Main Dashboard for NC and CAPA Overview."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from frontend.utils.api_client import APIClient

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 NC & CAPA Dashboard")
st.markdown("Real-time overview of Non-Conformances and CAPA Actions")
st.markdown("---")

# Initialize API client
api = APIClient()

# Refresh button
col1, col2, col3 = st.columns([4, 1, 1])
with col3:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

try:
    # Fetch statistics
    nc_stats = api.get_nc_statistics()
    capa_stats = api.get_capa_statistics()
    ncs = api.get_ncs(limit=1000)
    capas = api.get_capas(limit=1000)

    # =================== KEY METRICS ===================
    st.subheader("📈 Key Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Total NCs",
            nc_stats["total"],
            help="Total number of non-conformances"
        )

    with col2:
        st.metric(
            "Open NCs",
            nc_stats["open"],
            delta=f"-{nc_stats['closed']}" if nc_stats['closed'] > 0 else None,
            help="Currently open non-conformances"
        )

    with col3:
        closure_rate = (nc_stats["closed"] / nc_stats["total"] * 100) if nc_stats["total"] > 0 else 0
        st.metric(
            "Closure Rate",
            f"{closure_rate:.1f}%",
            help="Percentage of closed NCs"
        )

    with col4:
        st.metric(
            "Total CAPAs",
            capa_stats["total"],
            help="Total CAPA actions"
        )

    with col5:
        st.metric(
            "Pending CAPAs",
            capa_stats["pending"] + capa_stats["in_progress"],
            help="CAPAs pending or in progress"
        )

    with col6:
        st.metric(
            "Overdue CAPAs",
            capa_stats["overdue"],
            delta=-capa_stats["overdue"] if capa_stats["overdue"] > 0 else 0,
            delta_color="inverse",
            help="Overdue CAPA actions"
        )

    st.markdown("---")

    # =================== CHARTS ROW 1 ===================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 NC by Severity")

        if nc_stats.get("by_severity"):
            severity_data = nc_stats["by_severity"]

            fig = go.Figure(data=[go.Pie(
                labels=[s.upper() for s in severity_data.keys()],
                values=list(severity_data.values()),
                hole=0.4,
                marker=dict(colors=['#d32f2f', '#f57c00', '#fbc02d'])  # Critical, Major, Minor
            )])

            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No NC severity data available")

    with col2:
        st.subheader("📋 NC by Status")

        # Count NCs by status
        status_counts = {}
        for nc in ncs:
            status = nc['status'].replace('_', ' ').title()
            status_counts[status] = status_counts.get(status, 0) + 1

        if status_counts:
            fig = go.Figure(data=[go.Bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                marker_color='#1f77b4'
            )])

            fig.update_layout(
                xaxis_title="Status",
                yaxis_title="Count",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No NC status data available")

    # =================== CHARTS ROW 2 ===================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ CAPA by Type")

        if capa_stats.get("by_type"):
            type_data = capa_stats["by_type"]

            fig = go.Figure(data=[go.Pie(
                labels=[t.title() for t in type_data.keys()],
                values=list(type_data.values()),
                hole=0.4,
                marker=dict(colors=['#2196f3', '#4caf50'])  # Corrective, Preventive
            )])

            fig.update_layout(
                showlegend=True,
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No CAPA type data available")

    with col2:
        st.subheader("📊 CAPA Status Distribution")

        # Count CAPAs by status
        capa_status_data = {
            "Pending": capa_stats["pending"],
            "In Progress": capa_stats["in_progress"],
            "Completed": capa_stats["completed"]
        }

        fig = go.Figure(data=[go.Bar(
            x=list(capa_status_data.keys()),
            y=list(capa_status_data.values()),
            marker_color=['#ff9800', '#2196f3', '#4caf50']
        )])

        fig.update_layout(
            xaxis_title="Status",
            yaxis_title="Count",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # =================== NC SOURCE ANALYSIS ===================
    st.subheader("📍 NC by Source")

    source_counts = {}
    for nc in ncs:
        source = nc['source'].replace('_', ' ').title()
        source_counts[source] = source_counts.get(source, 0) + 1

    if source_counts:
        # Sort by count
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)

        fig = go.Figure(data=[go.Bar(
            x=[s[0] for s in sorted_sources],
            y=[s[1] for s in sorted_sources],
            marker_color='#673ab7',
            text=[s[1] for s in sorted_sources],
            textposition='auto'
        )])

        fig.update_layout(
            xaxis_title="Source",
            yaxis_title="Count",
            height=400,
            margin=dict(l=20, r=20, t=40, b=100),
            xaxis_tickangle=-45
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No NC source data available")

    st.markdown("---")

    # =================== RECENT ACTIVITY ===================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Recent Non-Conformances")

        recent_ncs = sorted(ncs, key=lambda x: x['created_at'], reverse=True)[:10]

        if recent_ncs:
            for nc in recent_ncs:
                severity_color = {
                    'critical': '🔴',
                    'major': '🟠',
                    'minor': '🟡'
                }.get(nc['severity'], '⚪')

                created = datetime.fromisoformat(nc['created_at'].replace('Z', ''))

                with st.expander(f"{severity_color} {nc['nc_number']} - {nc['title'][:50]}..."):
                    st.write(f"**Created:** {created.strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Severity:** {nc['severity'].upper()}")
                    st.write(f"**Status:** {nc['status'].replace('_', ' ').title()}")
                    st.write(f"**Detected by:** {nc['detected_by']}")
        else:
            st.info("No recent non-conformances")

    with col2:
        st.subheader("⏰ Overdue & Upcoming CAPAs")

        # Get overdue CAPAs
        overdue_capas = api.get_overdue_capas()

        if overdue_capas:
            st.markdown("**⚠️ Overdue:**")
            for capa in overdue_capas[:5]:
                st.error(f"**{capa['capa_number']}** - {capa['title'][:40]}... (Due: {capa['due_date']})")

        # Get upcoming CAPAs (due in next 7 days)
        from datetime import date, timedelta

        upcoming = []
        for capa in capas:
            if capa['status'] in ['pending', 'in_progress']:
                due = datetime.strptime(capa['due_date'], '%Y-%m-%d').date()
                days_until = (due - date.today()).days
                if 0 <= days_until <= 7:
                    upcoming.append((capa, days_until))

        if upcoming:
            st.markdown("**📅 Due in Next 7 Days:**")
            upcoming.sort(key=lambda x: x[1])
            for capa, days in upcoming[:5]:
                st.warning(f"**{capa['capa_number']}** - {capa['title'][:40]}... ({days} days)")

        if not overdue_capas and not upcoming:
            st.success("✅ All CAPAs are on track!")

    st.markdown("---")

    # =================== DEPARTMENT ANALYSIS (if data available) ===================
    st.subheader("🏢 NC by Department")

    dept_counts = {}
    for nc in ncs:
        dept = nc.get('department', 'Unknown')
        if dept and dept != 'Unknown':
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

    if dept_counts:
        sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)

        fig = go.Figure(data=[go.Bar(
            y=[d[0] for d in sorted_depts],
            x=[d[1] for d in sorted_depts],
            orientation='h',
            marker_color='#009688',
            text=[d[1] for d in sorted_depts],
            textposition='auto'
        )])

        fig.update_layout(
            xaxis_title="Count",
            yaxis_title="Department",
            height=max(300, len(sorted_depts) * 30),
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No department data available. Add department information to NCs to see this analysis.")

    st.markdown("---")

    # =================== SUMMARY TABLE ===================
    st.subheader("📋 Summary Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Non-Conformance Summary")

        nc_summary = pd.DataFrame([
            {"Metric": "Total NCs", "Value": nc_stats["total"]},
            {"Metric": "Open NCs", "Value": nc_stats["open"]},
            {"Metric": "Closed NCs", "Value": nc_stats["closed"]},
            {"Metric": "Closure Rate", "Value": f"{closure_rate:.1f}%"},
        ])

        st.dataframe(nc_summary, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### CAPA Summary")

        capa_summary = pd.DataFrame([
            {"Metric": "Total CAPAs", "Value": capa_stats["total"]},
            {"Metric": "Pending", "Value": capa_stats["pending"]},
            {"Metric": "In Progress", "Value": capa_stats["in_progress"]},
            {"Metric": "Completed", "Value": capa_stats["completed"]},
            {"Metric": "Overdue", "Value": capa_stats["overdue"]},
        ])

        st.dataframe(capa_summary, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"❌ Error loading dashboard data: {str(e)}")
    st.exception(e)

# Sidebar - Quick Actions
with st.sidebar:
    st.markdown("### 🚀 Quick Actions")

    if st.button("📝 Register NC", use_container_width=True):
        st.switch_page("pages/1_NC_Registration.py")

    if st.button("🔍 Perform RCA", use_container_width=True):
        st.switch_page("pages/3_RCA_Analysis.py")

    if st.button("✅ Manage CAPA", use_container_width=True):
        st.switch_page("pages/4_CAPA_Management.py")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This dashboard provides real-time insights into:
    - Non-conformance trends
    - CAPA effectiveness
    - Overdue actions
    - Department performance
    """)
