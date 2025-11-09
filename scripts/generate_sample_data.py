"""
Generate Sample Data for LIMS-QMS Platform
This script populates the database with realistic sample data for demonstration
"""
import sys
import os
from datetime import datetime, timedelta, date
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.models import (
    Customer, TestRequest, Sample, TestParameter,
    EquipmentMaster, CalibrationRecord,
    TrainingMaster, EmployeeTrainingMatrix, TrainingAttendance,
    NonConformance, RootCauseAnalysis, CAPAAction,
    AuditProgram, AuditSchedule, AuditFinding,
    RiskRegister, QMSDocument, CustomerPortalUser
)


def generate_customers(db):
    """Generate sample customers"""
    print("Generating customers...")

    customers = [
        Customer(
            customer_code="CUST-2024-001",
            name="Solar Tech Industries",
            contact_person="John Smith",
            email="john.smith@solartech.com",
            phone="+1-555-0101",
            address="123 Solar Street",
            city="San Francisco",
            state="CA",
            country="USA",
            postal_code="94102",
            customer_type="Manufacturer",
            credit_limit=100000.00,
            payment_terms="Net 30",
            is_active=True
        ),
        Customer(
            customer_code="CUST-2024-002",
            name="Green Energy Solutions",
            contact_person="Sarah Johnson",
            email="sarah.j@greenenergy.com",
            phone="+1-555-0102",
            address="456 Renewable Ave",
            city="Austin",
            state="TX",
            country="USA",
            postal_code="73301",
            customer_type="Trader",
            credit_limit=75000.00,
            payment_terms="Net 45",
            is_active=True
        ),
        Customer(
            customer_code="CUST-2024-003",
            name="Photovoltaic Innovations Ltd",
            contact_person="Michael Chen",
            email="m.chen@pvinnovations.com",
            phone="+1-555-0103",
            address="789 Innovation Blvd",
            city="Seattle",
            state="WA",
            country="USA",
            postal_code="98101",
            customer_type="Manufacturer",
            credit_limit=150000.00,
            payment_terms="Net 30",
            is_active=True
        )
    ]

    for customer in customers:
        db.add(customer)

    db.commit()
    print(f"Created {len(customers)} customers")


def generate_test_requests(db):
    """Generate sample test requests"""
    print("Generating test requests...")

    customers = db.query(Customer).all()
    test_types = ["IEC 61215", "IEC 61730", "IEC 61701", "IEC 62716"]
    statuses = ["Submitted", "In Progress", "Testing", "Completed", "Reported"]

    requests = []
    for i in range(1, 51):
        request_date = datetime.now().date() - timedelta(days=random.randint(1, 180))
        customer = random.choice(customers)

        request = TestRequest(
            request_number=f"TRQ-2025-{i:04d}",
            customer_id=customer.id,
            request_date=request_date,
            required_date=request_date + timedelta(days=random.randint(30, 90)),
            sample_description=f"Solar Panel Testing - {random.choice(['Monocrystalline', 'Polycrystalline', 'Thin Film'])}",
            test_type=random.choice(test_types),
            priority=random.choice(["Normal", "High", "Urgent"]),
            status=random.choice(statuses),
            assigned_to=f"Tech-{random.randint(1, 5)}",
            quote_amount=random.uniform(5000, 15000),
            quote_approved=random.choice([True, False]),
            created_by=customer.name
        )
        requests.append(request)
        db.add(request)

    db.commit()
    print(f"Created {len(requests)} test requests")


def generate_samples(db):
    """Generate sample records"""
    print("Generating samples...")

    test_requests = db.query(TestRequest).all()
    statuses = ["Received", "In Progress", "Testing", "Completed", "Reported"]

    samples = []
    sample_count = 1
    for request in test_requests[:30]:  # Create samples for first 30 requests
        num_samples = random.randint(1, 3)
        for i in range(num_samples):
            sample = Sample(
                sample_id=f"SMP-2025-{sample_count:04d}",
                test_request_id=request.id,
                sample_name=f"Solar Module {random.choice(['SM', 'SP', 'PV'])}-{random.randint(100, 500)}W",
                sample_type="Solar Panel",
                manufacturer=request.customer.name,
                model=f"Model-{random.randint(100, 999)}",
                serial_number=f"SN-2025-{sample_count:03d}",
                received_date=request.request_date,
                condition_on_receipt="Good condition, no visible damage",
                storage_location=f"Rack-{random.randint(1, 10)}-Shelf-{random.randint(1, 5)}",
                barcode=f"BC{sample_count:08d}",
                status=random.choice(statuses)
            )
            samples.append(sample)
            db.add(sample)
            sample_count += 1

    db.commit()
    print(f"Created {len(samples)} samples")


def generate_equipment(db):
    """Generate equipment records"""
    print("Generating equipment...")

    equipment_list = []
    categories = ["Testing Equipment", "Measurement Instrument", "Environmental Chamber", "Safety Equipment"]

    for i in range(1, 46):
        equip = EquipmentMaster(
            equipment_id=f"EQP-{i:04d}",
            name=f"Equipment {i}",
            manufacturer=random.choice(["Keysight", "Fluke", "Tektronix", "Rohde & Schwarz"]),
            model=f"Model-{random.randint(1000, 9999)}",
            serial_number=f"SN-EQP-{i:06d}",
            location=f"Lab-{random.randint(1, 5)}",
            category=random.choice(categories),
            calibration_frequency_days=random.choice([180, 365]),
            next_calibration_date=datetime.now().date() + timedelta(days=random.randint(-30, 180)),
            status="Active",
            purchase_date=datetime.now().date() - timedelta(days=random.randint(365, 1825)),
            purchase_cost=random.uniform(5000, 50000)
        )
        equipment_list.append(equip)
        db.add(equip)

    db.commit()
    print(f"Created {len(equipment_list)} equipment items")


def generate_non_conformances(db):
    """Generate non-conformance records"""
    print("Generating non-conformances...")

    categories = ["Quality", "Process", "Documentation", "Equipment", "Personnel"]
    severities = ["Critical", "Major", "Minor"]
    statuses = ["Open", "In Progress", "Closed"]

    ncs = []
    for i in range(1, 34):
        nc_date = datetime.now().date() - timedelta(days=random.randint(1, 365))

        nc = NonConformance(
            nc_number=f"NC-2025-{i:03d}",
            nc_date=nc_date,
            source=random.choice(["Internal Audit", "Customer Complaint", "Process Monitoring", "External Audit"]),
            category=random.choice(categories),
            description=f"Non-conformance related to {random.choice(categories)}",
            detected_by=f"Employee-{random.randint(1, 20)}",
            department=random.choice(["Quality", "Testing", "Engineering", "Admin"]),
            severity=random.choice(severities),
            status=random.choice(statuses),
            closure_date=nc_date + timedelta(days=random.randint(30, 90)) if random.choice([True, False]) else None
        )
        ncs.append(nc)
        db.add(nc)

    db.commit()
    print(f"Created {len(ncs)} non-conformances")


def generate_audit_program(db):
    """Generate audit program and schedule"""
    print("Generating audit program...")

    program = AuditProgram(
        program_id="AUD-PROG-2025",
        year=2025,
        program_name="Annual Audit Program 2025",
        scope="ISO 17025:2017 and ISO 9001:2015",
        objectives="Ensure compliance with ISO standards and continuous improvement",
        prepared_by="Quality Manager",
        approved_by="CEO",
        approval_date=date(2025, 1, 15),
        status="Active"
    )
    db.add(program)
    db.commit()

    # Generate audit schedule
    audit_areas = ["Document Control", "Equipment Calibration", "Testing Process",
                  "Personnel Competency", "Customer Service", "Management Review"]

    for i, area in enumerate(audit_areas, 1):
        schedule = AuditSchedule(
            program_id=program.id,
            audit_type=random.choice(["Internal", "External", "Surveillance"]),
            audit_area=area,
            planned_date=date(2025, 1 + i, 15),
            actual_date=date(2025, 1 + i, 15) if i <= 6 else None,
            lead_auditor=f"Auditor-{random.randint(1, 3)}",
            audit_team="Team members TBD",
            status="Completed" if i <= 6 else "Scheduled"
        )
        db.add(schedule)

    db.commit()
    print("Created audit program and schedule")


def generate_risk_register(db):
    """Generate risk register"""
    print("Generating risk register...")

    risks = [
        ("Equipment Failure", "Operational", "Testing Lab", 3, 4),
        ("Staff Competency Gap", "Personnel", "Training", 2, 3),
        ("Sample Contamination", "Quality", "Sample Handling", 2, 5),
        ("Data Integrity Issue", "Compliance", "Data Management", 1, 4),
        ("Customer Complaint", "Business", "Customer Service", 3, 3),
        ("Calibration Lapse", "Technical", "Equipment Management", 2, 4)
    ]

    for i, (desc, category, area, likelihood, impact) in enumerate(risks, 1):
        score = likelihood * impact
        if score >= 15:
            level = "Critical"
        elif score >= 10:
            level = "High"
        elif score >= 5:
            level = "Medium"
        else:
            level = "Low"

        risk = RiskRegister(
            risk_id=f"RISK-2025-{i:03d}",
            risk_category=category,
            risk_description=desc,
            process_area=area,
            likelihood=likelihood,
            impact=impact,
            risk_score=score,
            risk_level=level,
            mitigation_plan=f"Mitigation plan for {desc}",
            owner=f"Manager-{random.randint(1, 5)}",
            status="Active",
            review_date=datetime.now().date() + timedelta(days=90)
        )
        db.add(risk)

    db.commit()
    print(f"Created {len(risks)} risk items")


def main():
    """Main function to generate all sample data"""
    print("=" * 60)
    print("LIMS-QMS Platform - Sample Data Generation")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        # Generate data
        generate_customers(db)
        generate_test_requests(db)
        generate_samples(db)
        generate_equipment(db)
        generate_non_conformances(db)
        generate_audit_program(db)
        generate_risk_register(db)

        print("\n" + "=" * 60)
        print("✅ Sample data generation completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error generating data: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
