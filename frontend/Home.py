"""
LIMS-QMS Platform - Streamlit Dashboard Home
SESSION 9: Analytics Dashboard & Customer Portal
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="LIMS-QMS Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-healthy { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-critical { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🔬 LIMS-QMS Platform</div>', unsafe_allow_html=True)
st.markdown("### AI-Powered Laboratory Information Management System & Quality Management System")
st.markdown("**For Solar PV Testing & R&D Laboratories | ISO 17025/9001 Compliance**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100.png?text=LIMS-QMS+Logo", use_container_width=True)
    st.markdown("### Navigation")
    st.markdown("📊 **Executive Dashboard**")
    st.markdown("🔧 **Equipment Management**")
    st.markdown("🧪 **Test Requests**")
    st.markdown("⚠️ **Non-Conformances**")
    st.markdown("🔍 **Audit & Risk**")
    st.markdown("🤖 **AI Insights**")
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.metric("Active Tests", "23")
    st.metric("Equipment Due Cal", "5")
    st.metric("Open NCs", "3")

# Main Dashboard - Executive KPIs
st.markdown("## 📊 Executive Dashboard")

# KPI Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Test Requests (MTD)",
        value="47",
        delta="+12%",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="OEE Average",
        value="87.3%",
        delta="+2.3%",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="Quality Score",
        value="94.5%",
        delta="+1.2%",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="Open NCs",
        value="3",
        delta="-2",
        delta_color="inverse"
    )

with col5:
    st.metric(
        label="Revenue (MTD)",
        value="₹12.5L",
        delta="+18%",
        delta_color="normal"
    )

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Test Request Trend (Last 6 Months)")

    # Mock data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    test_requests = [45, 52, 48, 55, 51, 47]

    fig = px.line(
        x=months, y=test_requests,
        labels={'x': 'Month', 'y': 'Test Requests'},
        markers=True
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Test Status Distribution")

    # Mock data
    statuses = ['Completed', 'In Progress', 'Pending', 'On Hold']
    counts = [38, 15, 8, 2]
    colors = ['#28a745', '#1f77b4', '#ffc107', '#dc3545']

    fig = go.Figure(data=[go.Pie(
        labels=statuses,
        values=counts,
        marker_colors=colors,
        hole=0.4
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Equipment OEE Performance")

    # Mock data
    equipment = ['Thermal Chamber', 'UV Test Unit', 'Humidity Chamber', 'Tensile Tester', 'Thermal Cycle']
    oee = [92, 88, 85, 79, 95]

    fig = px.bar(
        x=equipment, y=oee,
        labels={'x': 'Equipment', 'y': 'OEE (%)'},
        color=oee,
        color_continuous_scale='RdYlGn'
    )
    fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Target: 85%")
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Non-Conformance Trend")

    # Mock data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    ncs = [8, 6, 5, 7, 4, 3]

    fig = px.area(
        x=months, y=ncs,
        labels={'x': 'Month', 'y': 'Open NCs'},
    )
    fig.update_traces(fillcolor='rgba(220, 53, 69, 0.3)', line_color='#dc3545')
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# AI Insights Section
st.markdown("## 🤖 AI-Powered Insights (SESSION 10)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ⚠️ Equipment Failure Predictions")
    st.markdown("""
    <div class="metric-card">
        <span class="status-indicator status-critical"></span>
        <strong>Thermal Chamber #2</strong><br>
        Failure Risk: 78%<br>
        Predicted Date: 2024-12-15<br>
        <em>Action: Schedule preventive maintenance</em>
    </div>
    <div class="metric-card">
        <span class="status-indicator status-warning"></span>
        <strong>UV Test Unit #1</strong><br>
        Failure Risk: 45%<br>
        Predicted Date: 2025-01-20<br>
        <em>Action: Monitor closely</em>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 💡 NC Root Cause Suggestions")
    st.markdown("""
    <div class="metric-card">
        <strong>NC-2024-023</strong><br>
        AI Suggested: <em>Inadequate calibration frequency</em><br>
        Confidence: 85%<br>
        Similar Cases: NC-2024-001, NC-2024-015
    </div>
    <div class="metric-card">
        <strong>NC-2024-024</strong><br>
        AI Suggested: <em>Insufficient training</em><br>
        Confidence: 90%<br>
        Similar Cases: NC-2024-005, NC-2024-018
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("### ⏱️ Test Duration Estimates")
    st.markdown("""
    <div class="metric-card">
        <strong>TRQ-2024-0145</strong><br>
        IEC 61215 Testing<br>
        Estimated: 42 days ± 5 days<br>
        Confidence: 88%
    </div>
    <div class="metric-card">
        <strong>TRQ-2024-0146</strong><br>
        IEC 61730 Testing<br>
        Estimated: 28 days ± 4 days<br>
        Confidence: 92%
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Alerts Section
st.markdown("## 🔔 Recent Alerts")

alerts_data = {
    "Type": ["Calibration Due", "Training Expiry", "NC Follow-up", "Equipment", "Test Delay"],
    "Description": [
        "Thermal Chamber #3 calibration due in 7 days",
        "John Doe - IEC 61215 training expires in 15 days",
        "NC-2024-020 CAPA effectiveness verification due",
        "UV Test Unit showing OEE decline trend",
        "TRQ-2024-0142 may exceed estimated duration"
    ],
    "Priority": ["High", "Medium", "High", "Medium", "Low"],
    "Date": ["2024-11-09", "2024-11-08", "2024-11-09", "2024-11-08", "2024-11-07"]
}

df_alerts = pd.DataFrame(alerts_data)
st.dataframe(df_alerts, use_container_width=True, hide_index=True)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <strong>LIMS-QMS Platform v1.0.0</strong><br>
    Powered by AI | ISO 17025/9001 Compliant | SESSION 10: AI Integration & Production Deployment<br>
    © 2024 Solar PV Testing Laboratory
</div>
""", unsafe_allow_html=True)
