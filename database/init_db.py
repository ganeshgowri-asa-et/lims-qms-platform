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

        db.commit()
        print("✅ Initial data seeded successfully!")


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
