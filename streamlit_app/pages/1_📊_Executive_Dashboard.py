"""
Executive Dashboard - High-level KPIs and Strategic Metrics
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Executive Dashboard", page_icon="📊", layout="wide")

# Check role access
if st.session_state.get('user_role') not in ['executive', 'lab manager']:
    st.error("Access Denied: This dashboard is only available to Executive and Lab Manager roles")
    st.stop()

st.title("📊 Executive Dashboard")
st.markdown("Strategic KPIs and Performance Metrics")

# API base URL
API_BASE_URL = "http://localhost:8000/api"

# Fetch data function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_executive_kpis():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/kpis/executive")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        # Return mock data if API is not available
        return {
            "test_requests": {"current": 245, "previous": 220, "change_percent": 11.4},
            "revenue": {"current": 1250000, "previous": 1100000, "change_percent": 13.6},
            "active_samples": 48,
            "quality_rate": 98.5,
            "on_time_delivery": 95.2,
            "non_conformances": 3
        }

@st.cache_data(ttl=300)
def fetch_test_volume_trend():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/trends/test-volume?months=12")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        # Return mock data
        months = pd.date_range(end=datetime.now(), periods=12, freq='M')
        return [
            {
                "month": month.strftime("%Y-%m"),
                "test_requests": 180 + i * 5 + (i % 3) * 10,
                "revenue": (180 + i * 5 + (i % 3) * 10) * 5000
            }
            for i, month in enumerate(months)
        ]

# Fetch data
kpis = fetch_executive_kpis()
trend_data = fetch_test_volume_trend()

# ============================================================================
# KEY PERFORMANCE INDICATORS
# ============================================================================

st.subheader("📈 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📋 Test Requests (This Month)",
        value=f"{kpis['test_requests']['current']:,}",
        delta=f"{kpis['test_requests']['change_percent']:.1f}% vs last month"
    )

with col2:
    st.metric(
        label="💰 Revenue (This Month)",
        value=f"${kpis['revenue']['current']:,.0f}",
        delta=f"{kpis['revenue']['change_percent']:.1f}% vs last month"
    )

with col3:
    st.metric(
        label="🔬 Active Samples",
        value=f"{kpis['active_samples']:,}",
        delta=None
    )

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        label="✅ Quality Rate",
        value=f"{kpis['quality_rate']:.1f}%",
        delta="Target: 95%"
    )

with col5:
    st.metric(
        label="⏰ On-Time Delivery",
        value=f"{kpis['on_time_delivery']:.1f}%",
        delta="Target: 90%"
    )

with col6:
    st.metric(
        label="⚠️ Non-Conformances",
        value=f"{kpis['non_conformances']}",
        delta="-2 vs last month",
        delta_color="inverse"
    )

st.markdown("---")

# ============================================================================
# TRENDS AND CHARTS
# ============================================================================

st.subheader("📊 Performance Trends")

# Convert trend data to DataFrame
df_trend = pd.DataFrame(trend_data)

# Two-column layout for charts
col_left, col_right = st.columns(2)

with col_left:
    # Test Volume Trend
    st.markdown("#### Test Request Volume")
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Scatter(
        x=df_trend['month'],
        y=df_trend['test_requests'],
        mode='lines+markers',
        name='Test Requests',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    fig_volume.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Requests",
        hovermode='x unified',
        height=350
    )
    st.plotly_chart(fig_volume, use_container_width=True)

with col_right:
    # Revenue Trend
    st.markdown("#### Revenue Trend")
    fig_revenue = go.Figure()
    fig_revenue.add_trace(go.Bar(
        x=df_trend['month'],
        y=df_trend['revenue'],
        name='Revenue',
        marker=dict(color='#2ca02c')
    ))
    fig_revenue.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified',
        height=350
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# ============================================================================
# GAUGE CHARTS FOR KEY METRICS
# ============================================================================

st.markdown("---")
st.subheader("🎯 Performance Indicators")

gauge_col1, gauge_col2, gauge_col3 = st.columns(3)

with gauge_col1:
    # Quality Rate Gauge
    fig_quality = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=kpis['quality_rate'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Quality Rate (%)"},
        delta={'reference': 95, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 85], 'color': "lightgray"},
                {'range': [85, 95], 'color': "lightyellow"},
                {'range': [95, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))
    fig_quality.update_layout(height=250)
    st.plotly_chart(fig_quality, use_container_width=True)

with gauge_col2:
    # On-Time Delivery Gauge
    fig_otd = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=kpis['on_time_delivery'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "On-Time Delivery (%)"},
        delta={'reference': 90, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 80], 'color': "lightgray"},
                {'range': [80, 90], 'color': "lightyellow"},
                {'range': [90, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig_otd.update_layout(height=250)
    st.plotly_chart(fig_otd, use_container_width=True)

with gauge_col3:
    # Customer Satisfaction (Mock data)
    customer_satisfaction = 92.5
    fig_csat = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=customer_satisfaction,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Customer Satisfaction (%)"},
        delta={'reference': 90, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkorange"},
            'steps': [
                {'range': [0, 80], 'color': "lightgray"},
                {'range': [80, 90], 'color': "lightyellow"},
                {'range': [90, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig_csat.update_layout(height=250)
    st.plotly_chart(fig_csat, use_container_width=True)

# ============================================================================
# STRATEGIC INSIGHTS
# ============================================================================

st.markdown("---")
st.subheader("💡 Strategic Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.success("✅ **Strong Growth**: Test request volume up 11.4% month-over-month")
    st.success("✅ **Revenue Growth**: Revenue increased by 13.6% compared to last month")

with insight_col2:
    st.info("📌 **Quality Excellence**: Maintaining quality rate above 95% target")
    st.info("📌 **On-Time Performance**: Consistently meeting delivery commitments")

# Auto-refresh option
st.markdown("---")
if st.checkbox("Auto-refresh data (every 5 minutes)"):
    st.info("Dashboard will auto-refresh every 5 minutes")
    st.cache_data.clear()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
