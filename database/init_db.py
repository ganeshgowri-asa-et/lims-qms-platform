"""
Database initialization script
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import Base, engine, init_db
from backend.core.security import get_password_hash
from backend.models import *
from sqlalchemy.orm import Session


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def seed_permissions(db: Session):
    """Seed comprehensive permissions for all modules"""
    print("\n📋 Seeding permissions...")

    # Define all resources and actions
    resources = [
        # Core System
        'user', 'role', 'permission', 'session', 'api_key',
        # Documents & Forms
        'document', 'form', 'form_template', 'form_record',
        # Projects & Tasks
        'project', 'task', 'milestone',
        # HR Module
        'employee', 'recruitment', 'training', 'leave', 'attendance', 'performance',
        # Procurement
        'vendor', 'rfq', 'purchase_order', 'equipment', 'calibration',
        # Financial
        'expense', 'invoice', 'payment', 'revenue',
        # CRM
        'lead', 'customer', 'order', 'support_ticket',
        # Quality
        'non_conformance', 'audit', 'capa', 'risk_assessment',
        # Analytics & Reports
        'report', 'analytics', 'kpi', 'dashboard',
        # Workflow
        'workflow', 'approval',
        # Competency
        'competency', 'certification',
        # Delegation
        'delegation',
    ]

    actions = ['create', 'read', 'update', 'delete', 'approve', 'review', 'export']

    permissions_created = 0
    for resource in resources:
        for action in actions:
            # Skip inappropriate combinations
            if action == 'approve' and resource not in ['document', 'purchase_order', 'expense', 'invoice', 'capa', 'leave', 'delegation']:
                continue
            if action == 'review' and resource not in ['document', 'non_conformance', 'audit', 'capa']:
                continue

            perm_name = f"{resource}:{action}"
            existing = db.query(Permission).filter(Permission.name == perm_name).first()

            if not existing:
                # Determine scope based on resource
                scope = 'all'
                if resource in ['task', 'document', 'form_record', 'expense']:
                    scope = 'own'  # Users can only access their own by default

                permission = Permission(
                    name=perm_name,
                    resource=resource,
                    action=action,
                    scope=scope,
                    description=f"Permission to {action} {resource}"
                )
                db.add(permission)
                permissions_created += 1

    db.commit()
    print(f"✅ Created {permissions_created} permissions")


def seed_roles_with_permissions(db: Session):
    """Seed predefined roles with appropriate permissions"""
    print("\n👥 Seeding roles and assigning permissions...")

    # Define roles with hierarchy
    roles_data = [
        {
            "name": "Admin",
            "code": "admin",
            "description": "Full system access",
            "level": 0,
            "is_system_role": True,
            "permissions": "*:*"  # All permissions
        },
        {
            "name": "Quality Manager",
            "code": "quality_manager",
            "description": "QMS oversight and quality management",
            "level": 1,
            "is_system_role": True,
            "permissions": [
                "document:*", "audit:*", "non_conformance:*", "capa:*",
                "risk_assessment:*", "report:*", "analytics:*"
            ]
        },
        {
            "name": "Lab Manager",
            "code": "lab_manager",
            "description": "Laboratory operations management",
            "level": 1,
            "is_system_role": True,
            "permissions": [
                "project:*", "task:*", "equipment:*", "calibration:*",
                "form:*", "employee:read", "training:*", "competency:*"
            ]
        },
        {
            "name": "Technician",
            "code": "technician",
            "description": "Test execution and data entry",
            "level": 2,
            "is_system_role": True,
            "permissions": [
                "form_record:create", "form_record:read", "form_record:update",
                "task:read", "task:update", "equipment:read",
                "document:read", "competency:read"
            ]
        },
        {
            "name": "Checker",
            "code": "checker",
            "description": "Review submissions and data verification",
            "level": 2,
            "is_system_role": True,
            "permissions": [
                "document:review", "form_record:review", "non_conformance:review",
                "task:read", "project:read", "report:read"
            ]
        },
        {
            "name": "Approver",
            "code": "approver",
            "description": "Final approvals and sign-offs",
            "level": 1,
            "is_system_role": True,
            "permissions": [
                "document:approve", "purchase_order:approve", "expense:approve",
                "invoice:approve", "capa:approve", "leave:approve",
                "delegation:approve"
            ]
        },
        {
            "name": "Auditor",
            "code": "auditor",
            "description": "Read-only audit access",
            "level": 2,
            "is_system_role": True,
            "permissions": [
                "*:read", "*:export", "audit:create", "audit:update"
            ]
        },
        {
            "name": "Customer",
            "code": "customer",
            "description": "Limited external access",
            "level": 3,
            "is_system_role": True,
            "permissions": [
                "order:read", "order:create", "support_ticket:create",
                "support_ticket:read", "report:read"
            ]
        },
        {
            "name": "HR Manager",
            "code": "hr_manager",
            "description": "Human resources management",
            "level": 1,
            "is_system_role": True,
            "permissions": [
                "employee:*", "recruitment:*", "training:*", "leave:*",
                "attendance:*", "performance:*", "competency:*"
            ]
        },
        {
            "name": "Finance Manager",
            "code": "finance_manager",
            "description": "Financial management and reporting",
            "level": 1,
            "is_system_role": True,
            "permissions": [
                "expense:*", "invoice:*", "payment:*", "revenue:*",
                "purchase_order:approve", "report:*"
            ]
        }
    ]

    roles_created = 0
    for role_data in roles_data:
        permissions_list = role_data.pop("permissions")

        existing_role = db.query(Role).filter(Role.code == role_data["code"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            db.flush()  # Get the role ID
            roles_created += 1

            # Assign permissions
            if permissions_list == "*:*":
                # Admin gets all permissions
                all_permissions = db.query(Permission).all()
                role.permissions = all_permissions
            else:
                # Assign specific permissions
                for perm_pattern in permissions_list:
                    if '*' in perm_pattern:
                        # Wildcard permission
                        resource, action = perm_pattern.split(':')
                        if resource == '*':
                            # All resources with specific action
                            perms = db.query(Permission).filter(
                                Permission.action == action
                            ).all()
                        elif action == '*':
                            # All actions on specific resource
                            perms = db.query(Permission).filter(
                                Permission.resource == resource
                            ).all()
                        role.permissions.extend(perms)
                    else:
                        # Exact permission
                        perm = db.query(Permission).filter(
                            Permission.name == perm_pattern
                        ).first()
                        if perm and perm not in role.permissions:
                            role.permissions.append(perm)

            print(f"✅ Created role: {role.name} ({len(role.permissions)} permissions)")

    db.commit()
    if roles_created > 0:
        print(f"✅ Created {roles_created} roles")
    else:
        print("ℹ️  Roles already exist")


def seed_data():
    """Seed initial data"""
    print("Seeding initial data...")

    with Session(engine) as db:
        # Seed permissions first
        seed_permissions(db)

        # Seed roles with permissions
        seed_roles_with_permissions(db)

        # Create default admin user
        admin_user = db.query(User).filter(User.username == "admin").first()

        if not admin_user:
            from datetime import datetime
            admin_user = User(
                username="admin",
                email="admin@lims-qms.com",
                hashed_password=get_password_hash("Admin@123"),
                full_name="System Administrator",
                is_superuser=True,
                is_active=True,
                is_verified=True,
                email_verified=True,
                password_changed_at=datetime.utcnow(),
                date_joined=datetime.utcnow()
            )
            db.add(admin_user)
            db.flush()

            # Assign admin role
            admin_role = db.query(Role).filter(Role.code == "admin").first()
            if admin_role:
                admin_user.roles.append(admin_role)

            db.commit()
            print("\n✅ Created admin user (username: admin, password: Admin@123)")
            print("⚠️  IMPORTANT: Change this password immediately after first login!")

        # Create document levels
        levels_data = [
            {"level_number": 1, "level_name": "Level 1 - Quality Manual, Policy", "numbering_format": "L1-{year}-{seq:04d}"},
            {"level_number": 2, "level_name": "Level 2 - Quality System Procedures", "numbering_format": "L2-{year}-{seq:04d}"},
            {"level_number": 3, "level_name": "Level 3 - Operation & Test Procedures", "numbering_format": "L3-{year}-{seq:04d}"},
            {"level_number": 4, "level_name": "Level 4 - Templates, Formats", "numbering_format": "L4-{year}-{seq:04d}"},
            {"level_number": 5, "level_name": "Level 5 - Records", "numbering_format": "L5-{year}-{seq:04d}"}
        ]

        for level_data in levels_data:
            existing_level = db.query(DocumentLevel).filter(
                DocumentLevel.level_number == level_data["level_number"]
            ).first()
            if not existing_level:
                level = DocumentLevel(**level_data)
                db.add(level)
                print(f"✅ Created document level: {level_data['level_name']}")

        db.commit()
        print("✅ Initial data seeded successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("LIMS-QMS Platform - Database Initialization")
    print("=" * 60)

    create_tables()
    seed_data()

    print("\n" + "=" * 60)
    print("✅ Database initialization completed successfully!")
    print("=" * 60)
    print("\n🔐 Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: Admin@123")
    print("\n📋 Predefined Roles:")
    print("  • Admin - Full system access")
    print("  • Quality Manager - QMS oversight")
    print("  • Lab Manager - Lab operations")
    print("  • Technician - Test execution")
    print("  • Checker - Review & verification")
    print("  • Approver - Final approvals")
    print("  • Auditor - Read-only audit access")
    print("  • Customer - Limited external access")
    print("  • HR Manager - Human resources")
    print("  • Finance Manager - Financial management")
    print("\n⚠️  SECURITY NOTICE:")
    print("  1. Change the admin password immediately after first login")
    print("  2. Configure ENCRYPTION_KEY in environment variables")
    print("  3. Set up Redis for session management")
    print("  4. Review and adjust password policies as needed")
    print("=" * 60)
