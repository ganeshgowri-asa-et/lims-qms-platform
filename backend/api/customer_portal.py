"""
Customer Portal API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from backend.database import get_db
from backend.models import (
    Customer, CustomerPortalUser, TestRequest, Sample, TestParameter
)

router = APIRouter()


# Pydantic models for request/response
class TestRequestCreate(BaseModel):
    sample_description: str
    test_type: str
    required_date: Optional[str] = None
    priority: str = "Normal"

    class Config:
        from_attributes = True


class TestRequestResponse(BaseModel):
    id: int
    request_number: str
    request_date: str
    required_date: Optional[str]
    sample_description: str
    test_type: str
    priority: str
    status: str
    quote_amount: Optional[float]
    quote_approved: bool

    class Config:
        from_attributes = True


class SampleTrackingResponse(BaseModel):
    sample_id: str
    sample_name: str
    status: str
    received_date: str
    test_request_number: str
    test_progress: Optional[int] = 0

    class Config:
        from_attributes = True


@router.post("/test-requests", response_model=TestRequestResponse)
async def create_test_request(
    request: TestRequestCreate,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Customer creates a new test request"""

    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Generate request number
    year = datetime.now().year
    count = db.query(TestRequest).filter(
        TestRequest.request_number.like(f"TRQ-{year}-%")
    ).count()
    request_number = f"TRQ-{year}-{count + 1:04d}"

    # Create test request
    new_request = TestRequest(
        request_number=request_number,
        customer_id=customer_id,
        request_date=datetime.now().date(),
        required_date=datetime.fromisoformat(request.required_date).date()
            if request.required_date else None,
        sample_description=request.sample_description,
        test_type=request.test_type,
        priority=request.priority,
        status="Submitted",
        created_by=customer.name
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return TestRequestResponse(
        id=new_request.id,
        request_number=new_request.request_number,
        request_date=new_request.request_date.isoformat(),
        required_date=new_request.required_date.isoformat() if new_request.required_date else None,
        sample_description=new_request.sample_description,
        test_type=new_request.test_type,
        priority=new_request.priority,
        status=new_request.status,
        quote_amount=float(new_request.quote_amount) if new_request.quote_amount else None,
        quote_approved=new_request.quote_approved
    )


@router.get("/test-requests/{customer_id}", response_model=List[TestRequestResponse])
async def get_customer_test_requests(
    customer_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all test requests for a customer"""

    query = db.query(TestRequest).filter(TestRequest.customer_id == customer_id)

    if status:
        query = query.filter(TestRequest.status == status)

    requests = query.order_by(TestRequest.request_date.desc()).all()

    return [
        TestRequestResponse(
            id=req.id,
            request_number=req.request_number,
            request_date=req.request_date.isoformat(),
            required_date=req.required_date.isoformat() if req.required_date else None,
            sample_description=req.sample_description,
            test_type=req.test_type,
            priority=req.priority,
            status=req.status,
            quote_amount=float(req.quote_amount) if req.quote_amount else None,
            quote_approved=req.quote_approved
        )
        for req in requests
    ]


@router.get("/samples/track/{customer_id}", response_model=List[SampleTrackingResponse])
async def track_customer_samples(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Track all samples for a customer in real-time"""

    # Get all samples for customer's test requests
    samples = db.query(Sample).join(TestRequest).filter(
        TestRequest.customer_id == customer_id
    ).order_by(Sample.received_date.desc()).all()

    tracking_data = []
    for sample in samples:
        # Calculate test progress
        total_params = db.query(TestParameter).filter(
            TestParameter.sample_id == sample.id
        ).count()

        completed_params = db.query(TestParameter).filter(
            and_(
                TestParameter.sample_id == sample.id,
                TestParameter.tested_date.isnot(None)
            )
        ).count()

        progress = int((completed_params / total_params * 100)) if total_params > 0 else 0

        tracking_data.append(
            SampleTrackingResponse(
                sample_id=sample.sample_id,
                sample_name=sample.sample_name,
                status=sample.status,
                received_date=sample.received_date.isoformat(),
                test_request_number=sample.test_request.request_number,
                test_progress=progress
            )
        )

    return tracking_data


@router.get("/samples/{sample_id}/details")
async def get_sample_details(
    sample_id: str,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific sample"""

    # Get sample and verify it belongs to the customer
    sample = db.query(Sample).join(TestRequest).filter(
        and_(
            Sample.sample_id == sample_id,
            TestRequest.customer_id == customer_id
        )
    ).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    # Get test parameters
    parameters = db.query(TestParameter).filter(
        TestParameter.sample_id == sample.id
    ).all()

    return {
        "sample_id": sample.sample_id,
        "sample_name": sample.sample_name,
        "sample_type": sample.sample_type,
        "manufacturer": sample.manufacturer,
        "model": sample.model,
        "serial_number": sample.serial_number,
        "received_date": sample.received_date.isoformat(),
        "status": sample.status,
        "test_request_number": sample.test_request.request_number,
        "test_parameters": [
            {
                "parameter_name": param.parameter_name,
                "test_method": param.test_method,
                "specification": param.specification,
                "result": param.result,
                "unit": param.unit,
                "pass_fail": param.pass_fail,
                "tested_date": param.tested_date.isoformat() if param.tested_date else None,
                "status": "Completed" if param.tested_date else "Pending"
            }
            for param in parameters
        ]
    }


@router.get("/dashboard/{customer_id}")
async def get_customer_dashboard(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get dashboard data for customer portal"""

    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get statistics
    total_requests = db.query(TestRequest).filter(
        TestRequest.customer_id == customer_id
    ).count()

    active_requests = db.query(TestRequest).filter(
        and_(
            TestRequest.customer_id == customer_id,
            TestRequest.status.in_(['Submitted', 'In Progress', 'Testing'])
        )
    ).count()

    completed_requests = db.query(TestRequest).filter(
        and_(
            TestRequest.customer_id == customer_id,
            TestRequest.status == 'Completed'
        )
    ).count()

    # Get recent requests
    recent_requests = db.query(TestRequest).filter(
        TestRequest.customer_id == customer_id
    ).order_by(TestRequest.request_date.desc()).limit(5).all()

    # Get active samples
    active_samples = db.query(Sample).join(TestRequest).filter(
        and_(
            TestRequest.customer_id == customer_id,
            Sample.status.in_(['Received', 'In Progress', 'Testing'])
        )
    ).all()

    return {
        "customer": {
            "name": customer.name,
            "customer_code": customer.customer_code,
            "email": customer.email
        },
        "statistics": {
            "total_requests": total_requests,
            "active_requests": active_requests,
            "completed_requests": completed_requests,
            "active_samples": len(active_samples)
        },
        "recent_requests": [
            {
                "request_number": req.request_number,
                "request_date": req.request_date.isoformat(),
                "test_type": req.test_type,
                "status": req.status
            }
            for req in recent_requests
        ],
        "active_samples": [
            {
                "sample_id": sample.sample_id,
                "sample_name": sample.sample_name,
                "status": sample.status,
                "received_date": sample.received_date.isoformat()
            }
            for sample in active_samples
        ]
    }
