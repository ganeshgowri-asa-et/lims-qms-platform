"""
Test History Page
"""
import streamlit as st
import sys
from pathlib import Path
import requests
import pandas as pd
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import settings

st.set_page_config(page_title="Test History", page_icon="📜", layout="wide")

st.title("📜 Test History")
st.markdown("View and manage historical test records")

st.markdown("---")

API_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}/api/v1"

# Filters
st.markdown("### 🔍 Search & Filter")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    search_query = st.text_input("Search", placeholder="Report number, customer...")

with filter_col2:
    status_filter = st.multiselect(
        "Status",
        options=["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"],
        default=["COMPLETED"]
    )

with filter_col3:
    standard_filter = st.multiselect(
        "IEC Standard",
        options=["IEC 61215", "IEC 61730", "IEC 61701"]
    )

with filter_col4:
    result_filter = st.multiselect(
        "Result",
        options=["PASS", "FAIL", "CONDITIONAL", "NOT_TESTED"]
    )

# Date range
date_col1, date_col2 = st.columns(2)

with date_col1:
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=30)
    )

with date_col2:
    end_date = st.date_input(
        "End Date",
        value=datetime.now()
    )

if st.button("🔍 Search", type="primary"):
    st.info("Searching test records...")

st.markdown("---")

# Fetch and display test reports
st.markdown("### 📋 Test Reports")

try:
    response = requests.get(f"{API_BASE_URL}/iec-tests/reports")

    if response.status_code == 200:
        reports = response.json()

        if reports:
            # Create DataFrame
            df_data = []
            for report in reports:
                df_data.append({
                    "ID": report["id"],
                    "Report Number": report["report_number"],
                    "Customer": report["customer_name"],
                    "Module Model": report["module_model"],
                    "Standard": report["iec_standard"],
                    "Test Type": report["test_type"],
                    "Status": report["status"],
                    "Result": report["overall_result"],
                    "Date": report["report_date"][:10] if report["report_date"] else "N/A"
                })

            df = pd.DataFrame(df_data)

            # Display summary metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("Total Reports", len(df))

            with metric_col2:
                passed = len(df[df["Result"] == "PASS"])
                st.metric("Passed", passed, delta=f"{passed/len(df)*100:.1f}%" if len(df) > 0 else "0%")

            with metric_col3:
                failed = len(df[df["Result"] == "FAIL"])
                st.metric("Failed", failed)

            with metric_col4:
                completed = len(df[df["Status"] == "COMPLETED"])
                st.metric("Completed", completed)

            st.markdown("---")

            # Display table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Result": st.column_config.TextColumn(
                        "Result",
                        help="Test result"
                    )
                }
            )

            # Export options
            st.markdown("---")
            st.markdown("### 📤 Export Data")

            export_col1, export_col2, export_col3 = st.columns(3)

            with export_col1:
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"test_reports_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with export_col2:
                if st.button("📊 Export to Excel", use_container_width=True):
                    st.info("Excel export functionality")

            with export_col3:
                if st.button("📄 Generate Summary Report", use_container_width=True):
                    st.info("Summary report generation")

        else:
            st.info("No test reports found")

    else:
        st.error("Failed to fetch test reports")

except Exception as e:
    st.error(f"Error: {str(e)}")

st.markdown("---")

# Statistics and analytics
st.markdown("### 📊 Analytics & Statistics")

analytics_col1, analytics_col2 = st.columns(2)

with analytics_col1:
    st.markdown("#### Tests by Standard")
    st.info("Chart: Distribution of tests by IEC standard")

    # Placeholder for chart
    if 'df' in locals() and not df.empty:
        standard_counts = df['Standard'].value_counts()
        st.bar_chart(standard_counts)

with analytics_col2:
    st.markdown("#### Pass/Fail Rate")
    st.info("Chart: Overall pass/fail statistics")

    # Placeholder for chart
    if 'df' in locals() and not df.empty:
        result_counts = df['Result'].value_counts()
        st.bar_chart(result_counts)

st.markdown("---")

# Recent activity
st.markdown("### 🕒 Recent Activity")

st.markdown("""
Track recent test activities and updates:
- New test reports created
- Reports completed
- Certificates issued
- Failed tests requiring attention
""")

# Activity timeline (mock data)
activities = [
    {"time": "2 hours ago", "activity": "Certificate issued for RPT-20241109-001", "type": "success"},
    {"time": "5 hours ago", "activity": "Test report RPT-20241109-002 completed", "type": "info"},
    {"time": "1 day ago", "activity": "New test RPT-20241108-005 created", "type": "info"},
    {"time": "2 days ago", "activity": "Test RPT-20241107-003 failed - requires review", "type": "warning"},
]

for activity in activities:
    if activity["type"] == "success":
        st.success(f"✅ {activity['time']}: {activity['activity']}")
    elif activity["type"] == "warning":
        st.warning(f"⚠️ {activity['time']}: {activity['activity']}")
    else:
        st.info(f"ℹ️ {activity['time']}: {activity['activity']}")
