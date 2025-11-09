"""
CRM page
"""
import streamlit as st
import pandas as pd


def show():
    """Show CRM page"""
    st.header("👥 Customer Relationship Management")

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Leads", "🏢 Customers", "📦 Orders", "🎫 Support Tickets"])

    with tab1:
        st.subheader("Lead Management")

        col1, col2 = st.columns([2, 1])

        with col1:
            leads = pd.DataFrame({
                'Lead Number': ['LEAD-2024-0025', 'LEAD-2024-0026', 'LEAD-2024-0027'],
                'Company': ['ABC Solar', 'XYZ Energy', 'Green Power'],
                'Contact': ['John Smith', 'Jane Doe', 'Bob Wilson'],
                'Source': ['Website', 'Referral', 'Trade Show'],
                'Status': ['Qualified', 'New', 'Contacted'],
                'Value': ['$50K', '$35K', '$75K']
            })

            st.dataframe(leads, use_container_width=True)

        with col2:
            st.markdown("### 📊 Lead Status")
            status_data = pd.DataFrame({
                'Status': ['New', 'Contacted', 'Qualified', 'Won'],
                'Count': [5, 8, 12, 3]
            })
            st.dataframe(status_data)

        if st.button("➕ Add New Lead"):
            st.info("Lead creation form will open here")

    with tab2:
        st.subheader("Customer Directory")

        customers = pd.DataFrame({
            'Customer Code': ['CUST-2024-0015', 'CUST-2024-0016', 'CUST-2024-0017'],
            'Company Name': ['Solar Corp', 'Power Systems Inc', 'Green Energy Ltd'],
            'Contact Person': ['Michael Brown', 'Sarah Johnson', 'David Lee'],
            'Email': ['michael@solar.com', 'sarah@power.com', 'david@green.com'],
            'Phone': ['+1-555-0101', '+1-555-0102', '+1-555-0103'],
            'Total Orders': [15, 8, 22]
        })

        st.dataframe(customers, use_container_width=True)

        if st.button("➕ Add New Customer"):
            st.info("Customer creation form will open here")

    with tab3:
        st.subheader("Customer Orders")

        orders = pd.DataFrame({
            'Order Number': ['ORD-2024-0045', 'ORD-2024-0046', 'ORD-2024-0047'],
            'Customer': ['Solar Corp', 'Power Systems Inc', 'Green Energy Ltd'],
            'Order Date': ['2024-03-01', '2024-03-05', '2024-03-08'],
            'Amount': ['$25,000', '$18,500', '$32,000'],
            'Status': ['In Progress', 'Confirmed', 'Completed'],
            'Delivery Date': ['2024-04-15', '2024-04-20', '2024-03-25']
        })

        st.dataframe(orders, use_container_width=True)

    with tab4:
        st.subheader("Support Tickets")

        tickets = pd.DataFrame({
            'Ticket Number': ['TKT-2024-0125', 'TKT-2024-0126', 'TKT-2024-0127'],
            'Customer': ['Solar Corp', 'Power Systems Inc', 'Green Energy Ltd'],
            'Subject': ['Test report query', 'Invoice clarification', 'Sample collection'],
            'Priority': ['Medium', 'Low', 'High'],
            'Status': ['Open', 'Resolved', 'In Progress'],
            'Created': ['2024-03-08', '2024-03-07', '2024-03-09']
        })

        st.dataframe(tickets, use_container_width=True)

        if st.button("➕ Create Ticket"):
            st.info("Ticket creation form will open here")
