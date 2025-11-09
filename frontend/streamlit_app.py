"""
LIMS-QMS Platform - Streamlit Frontend
"""
import streamlit as st
import requests
from datetime import datetime
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
API_PREFIX = "/api/v1"


def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)


def login(username: str, password: str):
    """Login to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}


def register(username: str, email: str, password: str, full_name: str):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": "user"
            }
        )
        if response.status_code == 201:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        return False, {"detail": str(e)}


def get_current_user(token: str):
    """Get current user information"""
    try:
        response = requests.get(
            f"{API_BASE_URL}{API_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="LIMS-QMS Platform",
        page_icon="🔬",
        layout="wide"
    )

    # Initialize session state
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user" not in st.session_state:
        st.session_state.user = None

    # Sidebar
    with st.sidebar:
        st.title("🔬 LIMS-QMS")
        st.markdown("---")

        # API Health Check
        is_healthy, health_data = check_api_health()
        if is_healthy:
            st.success("✅ API Connected")
            with st.expander("API Health Details"):
                st.json(health_data)
        else:
            st.error("❌ API Disconnected")
            st.warning(f"Unable to connect to API at {API_BASE_URL}")

        st.markdown("---")

        # User status
        if st.session_state.user:
            st.success(f"👤 {st.session_state.user.get('full_name', 'User')}")
            st.caption(f"Role: {st.session_state.user.get('role', 'N/A')}")
            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()

    # Main content
    if not st.session_state.token:
        # Login/Register page
        st.title("Welcome to LIMS-QMS Platform")
        st.markdown("### Laboratory Information Management System & Quality Management System")

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    if not username or not password:
                        st.error("Please provide both username and password")
                    else:
                        success, result = login(username, password)
                        if success:
                            st.session_state.token = result["access_token"]
                            # Get user info
                            success, user_data = get_current_user(st.session_state.token)
                            if success:
                                st.session_state.user = user_data
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to fetch user information")
                        else:
                            st.error(f"Login failed: {result.get('detail', 'Unknown error')}")

            st.info("💡 Default admin credentials: username=`admin`, password=`admin123`")

        with tab2:
            st.subheader("Register New Account")
            with st.form("register_form"):
                reg_username = st.text_input("Username", key="reg_username")
                reg_email = st.text_input("Email", key="reg_email")
                reg_full_name = st.text_input("Full Name", key="reg_full_name")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")
                submit_reg = st.form_submit_button("Register")

                if submit_reg:
                    if not all([reg_username, reg_email, reg_full_name, reg_password]):
                        st.error("Please fill in all fields")
                    elif reg_password != reg_password2:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 8:
                        st.error("Password must be at least 8 characters long")
                    else:
                        success, result = register(reg_username, reg_email, reg_password, reg_full_name)
                        if success:
                            st.success("Registration successful! Please login.")
                        else:
                            st.error(f"Registration failed: {result.get('detail', 'Unknown error')}")

    else:
        # Dashboard (logged in)
        st.title("LIMS-QMS Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("User", st.session_state.user.get('username', 'N/A'))
        with col2:
            st.metric("Role", st.session_state.user.get('role', 'N/A'))
        with col3:
            st.metric("Status", "Active" if st.session_state.user.get('is_active') else "Inactive")

        st.markdown("---")

        st.info("🚧 Dashboard features will be implemented in future sessions")

        # Display user information
        with st.expander("User Information"):
            st.json(st.session_state.user)


if __name__ == "__main__":
    main()
