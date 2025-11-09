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


def seed_data():
    """Seed initial data"""
    print("Seeding initial data...")

    with Session(engine) as db:
        # Create default admin user
        admin_user = db.query(User).filter(User.username == "admin").first()

        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@lims-qms.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_superuser=True,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            print("✅ Created admin user (username: admin, password: admin123)")

        # Create default roles
        roles_data = [
            {"name": "Administrator", "code": "admin", "description": "Full system access"},
            {"name": "Manager", "code": "manager", "description": "Management level access"},
            {"name": "Engineer", "code": "engineer", "description": "Technical staff access"},
            {"name": "Technician", "code": "technician", "description": "Laboratory technician access"},
            {"name": "Viewer", "code": "viewer", "description": "Read-only access"}
        ]

        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.code == role_data["code"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                print(f"✅ Created role: {role_data['name']}")

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

        # Create sample KPI definitions
        kpi_definitions_data = [
            {
                "kpi_code": "KPI-DOC-001",
                "name": "Document Approval Time",
                "description": "Average time to approve documents",
                "category": "Quality",
                "unit_of_measure": "days",
                "target_value": 5.0,
                "frequency": "Monthly",
                "is_higher_better": False
            },
            {
                "kpi_code": "KPI-TASK-001",
                "name": "Task Completion Rate",
                "description": "Percentage of tasks completed on time",
                "category": "Productivity",
                "unit_of_measure": "%",
                "target_value": 90.0,
                "frequency": "Monthly",
                "is_higher_better": True
            },
            {
                "kpi_code": "KPI-NC-001",
                "name": "Nonconformance Closure Rate",
                "description": "Percentage of NCs closed within target date",
                "category": "Quality",
                "unit_of_measure": "%",
                "target_value": 95.0,
                "frequency": "Monthly",
                "is_higher_better": True
            },
            {
                "kpi_code": "KPI-EQ-001",
                "name": "Equipment Utilization",
                "description": "Percentage of equipment actively used",
                "category": "Productivity",
                "unit_of_measure": "%",
                "target_value": 85.0,
                "frequency": "Monthly",
                "is_higher_better": True
            },
            {
                "kpi_code": "KPI-CUST-001",
                "name": "Customer Satisfaction Score",
                "description": "Average customer satisfaction rating",
                "category": "Customer Satisfaction",
                "unit_of_measure": "score",
                "target_value": 4.5,
                "frequency": "Quarterly",
                "is_higher_better": True
            }
        ]

        for kpi_data in kpi_definitions_data:
            existing_kpi = db.query(KPIDefinition).filter(KPIDefinition.kpi_code == kpi_data["kpi_code"]).first()
            if not existing_kpi:
                kpi = KPIDefinition(**kpi_data, owner_id=admin_user.id, show_on_dashboard=True)
                db.add(kpi)
                print(f"✅ Created KPI: {kpi_data['name']}")

        # Create sample quality objectives
        quality_objectives_data = [
            {
                "objective_number": "QO-2025-001",
                "title": "Reduce Document Approval Time",
                "description": "Reduce average document approval time from 7 days to 5 days",
                "category": "Process Improvement",
                "measurable_target": "Average approval time <= 5 days",
                "is_organizational": True
            },
            {
                "objective_number": "QO-2025-002",
                "title": "Improve NC Closure Rate",
                "description": "Achieve 95% NC closure rate within target dates",
                "category": "Quality",
                "measurable_target": "NC closure rate >= 95%",
                "is_organizational": True
            },
            {
                "objective_number": "QO-2025-003",
                "title": "Increase Customer Satisfaction",
                "description": "Maintain customer satisfaction score above 4.5/5.0",
                "category": "Customer Satisfaction",
                "measurable_target": "Customer satisfaction >= 4.5",
                "is_organizational": True
            }
        ]

        for obj_data in quality_objectives_data:
            existing_obj = db.query(QualityObjective).filter(
                QualityObjective.objective_number == obj_data["objective_number"]
            ).first()
            if not existing_obj:
                from datetime import date, timedelta
                obj = QualityObjective(
                    **obj_data,
                    owner_id=admin_user.id,
                    start_date=date.today(),
                    target_date=date.today() + timedelta(days=365),
                    status='active'
                )
                db.add(obj)
                print(f"✅ Created quality objective: {obj_data['title']}")

        db.commit()
        print("✅ Initial data seeded successfully!")
        print("✅ Analytics KPIs and objectives created!")


if __name__ == "__main__":
    print("=" * 50)
    print("LIMS-QMS Platform - Database Initialization")
    print("=" * 50)

    create_tables()
    seed_data()

    print("\n" + "=" * 50)
    print("✅ Database initialization completed!")
    print("=" * 50)
    print("\nDefault admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n⚠️  Please change the admin password after first login!")
