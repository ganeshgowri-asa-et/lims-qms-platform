"""Initialize database with sample data."""
import sys
sys.path.append('../backend')

from app.core.database import engine, Base, SessionLocal
from app.models.documents import QMSDocument, DocumentRevision, DocumentStatus, DocumentType
from app.models.equipment import EquipmentMaster, EquipmentStatus, CalibrationStatus
from datetime import datetime, timedelta


def init_database():
    """Initialize database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def create_sample_data():
    """Create sample data for testing."""
    db = SessionLocal()

    try:
        print("\nCreating sample documents...")

        # Sample documents
        sample_docs = [
            {
                "doc_number": "QSF-2025-001",
                "title": "Quality Management System Manual",
                "type": DocumentType.MANUAL,
                "owner": "Quality Manager",
                "department": "Quality Assurance",
                "created_by": "John Doe",
                "description": "Master quality management system manual",
                "status": DocumentStatus.APPROVED,
                "current_revision": "2.0",
                "current_major_version": 2,
                "current_minor_version": 0,
            },
            {
                "doc_number": "QSF-2025-002",
                "title": "Calibration Procedure",
                "type": DocumentType.PROCEDURE,
                "owner": "Calibration Manager",
                "department": "Calibration Lab",
                "created_by": "Jane Smith",
                "description": "Standard operating procedure for equipment calibration",
                "status": DocumentStatus.APPROVED,
                "current_revision": "1.0",
                "current_major_version": 1,
                "current_minor_version": 0,
            },
            {
                "doc_number": "QSF-2025-003",
                "title": "Document Control Form",
                "type": DocumentType.FORM,
                "owner": "QA Coordinator",
                "department": "Quality Assurance",
                "created_by": "Alice Johnson",
                "description": "Form for document control and tracking",
                "status": DocumentStatus.DRAFT,
                "current_revision": "1.0",
                "current_major_version": 1,
                "current_minor_version": 0,
            },
        ]

        for doc_data in sample_docs:
            doc = QMSDocument(**doc_data)
            db.add(doc)

        db.commit()
        print(f"✅ Created {len(sample_docs)} sample documents")

        print("\nCreating sample equipment...")

        # Sample equipment
        sample_equipment = [
            {
                "equipment_id": "EQP-2025-0001",
                "name": "UV-Vis Spectrophotometer",
                "manufacturer": "Shimadzu",
                "model_number": "UV-2600",
                "serial_number": "A12345678",
                "category": "Analytical Instruments",
                "equipment_type": "Spectrophotometer",
                "location": "Lab Room 101",
                "department": "R&D",
                "responsible_person": "Dr. Smith",
                "status": EquipmentStatus.OPERATIONAL,
                "requires_calibration": True,
                "calibration_frequency_days": 365,
                "next_calibration_date": datetime.now() + timedelta(days=45),
                "calibration_status": CalibrationStatus.DUE,
                "maintenance_frequency_days": 180,
                "next_maintenance_date": datetime.now() + timedelta(days=90),
                "oee_percentage": 95.5,
            },
            {
                "equipment_id": "EQP-2025-0002",
                "name": "Solar Simulator",
                "manufacturer": "Newport",
                "model_number": "Class AAA",
                "serial_number": "SS987654",
                "category": "Testing Equipment",
                "equipment_type": "Solar Simulator",
                "location": "Testing Lab",
                "department": "Testing",
                "responsible_person": "John Davis",
                "status": EquipmentStatus.OPERATIONAL,
                "requires_calibration": True,
                "calibration_frequency_days": 180,
                "next_calibration_date": datetime.now() + timedelta(days=5),
                "calibration_status": CalibrationStatus.DUE,
                "maintenance_frequency_days": 90,
                "next_maintenance_date": datetime.now() + timedelta(days=30),
                "oee_percentage": 92.3,
            },
            {
                "equipment_id": "EQP-2025-0003",
                "name": "Environmental Chamber",
                "manufacturer": "Espec",
                "model_number": "SH-641",
                "serial_number": "EC456789",
                "category": "Environmental Testing",
                "equipment_type": "Climate Chamber",
                "location": "Environmental Lab",
                "department": "Reliability Testing",
                "responsible_person": "Sarah Wilson",
                "status": EquipmentStatus.OPERATIONAL,
                "requires_calibration": True,
                "calibration_frequency_days": 365,
                "next_calibration_date": datetime.now() + timedelta(days=120),
                "calibration_status": CalibrationStatus.DUE,
                "maintenance_frequency_days": 180,
                "next_maintenance_date": datetime.now() + timedelta(days=60),
                "oee_percentage": 88.7,
            },
        ]

        for eq_data in sample_equipment:
            equipment = EquipmentMaster(**eq_data)
            db.add(equipment)

        db.commit()
        print(f"✅ Created {len(sample_equipment)} sample equipment records")

        print("\n✅ Sample data creation completed successfully!")

    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=== LIMS & QMS Platform - Database Initialization ===\n")

    init_database()
    create_sample_data()

    print("\n=== Initialization Complete ===")
    print("\nNext steps:")
    print("1. Start the backend API: cd backend && python run.py")
    print("2. Start the frontend UI: cd frontend && streamlit run app.py")
    print("3. Access the API docs: http://localhost:8000/docs")
    print("4. Access the UI: http://localhost:8501")
