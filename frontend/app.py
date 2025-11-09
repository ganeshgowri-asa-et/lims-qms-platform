"""
Main Streamlit Application - LIMS-QMS Organization OS
"""
import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="LIMS-QMS Organization OS",
    page_icon="🏢",
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
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    return st.session_state.authenticated


def login_page():
    """Login page"""
    st.markdown("<h1 class='main-header'>🏢 LIMS-QMS Organization OS</h1>", unsafe_allow_html=True)
    st.markdown("### Complete Organization Operating System")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                # TODO: Implement actual authentication
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "username": username,
                        "full_name": "Demo User",
                        "role": "Admin"
                    }
                    st.rerun()
                else:
                    st.error("Please enter username and password")

        st.info("Demo Mode: Enter any username and password to login")


def main_app():
    """Main application after login"""

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 👤 " + st.session_state.user.get('full_name', 'User'))
        st.caption(f"Role: {st.session_state.user.get('role', 'User')}")
        st.divider()

        selected = option_menu(
            "Main Menu",
            [
                "Dashboard",
                "Documents",
                "Forms",
                "Projects",
                "Tasks",
                "HR",
                "Procurement",
                "Equipment",
                "Financial",
                "CRM",
                "Quality",
                "Analytics",
                "AI Assistant",
                "Settings"
            ],
            icons=[
                'speedometer2', 'file-earmark-text', 'clipboard-check',
                'diagram-3', 'list-task', 'people', 'cart',
                'tools', 'currency-dollar', 'person-lines-fill',
                'shield-check', 'bar-chart', 'robot', 'gear'
            ],
            menu_icon="cast",
            default_index=0,
        )

        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # Main content area
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Documents":
        show_documents()
    elif selected == "Forms":
        show_forms()
    elif selected == "Projects":
        show_projects()
    elif selected == "Tasks":
        show_tasks()
    elif selected == "HR":
        show_hr()
    elif selected == "Procurement":
        show_procurement()
    elif selected == "Equipment":
        show_equipment()
    elif selected == "Financial":
        show_financial()
    elif selected == "CRM":
        show_crm()
    elif selected == "Quality":
        show_quality()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "AI Assistant":
        show_ai_assistant()
    elif selected == "Settings":
        show_settings()


def show_dashboard():
    """Dashboard page"""
    st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Active Projects", value="12", delta="2")

    with col2:
        st.metric(label="Pending Tasks", value="45", delta="-5")

    with col3:
        st.metric(label="Documents", value="234", delta="15")

    with col4:
        st.metric(label="Open NCs", value="3", delta="-1")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Project Status")
        import plotly.express as px
        import pandas as pd

        data = pd.DataFrame({
            'Status': ['Planning', 'In Progress', 'Completed', 'On Hold'],
            'Count': [3, 7, 15, 2]
        })
        fig = px.pie(data, values='Count', names='Status', title='Projects by Status')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📋 Task Distribution")
        task_data = pd.DataFrame({
            'Priority': ['Low', 'Medium', 'High', 'Critical'],
            'Count': [15, 20, 8, 2]
        })
        fig = px.bar(task_data, x='Priority', y='Count', title='Tasks by Priority')
        st.plotly_chart(fig, use_container_width=True)

    # Recent activities
    st.subheader("🕐 Recent Activities")
    activities = [
        {"time": "2 mins ago", "activity": "Document DOC-2024-0015 approved"},
        {"time": "15 mins ago", "activity": "New task TASK-2024-0123 created"},
        {"time": "1 hour ago", "activity": "NC-2024-0005 closed"},
        {"time": "2 hours ago", "activity": "Equipment EQ-2024-0032 calibrated"},
    ]

    for act in activities:
        st.info(f"**{act['time']}**: {act['activity']}")


def show_documents():
    """Documents page"""
    from pages import documents
    documents.show()


def show_forms():
    """Forms page"""
    from pages import forms
    forms.show()


def show_projects():
    """Projects page"""
    from pages import projects
    projects.show()


def show_tasks():
    """Tasks page"""
    from pages import tasks
    tasks.show()


def show_hr():
    """HR page"""
    from pages import hr
    hr.show()


def show_procurement():
    """Procurement page"""
    from pages import procurement
    procurement.show()


def show_equipment():
    """Equipment page"""
    from pages import equipment
    equipment.show()


def show_financial():
    """Financial page"""
    from pages import financial
    financial.show()


def show_crm():
    """CRM page"""
    from pages import crm
    crm.show()


def show_quality():
    """Quality page"""
    from pages import quality
    quality.show()


def show_analytics():
    """Analytics page"""
    from pages import analytics
    analytics.show()


def show_ai_assistant():
    """AI Assistant page"""
    from pages import ai_assistant
    ai_assistant.show()


def show_settings():
    """Settings page"""
    st.header("⚙️ Settings")
    st.subheader("User Preferences")

    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Tamil", "Telugu", "Gujarati", "Marathi"]
    )

    theme = st.selectbox("Theme", ["Light", "Dark"])

    st.subheader("Notifications")
    st.checkbox("Email notifications", value=True)
    st.checkbox("Desktop notifications", value=True)

    if st.button("Save Settings"):
        st.success("Settings saved successfully!")


# Main app flow
if __name__ == "__main__":
    if check_authentication():
        main_app()
    else:
        login_page()
