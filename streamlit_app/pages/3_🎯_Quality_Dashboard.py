"""
Quality Dashboard - Quality Metrics, NC, CAPA, and Audit Findings
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Quality Dashboard", page_icon="🎯", layout="wide")

# Check role access
if st.session_state.get('user_role') not in ['executive', 'quality manager', 'lab manager']:
    st.error("Access Denied: This dashboard is only available to authorized roles")
    st.stop()

st.title("🎯 Quality Dashboard")
st.markdown("Quality Management System Performance")

API_BASE_URL = "http://localhost:8000/api"

# Fetch data functions
@st.cache_data(ttl=300)
def fetch_quality_kpis():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/kpis/quality")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Mock data
    return {
        "nc_trend": [
            {"month": "2025-05", "count": 8},
            {"month": "2025-06", "count": 6},
            {"month": "2025-07", "count": 7},
            {"month": "2025-08", "count": 5},
            {"month": "2025-09", "count": 4},
            {"month": "2025-10", "count": 3}
        ],
        "nc_by_severity": [
            {"severity": "Critical", "count": 2},
            {"severity": "Major", "count": 8},
            {"severity": "Minor", "count": 23}
        ],
        "capa_effectiveness": 87.5,
        "audit_findings": {
            "total": 15,
            "by_type": [
                {"type": "Observation", "count": 8},
                {"type": "Minor NC", "count": 5},
                {"type": "Major NC", "count": 2}
            ]
        }
    }

@st.cache_data(ttl=300)
def fetch_quality_trend():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/trends/quality-metrics?months=12")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    # Mock data
    months = pd.date_range(end=datetime.now(), periods=12, freq='M')
    return [
        {
            "month": month.strftime("%Y-%m"),
            "nc_count": max(3, 8 - i // 2),
            "sample_count": 100 + i * 5,
            "quality_rate": 96 + (i % 3) * 0.5
        }
        for i, month in enumerate(months)
    ]

kpis = fetch_quality_kpis()
quality_trend = fetch_quality_trend()

# ============================================================================
# QUALITY KPIs
# ============================================================================

st.subheader("📊 Quality Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    current_nc = kpis['nc_trend'][-1]['count']
    prev_nc = kpis['nc_trend'][-2]['count']
    st.metric(
        label="⚠️ Non-Conformances (MTD)",
        value=current_nc,
        delta=f"{current_nc - prev_nc}",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="✅ CAPA Effectiveness",
        value=f"{kpis['capa_effectiveness']:.1f}%",
        delta="Target: 85%"
    )

with col3:
    st.metric(
        label="📋 Audit Findings (YTD)",
        value=kpis['audit_findings']['total'],
        delta="ISO 17025"
    )

with col4:
    total_nc = sum(s['count'] for s in kpis['nc_by_severity'])
    st.metric(
        label="📈 Total NC (YTD)",
        value=total_nc,
        delta="-5 vs last year"
    )

st.markdown("---")

# ============================================================================
# NON-CONFORMANCE TRENDS
# ============================================================================

st.subheader("📉 Non-Conformance Analysis")

nc_col1, nc_col2 = st.columns(2)

with nc_col1:
    # NC Trend over time
    df_nc_trend = pd.DataFrame(kpis['nc_trend'])
    fig_nc_trend = go.Figure()
    fig_nc_trend.add_trace(go.Scatter(
        x=df_nc_trend['month'],
        y=df_nc_trend['count'],
        mode='lines+markers',
        name='NC Count',
        line=dict(color='#d62728', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(214, 39, 40, 0.2)'
    ))
    fig_nc_trend.update_layout(
        title='Non-Conformance Trend (Last 6 Months)',
        xaxis_title='Month',
        yaxis_title='NC Count',
        hovermode='x unified',
        height=350
    )
    st.plotly_chart(fig_nc_trend, use_container_width=True)

with nc_col2:
    # NC by Severity
    df_nc_severity = pd.DataFrame(kpis['nc_by_severity'])
    fig_nc_severity = px.pie(
        df_nc_severity,
        values='count',
        names='severity',
        title='NC Distribution by Severity',
        color='severity',
        color_discrete_map={
            'Critical': '#d62728',
            'Major': '#ff7f0e',
            'Minor': '#2ca02c'
        }
    )
    fig_nc_severity.update_traces(textposition='inside', textinfo='percent+label+value')
    fig_nc_severity.update_layout(height=350)
    st.plotly_chart(fig_nc_severity, use_container_width=True)

# NC by Category (Mock data)
st.markdown("#### Non-Conformance by Category")
nc_category = pd.DataFrame({
    'Category': ['Documentation', 'Process', 'Equipment', 'Personnel', 'Material'],
    'Count': [8, 12, 5, 4, 4]
})

fig_nc_cat = px.bar(
    nc_category,
    x='Category',
    y='Count',
    title='NC Distribution by Category',
    color='Count',
    color_continuous_scale='Reds'
)
fig_nc_cat.update_layout(height=300, showlegend=False)
st.plotly_chart(fig_nc_cat, use_container_width=True)

st.markdown("---")

# ============================================================================
# CAPA PERFORMANCE
# ============================================================================

st.subheader("🔧 CAPA Performance")

capa_col1, capa_col2, capa_col3 = st.columns(3)

with capa_col1:
    # CAPA Effectiveness Gauge
    fig_capa = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=kpis['capa_effectiveness'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "CAPA Effectiveness (%)"},
        delta={'reference': 85, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 70], 'color': "lightcoral"},
                {'range': [70, 85], 'color': "lightyellow"},
                {'range': [85, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    fig_capa.update_layout(height=300)
    st.plotly_chart(fig_capa, use_container_width=True)

with capa_col2:
    # CAPA Status (Mock data)
    st.markdown("#### CAPA Action Status")
    capa_status = pd.DataFrame({
        'Status': ['Planned', 'In Progress', 'Completed', 'Overdue'],
        'Count': [5, 12, 28, 2]
    })

    fig_capa_status = px.funnel(
        capa_status,
        x='Count',
        y='Status',
        color='Status',
        color_discrete_map={
            'Planned': '#1f77b4',
            'In Progress': '#ff7f0e',
            'Completed': '#2ca02c',
            'Overdue': '#d62728'
        }
    )
    fig_capa_status.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_capa_status, use_container_width=True)

with capa_col3:
    # Recent CAPA Actions
    st.markdown("#### Recent CAPA Actions")
    recent_capa = pd.DataFrame({
        'CAPA #': ['CAPA-2025-015', 'CAPA-2025-014', 'CAPA-2025-013',
                  'CAPA-2025-012', 'CAPA-2025-011'],
        'Status': ['In Progress', 'Completed', 'In Progress', 'Completed', 'In Progress'],
        'Due Date': ['2025-11-20', '2025-11-05', '2025-11-25', '2025-10-30', '2025-11-18']
    })

    st.dataframe(
        recent_capa,
        use_container_width=True,
        hide_index=True,
        height=250
    )

st.markdown("---")

# ============================================================================
# AUDIT FINDINGS
# ============================================================================

st.subheader("📋 Audit Findings Analysis")

audit_col1, audit_col2 = st.columns(2)

with audit_col1:
    # Audit Findings by Type
    df_findings = pd.DataFrame(kpis['audit_findings']['by_type'])
    fig_findings = px.bar(
        df_findings,
        x='type',
        y='count',
        title='Audit Findings by Type (YTD)',
        color='type',
        color_discrete_map={
            'Observation': '#2ca02c',
            'Minor NC': '#ff7f0e',
            'Major NC': '#d62728'
        }
    )
    fig_findings.update_layout(
        xaxis_title='Finding Type',
        yaxis_title='Count',
        showlegend=False,
        height=350
    )
    st.plotly_chart(fig_findings, use_container_width=True)

with audit_col2:
    # Audit Schedule (Mock data)
    st.markdown("#### Upcoming Audits")
    upcoming_audits = pd.DataFrame({
        'Audit': ['Internal Audit - Lab', 'ISO 17025 Surveillance',
                 'Equipment Calibration', 'Document Control'],
        'Date': ['2025-11-15', '2025-12-05', '2025-11-22', '2025-11-30'],
        'Type': ['Internal', 'External', 'Internal', 'Internal']
    })

    st.dataframe(
        upcoming_audits,
        use_container_width=True,
        hide_index=True,
        height=250
    )

st.markdown("---")

# ============================================================================
# QUALITY RATE TREND
# ============================================================================

st.subheader("📈 Overall Quality Performance")

df_quality_trend = pd.DataFrame(quality_trend)

fig_quality = go.Figure()

# Add quality rate line
fig_quality.add_trace(go.Scatter(
    x=df_quality_trend['month'],
    y=df_quality_trend['quality_rate'],
    mode='lines+markers',
    name='Quality Rate (%)',
    yaxis='y',
    line=dict(color='#2ca02c', width=3),
    marker=dict(size=8)
))

# Add NC count bars
fig_quality.add_trace(go.Bar(
    x=df_quality_trend['month'],
    y=df_quality_trend['nc_count'],
    name='NC Count',
    yaxis='y2',
    marker_color='rgba(214, 39, 40, 0.6)'
))

# Add target line
fig_quality.add_trace(go.Scatter(
    x=df_quality_trend['month'],
    y=[95] * len(df_quality_trend),
    mode='lines',
    name='Target (95%)',
    line=dict(color='red', width=2, dash='dash'),
    yaxis='y'
))

fig_quality.update_layout(
    title='Quality Rate and NC Trend (12 Months)',
    xaxis=dict(title='Month'),
    yaxis=dict(
        title='Quality Rate (%)',
        side='left',
        range=[90, 100]
    ),
    yaxis2=dict(
        title='NC Count',
        side='right',
        overlaying='y'
    ),
    hovermode='x unified',
    height=400,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

st.plotly_chart(fig_quality, use_container_width=True)

# ============================================================================
# RISK MATRIX (5x5)
# ============================================================================

st.markdown("---")
st.subheader("🎲 Risk Matrix (5x5)")

# Mock risk data
risk_data = pd.DataFrame({
    'Risk': ['R1: Equipment Failure', 'R2: Staff Competency', 'R3: Sample Contamination',
            'R4: Data Integrity', 'R5: Customer Complaint', 'R6: Calibration Lapse'],
    'Likelihood': [3, 2, 2, 1, 3, 2],
    'Impact': [4, 3, 5, 4, 3, 4],
    'Score': [12, 6, 10, 4, 9, 8]
})

risk_data['Level'] = risk_data['Score'].apply(
    lambda x: 'Critical' if x >= 15 else 'High' if x >= 10 else 'Medium' if x >= 5 else 'Low'
)

# Create scatter plot for risk matrix
fig_risk = px.scatter(
    risk_data,
    x='Likelihood',
    y='Impact',
    size='Score',
    color='Level',
    hover_name='Risk',
    title='Risk Assessment Matrix',
    color_discrete_map={
        'Low': '#2ca02c',
        'Medium': '#ffcc00',
        'High': '#ff7f0e',
        'Critical': '#d62728'
    },
    size_max=30
)

fig_risk.update_xaxes(range=[0, 6], title='Likelihood (1-5)')
fig_risk.update_yaxes(range=[0, 6], title='Impact (1-5)')
fig_risk.update_layout(height=400)

st.plotly_chart(fig_risk, use_container_width=True)

# Risk register table
st.markdown("#### Risk Register Summary")
st.dataframe(
    risk_data[['Risk', 'Likelihood', 'Impact', 'Score', 'Level']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score": st.column_config.ProgressColumn(
            "Risk Score",
            min_value=0,
            max_value=25,
            format="%d"
        ),
        "Level": st.column_config.TextColumn(
            "Risk Level"
        )
    }
)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
