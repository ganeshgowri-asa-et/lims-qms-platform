"""
Operational Dashboard - Lab Operations and Resource Metrics
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Operational Dashboard", page_icon="⚙️", layout="wide")

# Check role access
if st.session_state.get('user_role') not in ['executive', 'lab manager', 'technician']:
    st.error("Access Denied: This dashboard is only available to authorized roles")
    st.stop()

st.title("⚙️ Operational Dashboard")
st.markdown("Laboratory Operations and Resource Management")

API_BASE_URL = "http://localhost:8000/api"

# Fetch data functions
@st.cache_data(ttl=300)
def fetch_operational_kpis():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/kpis/operational")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Mock data
    return {
        "avg_turnaround_days": 7.2,
        "equipment_calibration": {
            "total": 45,
            "overdue": 3,
            "compliance_rate": 93.3
        },
        "training_compliance": 87.5,
        "sample_status_distribution": [
            {"status": "Received", "count": 15},
            {"status": "In Progress", "count": 22},
            {"status": "Testing", "count": 18},
            {"status": "Completed", "count": 35},
            {"status": "Reported", "count": 28}
        ]
    }

kpis = fetch_operational_kpis()

# ============================================================================
# OPERATIONAL KPIs
# ============================================================================

st.subheader("📊 Operational Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="⏱️ Avg Turnaround Time",
        value=f"{kpis['avg_turnaround_days']:.1f} days",
        delta="-0.5 days",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="🔧 Equipment Calibration",
        value=f"{kpis['equipment_calibration']['compliance_rate']:.1f}%",
        delta=f"{kpis['equipment_calibration']['overdue']} overdue",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="📚 Training Compliance",
        value=f"{kpis['training_compliance']:.1f}%",
        delta="Target: 85%"
    )

with col4:
    total_active = sum(s['count'] for s in kpis['sample_status_distribution']
                      if s['status'] in ['Received', 'In Progress', 'Testing'])
    st.metric(
        label="🔬 Active Samples",
        value=total_active,
        delta="+8"
    )

st.markdown("---")

# ============================================================================
# SAMPLE STATUS DISTRIBUTION
# ============================================================================

st.subheader("📦 Sample Status Distribution")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Pie chart
    df_status = pd.DataFrame(kpis['sample_status_distribution'])
    fig_pie = px.pie(
        df_status,
        values='count',
        names='status',
        title='Sample Status Breakdown',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    # Bar chart
    fig_bar = px.bar(
        df_status,
        x='status',
        y='count',
        title='Sample Count by Status',
        color='status',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_layout(
        xaxis_title="Status",
        yaxis_title="Number of Samples",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ============================================================================
# EQUIPMENT & CALIBRATION STATUS
# ============================================================================

st.subheader("🔧 Equipment & Calibration Status")

equip_col1, equip_col2, equip_col3 = st.columns(3)

with equip_col1:
    st.markdown("#### Equipment Overview")
    st.metric("Total Equipment", kpis['equipment_calibration']['total'])
    st.metric("Calibration Due Soon", 7, delta="Within 30 days", delta_color="off")
    st.metric("Overdue Calibration", kpis['equipment_calibration']['overdue'],
             delta_color="inverse")

with equip_col2:
    # Calibration compliance gauge
    fig_cal = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpis['equipment_calibration']['compliance_rate'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Calibration Compliance (%)"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 80], 'color': "lightcoral"},
                {'range': [80, 95], 'color': "lightyellow"},
                {'range': [95, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))
    fig_cal.update_layout(height=300)
    st.plotly_chart(fig_cal, use_container_width=True)

with equip_col3:
    # Mock equipment by category
    equipment_data = pd.DataFrame({
        'Category': ['Testing Equipment', 'Measurement Instruments',
                    'Environmental Chambers', 'Safety Equipment'],
        'Count': [15, 12, 10, 8]
    })
    fig_equip = px.bar(
        equipment_data,
        x='Count',
        y='Category',
        orientation='h',
        title='Equipment by Category',
        color='Count',
        color_continuous_scale='Blues'
    )
    fig_equip.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_equip, use_container_width=True)

st.markdown("---")

# ============================================================================
# TRAINING & COMPETENCY
# ============================================================================

st.subheader("📚 Training & Competency Status")

train_col1, train_col2 = st.columns(2)

with train_col1:
    # Training compliance by department (mock data)
    training_dept = pd.DataFrame({
        'Department': ['Quality', 'Testing', 'Engineering', 'Admin'],
        'Compliance': [92, 85, 88, 90],
        'Target': [85, 85, 85, 85]
    })

    fig_training = go.Figure()
    fig_training.add_trace(go.Bar(
        name='Actual',
        x=training_dept['Department'],
        y=training_dept['Compliance'],
        marker_color='steelblue'
    ))
    fig_training.add_trace(go.Scatter(
        name='Target',
        x=training_dept['Department'],
        y=training_dept['Target'],
        mode='markers+lines',
        marker=dict(color='red', size=10),
        line=dict(color='red', width=2, dash='dash')
    ))
    fig_training.update_layout(
        title='Training Compliance by Department',
        xaxis_title='Department',
        yaxis_title='Compliance (%)',
        barmode='group',
        height=350
    )
    st.plotly_chart(fig_training, use_container_width=True)

with train_col2:
    # Training schedule (mock data)
    st.markdown("#### Upcoming Training Sessions")

    upcoming_training = pd.DataFrame({
        'Training': ['ISO 17025 Audit', 'Equipment Operation', 'Safety Procedures',
                    'Quality Management', 'Data Analysis'],
        'Date': ['2025-11-15', '2025-11-18', '2025-11-22', '2025-11-25', '2025-11-28'],
        'Attendees': [12, 8, 15, 10, 6]
    })

    st.dataframe(
        upcoming_training,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Training": st.column_config.TextColumn("Training Name", width="medium"),
            "Date": st.column_config.DateColumn("Scheduled Date", width="small"),
            "Attendees": st.column_config.NumberColumn("Expected Attendees", width="small")
        }
    )

st.markdown("---")

# ============================================================================
# WORKLOAD ANALYSIS
# ============================================================================

st.subheader("📊 Workload Analysis")

# Mock workload data
workload_data = pd.DataFrame({
    'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    'Received': [25, 32, 28, 30],
    'Completed': [22, 28, 30, 25],
    'Backlog': [15, 19, 17, 22]
})

fig_workload = go.Figure()
fig_workload.add_trace(go.Bar(name='Received', x=workload_data['Week'],
                              y=workload_data['Received'], marker_color='lightblue'))
fig_workload.add_trace(go.Bar(name='Completed', x=workload_data['Week'],
                              y=workload_data['Completed'], marker_color='lightgreen'))
fig_workload.add_trace(go.Scatter(name='Backlog', x=workload_data['Week'],
                                 y=workload_data['Backlog'], mode='lines+markers',
                                 marker=dict(size=10, color='red'),
                                 line=dict(width=3, color='red')))

fig_workload.update_layout(
    title='Weekly Workload Trend',
    xaxis_title='Week',
    yaxis_title='Number of Samples',
    barmode='group',
    height=400
)
st.plotly_chart(fig_workload, use_container_width=True)

# ============================================================================
# ALERTS AND NOTIFICATIONS
# ============================================================================

st.markdown("---")
st.subheader("🔔 Alerts & Notifications")

alert_col1, alert_col2, alert_col3 = st.columns(3)

with alert_col1:
    st.warning("⚠️ **Calibration Alert**\n\n3 equipment items overdue for calibration")

with alert_col2:
    st.info("ℹ️ **Training Reminder**\n\n7 employees have pending training completion")

with alert_col3:
    st.success("✅ **Capacity Status**\n\nLab capacity at 75% - optimal range")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
