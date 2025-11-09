"""
Administration & User Management page
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from frontend.utils.api_client import api_client


def show():
    """Show administration page"""
    st.header("⚙️ Administration")

    # Check if user is admin
    if not st.session_state.get('user', {}).get('role') in ['Admin', 'Manager']:
        st.warning("⚠️ This page requires Administrator or Manager privileges")
        return

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 User Management",
        "🔐 Roles & Permissions",
        "🔧 System Configuration",
        "📋 Template Management",
        "💾 Backup & Restore"
    ])

    with tab1:
        show_user_management()

    with tab2:
        show_roles_permissions()

    with tab3:
        show_system_config()

    with tab4:
        show_template_management()

    with tab5:
        show_backup_restore()


def show_user_management():
    """User management interface"""
    st.subheader("User Management")

    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        if st.button("➕ Add User"):
            st.session_state.show_add_user = True

    with col2:
        if st.button("📥 Import Users"):
            st.info("Upload CSV file with user data")

    with col3:
        if st.button("📤 Export Users"):
            st.success("Users exported successfully")

    # Add user form
    if st.session_state.get('show_add_user', False):
        with st.expander("➕ Add New User", expanded=True):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)

                with col1:
                    username = st.text_input("Username*")
                    email = st.text_input("Email*")
                    full_name = st.text_input("Full Name*")

                with col2:
                    role = st.selectbox(
                        "Role*",
                        ["User", "Checker", "Approver", "Manager", "Admin"]
                    )
                    department = st.selectbox(
                        "Department",
                        ["Quality", "Testing", "Calibration", "Engineering", "Management"]
                    )
                    is_active = st.checkbox("Active", value=True)

                password = st.text_input("Temporary Password*", type="password")
                send_email = st.checkbox("Send welcome email", value=True)

                col1, col2 = st.columns([1, 5])
                with col1:
                    submit = st.form_submit_button("Create User", type="primary")
                with col2:
                    cancel = st.form_submit_button("Cancel")

                if submit:
                    if username and email and full_name and password:
                        user_data = {
                            "username": username,
                            "email": email,
                            "full_name": full_name,
                            "role": role,
                            "department": department,
                            "is_active": is_active
                        }
                        result = api_client.create_user(user_data)
                        if result:
                            st.success(f"✅ User '{username}' created successfully!")
                            st.session_state.show_add_user = False
                            st.rerun()
                    else:
                        st.error("Please fill all required fields")

                if cancel:
                    st.session_state.show_add_user = False
                    st.rerun()

    # User list
    st.markdown("### User Directory")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All", "Admin", "Manager", "Approver", "Checker", "User"])
    with col2:
        dept_filter = st.selectbox("Filter by Department", ["All", "Quality", "Testing", "Calibration", "Engineering"])
    with col3:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])

    # Fetch users
    try:
        users = api_client.get_users()
    except:
        users = []

    # Mock data
    if not users:
        users_df = pd.DataFrame({
            'Username': ['alice.qa', 'bob.eng', 'jane.tech', 'mike.mgr', 'sarah.admin'],
            'Full Name': ['Alice QA', 'Bob Engineer', 'Jane Technician', 'Mike Manager', 'Sarah Admin'],
            'Email': [
                'alice.qa@company.com',
                'bob.engineer@company.com',
                'jane.tech@company.com',
                'mike.manager@company.com',
                'sarah.admin@company.com'
            ],
            'Role': ['Approver', 'Checker', 'User', 'Manager', 'Admin'],
            'Department': ['Quality', 'Engineering', 'Testing', 'Management', 'IT'],
            'Last Login': [
                '2024-03-11 14:30',
                '2024-03-11 10:15',
                '2024-03-11 09:45',
                '2024-03-10 16:20',
                '2024-03-11 08:30'
            ],
            'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active']
        })
    else:
        users_df = pd.DataFrame(users)

    st.dataframe(users_df, use_container_width=True, height=400)

    # User actions
    st.markdown("### User Actions")
    selected_user = st.selectbox("Select User", users_df['Username'].tolist() if not users_df.empty else [])

    if selected_user:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✏️ Edit User"):
                st.info(f"Editing user: {selected_user}")

        with col2:
            if st.button("🔒 Reset Password"):
                st.success("Password reset email sent")

        with col3:
            if st.button("🚫 Deactivate"):
                st.warning(f"User {selected_user} deactivated")

        with col4:
            if st.button("🗑️ Delete"):
                st.error("⚠️ Confirm deletion?")


def show_roles_permissions():
    """Roles and permissions management"""
    st.subheader("Roles & Permissions")

    # Role hierarchy
    st.markdown("### Role Hierarchy")

    roles_df = pd.DataFrame({
        'Role': ['Admin', 'Manager', 'Approver', 'Checker', 'User'],
        'Level': [5, 4, 3, 2, 1],
        'Users': [2, 5, 8, 12, 35],
        'Description': [
            'Full system access',
            'Department management',
            'Approve documents and forms',
            'Review and verify data',
            'Basic access'
        ]
    })

    st.dataframe(roles_df, use_container_width=True)

    # Permission matrix
    st.markdown("### Permission Matrix")

    permissions = pd.DataFrame({
        'Module': [
            'Documents',
            'Forms',
            'Projects',
            'Tasks',
            'Quality',
            'Analytics',
            'Administration',
            'AI Assistant'
        ],
        'Admin': ['✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ Full'],
        'Manager': ['✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ Full', '✅ View', '⚠️ Limited', '✅ Full'],
        'Approver': ['✅ Approve', '✅ Approve', '👁️ View', '✅ Edit', '✅ Approve', '👁️ View', '❌ None', '✅ Full'],
        'Checker': ['👁️ View', '✅ Review', '👁️ View', '✅ Edit', '✅ Review', '👁️ View', '❌ None', '✅ Full'],
        'User': ['👁️ View', '✅ Create', '👁️ View', '✅ Own', '👁️ View', '👁️ View', '❌ None', '✅ Basic']
    })

    st.dataframe(permissions, use_container_width=True)

    # Add/Edit role
    with st.expander("➕ Create Custom Role"):
        role_name = st.text_input("Role Name")
        role_description = st.text_area("Description")

        st.markdown("**Assign Permissions:**")

        modules = ['Documents', 'Forms', 'Projects', 'Tasks', 'Quality', 'Analytics', 'Administration']
        permission_levels = ['None', 'View', 'Create', 'Edit', 'Delete', 'Approve', 'Full']

        for module in modules:
            st.selectbox(f"{module}", permission_levels, key=f"perm_{module}")

        if st.button("Create Role"):
            st.success(f"✅ Role '{role_name}' created successfully!")


def show_system_config():
    """System configuration"""
    st.subheader("System Configuration")

    # General settings
    with st.expander("🔧 General Settings", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("Organization Name", value="LIMS-QMS Organization")
            st.text_input("System Administrator Email", value="admin@company.com")
            st.selectbox("Default Language", ["English", "Hindi", "Tamil", "Telugu"])

        with col2:
            st.selectbox("Timezone", ["Asia/Kolkata", "UTC", "Asia/Dubai"])
            st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
            st.selectbox("Theme", ["Light", "Dark", "Auto"])

    # Document settings
    with st.expander("📄 Document Settings"):
        st.checkbox("Enable document versioning", value=True)
        st.checkbox("Require approval for document publication", value=True)
        st.number_input("Document retention period (years)", min_value=1, max_value=50, value=7)
        st.number_input("Maximum file upload size (MB)", min_value=1, max_value=100, value=10)

        st.multiselect(
            "Allowed file types",
            ["PDF", "DOCX", "XLSX", "PNG", "JPG", "CSV"],
            default=["PDF", "DOCX", "XLSX"]
        )

    # Workflow settings
    with st.expander("⚡ Workflow Settings"):
        st.number_input("Default approval timeout (days)", min_value=1, max_value=30, value=7)
        st.checkbox("Send notification on task assignment", value=True)
        st.checkbox("Send notification on approval pending", value=True)
        st.checkbox("Auto-escalate overdue tasks", value=True)

    # Email settings
    with st.expander("📧 Email Configuration"):
        st.text_input("SMTP Server", value="smtp.gmail.com")
        st.number_input("SMTP Port", value=587)
        st.text_input("SMTP Username")
        st.text_input("SMTP Password", type="password")
        st.text_input("From Email", value="noreply@company.com")

        if st.button("Test Email Configuration"):
            st.success("✅ Test email sent successfully!")

    # Security settings
    with st.expander("🔐 Security Settings"):
        st.number_input("Password minimum length", min_value=6, max_value=20, value=8)
        st.checkbox("Require special characters in password", value=True)
        st.checkbox("Enable two-factor authentication", value=False)
        st.number_input("Session timeout (minutes)", min_value=15, max_value=480, value=60)
        st.number_input("Max login attempts", min_value=3, max_value=10, value=5)

    # Save configuration
    if st.button("💾 Save Configuration", type="primary"):
        st.success("✅ Configuration saved successfully!")


def show_template_management():
    """Template management"""
    st.subheader("Template Management")

    # Template library
    st.markdown("### Template Library")

    templates_df = pd.DataFrame({
        'Template Code': [
            'CAL-LOG',
            'TEST-REPORT',
            'NC-FORM',
            'EQ-CARD',
            'TRAINING-REC'
        ],
        'Template Name': [
            'Calibration Log',
            'Test Report',
            'Non-Conformance Report',
            'Equipment History Card',
            'Training Record'
        ],
        'Category': [
            'Calibration',
            'Testing',
            'Quality',
            'Equipment',
            'HR'
        ],
        'Version': ['2.0', '3.1', '1.5', '1.0', '2.2'],
        'Fields': [12, 25, 15, 18, 10],
        'Records': [145, 523, 28, 167, 89],
        'Status': [
            '✅ Active',
            '✅ Active',
            '✅ Active',
            '✅ Active',
            '✅ Active'
        ]
    })

    st.dataframe(templates_df, use_container_width=True)

    # Template actions
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("➕ New Template"):
            st.info("Create new template")

    with col2:
        if st.button("📥 Import Template"):
            st.info("Upload template file")

    with col3:
        if st.button("📤 Export Selected"):
            st.success("Template exported")

    with col4:
        if st.button("🗑️ Archive Old"):
            st.warning("Archive unused templates")


def show_backup_restore():
    """Backup and restore"""
    st.subheader("Backup & Restore")

    # Backup section
    st.markdown("### Create Backup")

    col1, col2 = st.columns(2)

    with col1:
        backup_type = st.selectbox(
            "Backup Type",
            ["Full System Backup", "Database Only", "Documents Only", "Configuration Only"]
        )

    with col2:
        include_files = st.checkbox("Include uploaded files", value=True)
        compress = st.checkbox("Compress backup", value=True)

    if st.button("🔄 Create Backup", type="primary"):
        with st.spinner("Creating backup..."):
            import time
            time.sleep(2)
            st.success(f"✅ Backup created: backup_20240311_143022.zip")

    # Backup history
    st.markdown("### Backup History")

    backups_df = pd.DataFrame({
        'Backup ID': [
            'backup_20240311_143022',
            'backup_20240310_200015',
            'backup_20240309_180030',
            'backup_20240308_143045'
        ],
        'Date': [
            '2024-03-11 14:30',
            '2024-03-10 20:00',
            '2024-03-09 18:00',
            '2024-03-08 14:30'
        ],
        'Type': [
            'Full System',
            'Database',
            'Full System',
            'Documents'
        ],
        'Size': ['2.4 GB', '850 MB', '2.3 GB', '1.5 GB'],
        'Status': [
            '✅ Success',
            '✅ Success',
            '✅ Success',
            '✅ Success'
        ]
    })

    st.dataframe(backups_df, use_container_width=True)

    # Restore section
    st.markdown("### Restore from Backup")

    st.warning("⚠️ Warning: Restoring from backup will overwrite current data")

    restore_backup = st.selectbox(
        "Select backup to restore",
        backups_df['Backup ID'].tolist()
    )

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("🔄 Restore"):
            st.error("⚠️ Please confirm restoration")

    with col2:
        if st.button("📥 Download"):
            st.success("Backup download started")

    # Automated backup settings
    st.markdown("### Automated Backup Settings")

    enable_auto = st.checkbox("Enable automated backups", value=True)

    if enable_auto:
        col1, col2 = st.columns(2)

        with col1:
            frequency = st.selectbox(
                "Backup Frequency",
                ["Daily", "Weekly", "Monthly"]
            )
            time = st.time_input("Backup Time", datetime.strptime("02:00", "%H:%M").time())

        with col2:
            retention = st.number_input("Retention (days)", min_value=7, max_value=365, value=30)
            max_backups = st.number_input("Max backups to keep", min_value=1, max_value=50, value=10)

        if st.button("💾 Save Backup Settings"):
            st.success("✅ Automated backup settings saved!")
