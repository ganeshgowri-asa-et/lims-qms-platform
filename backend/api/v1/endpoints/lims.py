"""
LIMS Core - Test Request & Sample Management API (Session 5)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.lims import Customer, TestRequest, Sample, TestParameter, TestResult
from backend.models.common import AuditLog


router = APIRouter()


# Schemas
class CustomerCreate(BaseModel):
    company_name: str
    contact_person: str = None
    email: str = None
    phone: str = None


class CustomerResponse(BaseModel):
    id: int
    customer_code: str
    company_name: str

    class Config:
        from_attributes = True


class TestRequestCreate(BaseModel):
    customer_id: int
    request_date: date
    test_standard: str
    sample_type: str
    quantity: int
    created_by_id: int


class TestRequestResponse(BaseModel):
    id: int
    trq_number: str
    customer_id: int
    status: str
    request_date: date

    class Config:
        from_attributes = True


class SampleCreate(BaseModel):
    test_request_id: int
    sample_description: str
    manufacturer: str = None
    model_number: str = None


@router.post("/customers", response_model=CustomerResponse)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create new customer"""

    # Generate customer code
    last_customer = db.query(Customer).order_by(Customer.id.desc()).first()

    if last_customer and last_customer.customer_code:
        last_num = int(last_customer.customer_code.split("-")[-1])
        customer_code = f"CUST-{last_num + 1:04d}"
    else:
        customer_code = "CUST-0001"

    db_customer = Customer(
        customer_code=customer_code,
        company_name=customer.company_name,
        contact_person=customer.contact_person,
        email=customer.email,
        phone=customer.phone
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all customers"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers


@router.post("/test-requests", response_model=TestRequestResponse)
def create_test_request(request: TestRequestCreate, db: Session = Depends(get_db)):
    """Create test request with auto-generated TRQ number"""

    # Generate TRQ number: TRQ-YYYY-XXX
    year = datetime.now().year
    last_trq = db.query(TestRequest).filter(
        TestRequest.trq_number.like(f"TRQ-{year}-%")
    ).order_by(TestRequest.id.desc()).first()

    if last_trq:
        last_num = int(last_trq.trq_number.split("-")[-1])
        trq_number = f"TRQ-{year}-{last_num + 1:03d}"
    else:
        trq_number = f"TRQ-{year}-001"

    db_request = TestRequest(
        trq_number=trq_number,
        customer_id=request.customer_id,
        request_date=request.request_date,
        test_standard=request.test_standard,
        sample_type=request.sample_type,
        quantity=request.quantity,
        created_by_id=request.created_by_id
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Audit log
    audit_log = AuditLog(
        user_id=request.created_by_id,
        module="lims",
        action="create",
        entity_type="test_requests",
        entity_id=db_request.id,
        description=f"Created test request {trq_number}"
    )
    db.add(audit_log)
    db.commit()

    return db_request


@router.get("/test-requests", response_model=List[TestRequestResponse])
def list_test_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all test requests"""
    requests = db.query(TestRequest).offset(skip).limit(limit).all()
    return requests


@router.post("/samples")
def create_sample(sample: SampleCreate, db: Session = Depends(get_db)):
    """Create sample with auto-generated sample ID and barcode"""

    # Generate sample ID
    year = datetime.now().year
    last_sample = db.query(Sample).filter(
        Sample.sample_id.like(f"SMP-{year}-%")
    ).order_by(Sample.id.desc()).first()

    if last_sample:
        last_num = int(last_sample.sample_id.split("-")[-1])
        sample_id = f"SMP-{year}-{last_num + 1:04d}"
    else:
        sample_id = f"SMP-{year}-0001"

    db_sample = Sample(
        sample_id=sample_id,
        test_request_id=sample.test_request_id,
        sample_description=sample.sample_description,
        manufacturer=sample.manufacturer,
        model_number=sample.model_number,
        received_date=date.today()
    )

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    # TODO: Generate barcode (would use python-barcode library)
    # barcode_path = generate_barcode(sample_id)
    # db_sample.barcode_path = barcode_path

    return {"message": "Sample created", "sample_id": sample_id}


@router.get("/samples")
def list_samples(
    test_request_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List samples with filters"""
    query = db.query(Sample)

    if test_request_id:
        query = query.filter(Sample.test_request_id == test_request_id)

    if status:
        query = query.filter(Sample.status == status)

    samples = query.offset(skip).limit(limit).all()
    return samples


@router.post("/test-results")
def create_test_result(
    sample_id: int,
    parameter_id: int,
    test_date: date,
    measured_value: float,
    result: str,
    tested_by_id: int,
    db: Session = Depends(get_db)
):
    """Record test result"""

    db_result = TestResult(
        sample_id=sample_id,
        parameter_id=parameter_id,
        test_date=test_date,
        measured_value=measured_value,
        result=result,
        tested_by_id=tested_by_id
    )

    db.add(db_result)

    # Update sample status
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if sample:
        sample.status = "in_testing"

    db.commit()

    # Audit log
    audit_log = AuditLog(
        user_id=tested_by_id,
        module="lims",
        action="create",
        entity_type="test_results",
        entity_id=db_result.id,
        description=f"Recorded test result for sample {sample.sample_id}"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Test result recorded"}


@router.get("/samples/{sample_id}/results")
def get_sample_results(sample_id: int, db: Session = Depends(get_db)):
    """Get all test results for a sample"""
    results = db.query(TestResult).filter(TestResult.sample_id == sample_id).all()
    return results
