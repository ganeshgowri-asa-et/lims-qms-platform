"""
Procurement page
"""
import streamlit as st
import pandas as pd


def show():
    """Show procurement page"""
    st.header("🛒 Procurement Management")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Purchase Orders", "💼 Vendors", "📝 RFQs", "📊 Statistics"])

    with tab1:
        st.subheader("Purchase Orders")

        pos = pd.DataFrame({
            'PO Number': ['PO-2024-0015', 'PO-2024-0016', 'PO-2024-0017'],
            'Vendor': ['Vendor A', 'Vendor B', 'Vendor C'],
            'Date': ['2024-03-01', '2024-03-05', '2024-03-08'],
            'Amount': ['$15,000', '$8,500', '$22,000'],
            'Status': ['Approved', 'Received', 'Sent'],
            'Delivery Date': ['2024-03-20', '2024-03-15', '2024-03-25']
        })

        st.dataframe(pos, use_container_width=True)

        if st.button("➕ Create Purchase Order"):
            st.info("Create PO form will open here")

    with tab2:
        st.subheader("Vendor Management")

        vendors = pd.DataFrame({
            'Vendor Code': ['VEN-001', 'VEN-002', 'VEN-003'],
            'Name': ['ABC Instruments', 'XYZ Calibration', 'Tech Solutions'],
            'Contact': ['John', 'Jane', 'Bob'],
            'Email': ['abc@vendor.com', 'xyz@vendor.com', 'tech@vendor.com'],
            'Rating': ['4.5/5', '4.8/5', '4.2/5'],
            'Status': ['Approved', 'Approved', 'Pending']
        })

        st.dataframe(vendors, use_container_width=True)

    with tab3:
        st.subheader("Request for Quotation (RFQ)")

        rfqs = pd.DataFrame({
            'RFQ Number': ['RFQ-2024-0012', 'RFQ-2024-0013'],
            'Title': ['Calibration Equipment', 'Lab Consumables'],
            'Vendor': ['Vendor A', 'Vendor B'],
            'Issue Date': ['2024-02-25', '2024-03-01'],
            'Due Date': ['2024-03-10', '2024-03-15'],
            'Status': ['Received', 'Sent']
        })

        st.dataframe(rfqs, use_container_width=True)

    with tab4:
        st.subheader("Procurement Statistics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total POs", "156")
        with col2:
            st.metric("This Month", "12", "+3")
        with col3:
            st.metric("Total Spend", "$450K")
        with col4:
            st.metric("Active Vendors", "25")
