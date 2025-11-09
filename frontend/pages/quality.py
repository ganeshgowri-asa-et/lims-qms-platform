"""
Quality Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show quality page"""
    st.header("✅ Quality Management")

    tab1, tab2, tab3, tab4 = st.tabs(["🚫 Non-Conformances", "✅ CAPA", "📋 Audits", "⚠️ Risk Assessment"])

    with tab1:
        st.subheader("Non-Conformance Management")

        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total NCs", "45")
        with col2:
            st.metric("Open", "3", "-1")
        with col3:
            st.metric("This Month", "2")
        with col4:
            st.metric("Closure Rate", "95%", "+2%")

        st.divider()

        # NC List
        ncs = pd.DataFrame({
            'NC Number': ['NC-2024-0008', 'NC-2024-0009', 'NC-2024-0010'],
            'Title': ['Calibration overdue', 'Document missing signature', 'Equipment malfunction'],
            'Category': ['Process', 'Documentation', 'Equipment'],
            'Severity': ['Medium', 'Low', 'High'],
            'Status': ['Open', 'Investigating', 'Closed'],
            'Detected Date': ['2024-03-05', '2024-03-07', '2024-03-01'],
            'Target Closure': ['2024-03-20', '2024-03-15', '2024-03-10']
        })

        st.dataframe(ncs, use_container_width=True)

        if st.button("➕ Report NC"):
            st.info("NC reporting form will open here")

    with tab2:
        st.subheader("CAPA Management")

        capas = pd.DataFrame({
            'CAPA Number': ['CAPA-2024-0015', 'CAPA-2024-0016', 'CAPA-2024-0017'],
            'Title': ['Improve calibration process', 'Update training procedure', 'Equipment upgrade'],
            'Type': ['Corrective', 'Preventive', 'Corrective'],
            'Status': ['In Progress', 'Implemented', 'Open'],
            'Target Date': ['2024-04-15', '2024-03-31', '2024-05-30'],
            'Owner': ['John Doe', 'Jane Smith', 'Bob Johnson']
        })

        st.dataframe(capas, use_container_width=True)

        if st.button("➕ Create CAPA"):
            st.info("CAPA creation form will open here")

    with tab3:
        st.subheader("Audit Management")

        audits = pd.DataFrame({
            'Audit Number': ['AUD-2024-0005', 'AUD-2024-0006', 'AUD-2024-0007'],
            'Title': ['Internal Audit Q1 2024', 'ISO 17025 Surveillance', 'Process Audit - Testing'],
            'Type': ['Internal', 'External', 'Internal'],
            'Date': ['2024-03-15', '2024-04-20', '2024-03-25'],
            'Status': ['Planned', 'Planned', 'Completed'],
            'Lead Auditor': ['Alice Williams', 'External Auditor', 'Bob Johnson']
        })

        st.dataframe(audits, use_container_width=True)

        if st.button("➕ Schedule Audit"):
            st.info("Audit scheduling form will open here")

    with tab4:
        st.subheader("Risk Assessment")

        risks = pd.DataFrame({
            'Risk Number': ['RISK-2024-0012', 'RISK-2024-0013', 'RISK-2024-0014'],
            'Title': ['Equipment failure during testing', 'Staff turnover', 'Power outage'],
            'Category': ['Operational', 'HR', 'Operational'],
            'Likelihood': ['Medium', 'Low', 'High'],
            'Impact': ['High', 'Medium', 'Medium'],
            'Risk Level': ['High', 'Low', 'High'],
            'Status': ['Active', 'Mitigated', 'Active']
        })

        st.dataframe(risks, use_container_width=True)

        # Risk matrix
        st.subheader("Risk Matrix")
        import plotly.graph_objects as go

        fig = go.Figure(data=go.Heatmap(
            z=[[1, 2, 3, 4, 5],
               [2, 4, 6, 8, 10],
               [3, 6, 9, 12, 15],
               [4, 8, 12, 16, 20],
               [5, 10, 15, 20, 25]],
            x=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            y=['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            colorscale='RdYlGn_r'
        ))
        fig.update_layout(title='Risk Matrix (Likelihood vs Impact)', xaxis_title='Impact', yaxis_title='Likelihood')
        st.plotly_chart(fig, use_container_width=True)
