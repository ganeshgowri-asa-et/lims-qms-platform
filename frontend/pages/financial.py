"""
Financial Management page
"""
import streamlit as st
import pandas as pd


def show():
    """Show financial page"""
    st.header("💰 Financial Management")

    tab1, tab2, tab3, tab4 = st.tabs(["💵 Expenses", "📄 Invoices", "💳 Payments", "📊 Reports"])

    with tab1:
        st.subheader("Expense Management")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ➕ Add Expense")

            with st.form("add_expense"):
                expense_date = st.date_input("Date")
                category = st.selectbox("Category", ["Travel", "Food", "Supplies", "Equipment", "Training", "Other"])
                amount = st.number_input("Amount ($)", min_value=0.0, value=0.0)
                description = st.text_area("Description")
                receipt = st.file_uploader("Upload Receipt", type=['pdf', 'jpg', 'png'])

                submit = st.form_submit_button("Submit Expense")

                if submit:
                    st.success("✅ Expense submitted for approval")

        with col2:
            st.markdown("### 📊 My Expenses")

            expenses = pd.DataFrame({
                'Date': ['2024-03-01', '2024-02-28', '2024-02-25'],
                'Category': ['Travel', 'Supplies', 'Food'],
                'Amount': ['$150', '$85', '$45'],
                'Status': ['Approved', 'Pending', 'Approved']
            })

            st.dataframe(expenses, use_container_width=True)

    with tab2:
        st.subheader("Invoice Management")

        invoices = pd.DataFrame({
            'Invoice Number': ['INV-2024-0045', 'INV-2024-0046', 'INV-2024-0047'],
            'Customer': ['Solar Corp', 'Power Systems Inc', 'Green Energy Ltd'],
            'Date': ['2024-03-01', '2024-03-05', '2024-03-08'],
            'Amount': ['$25,000', '$18,500', '$32,000'],
            'Status': ['Paid', 'Pending', 'Sent'],
            'Due Date': ['2024-03-31', '2024-04-05', '2024-04-08']
        })

        st.dataframe(invoices, use_container_width=True)

        if st.button("➕ Create Invoice"):
            st.info("Invoice creation form will open here")

    with tab3:
        st.subheader("Payment Tracking")

        payments = pd.DataFrame({
            'Payment ID': ['PAY-2024-0025', 'PAY-2024-0026', 'PAY-2024-0027'],
            'Invoice': ['INV-2024-0045', 'INV-2024-0043', 'INV-2024-0042'],
            'Customer': ['Solar Corp', 'Power Systems Inc', 'Green Energy Ltd'],
            'Amount': ['$25,000', '$15,000', '$28,000'],
            'Date': ['2024-03-15', '2024-03-10', '2024-03-05'],
            'Method': ['Bank Transfer', 'Cheque', 'Bank Transfer']
        })

        st.dataframe(payments, use_container_width=True)

    with tab4:
        st.subheader("Financial Reports")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Revenue (MTD)", "$125K", "+15%")
        with col2:
            st.metric("Expenses (MTD)", "$45K", "+5%")
        with col3:
            st.metric("Profit (MTD)", "$80K", "+20%")
        with col4:
            st.metric("Outstanding", "$35K", "-10%")

        import plotly.express as px

        # Revenue trend
        revenue_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar'],
            'Revenue': [95000, 108000, 125000],
            'Expenses': [38000, 42000, 45000]
        })

        fig = px.line(revenue_data, x='Month', y=['Revenue', 'Expenses'], title='Revenue vs Expenses')
        st.plotly_chart(fig, use_container_width=True)
