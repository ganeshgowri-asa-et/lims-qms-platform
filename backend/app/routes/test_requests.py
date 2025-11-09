"""
API routes for Test Request management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.test_request import TestRequest
from app.models.test_parameter import TestParameter
from app.schemas.test_request import (
    TestRequestCreate,
    TestRequestUpdate,
    TestRequestResponse,
    QuoteResponse
)
from app.services.numbering import NumberingService
from app.services.barcode import BarcodeService
from app.services.quote import QuoteService

router = APIRouter()


@router.post("/test-requests", response_model=TestRequestResponse, status_code=201)
def create_test_request(request: TestRequestCreate, db: Session = Depends(get_db)):
    """Create a new test request with auto-generated TRQ number"""

    # Generate TRQ number
    trq_number = NumberingService.generate_test_request_number(db)

    # Generate barcode
    barcode_data = BarcodeService.generate_barcode_for_test_request(trq_number)

    # Create test request
    request_dict = request.model_dump(exclude={'test_parameters'})
    db_request = TestRequest(
        trq_number=trq_number,
        barcode_data=barcode_data,
        status="draft",
        **request_dict
    )

    db.add(db_request)
    db.flush()  # Flush to get the ID

    # Create test parameters
    if request.test_parameters:
        for param_data in request.test_parameters:
            param = TestParameter(
                test_request_id=db_request.id,
                **param_data.model_dump()
            )
            db.add(param)

    db.commit()
    db.refresh(db_request)

    return db_request


@router.get("/test-requests", response_model=List[TestRequestResponse])
def list_test_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all test requests with optional filters"""

    query = db.query(TestRequest)

    if status:
        query = query.filter(TestRequest.status == status)

    if priority:
        query = query.filter(TestRequest.priority == priority)

    if customer_id:
        query = query.filter(TestRequest.customer_id == customer_id)

    requests = query.order_by(TestRequest.created_at.desc()).offset(skip).limit(limit).all()
    return requests


@router.get("/test-requests/{trq_number}", response_model=TestRequestResponse)
def get_test_request(trq_number: str, db: Session = Depends(get_db)):
    """Get a test request by TRQ number"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    return request


@router.put("/test-requests/{trq_number}", response_model=TestRequestResponse)
def update_test_request(
    trq_number: str,
    request_update: TestRequestUpdate,
    db: Session = Depends(get_db)
):
    """Update a test request"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    # Update fields
    update_data = request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    db.commit()
    db.refresh(request)

    return request


@router.post("/test-requests/{trq_number}/submit")
def submit_test_request(
    trq_number: str,
    submitted_by: str,
    db: Session = Depends(get_db)
):
    """Submit a test request for approval"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    request.status = "submitted"
    request.submitted_by = submitted_by
    request.submitted_date = date.today()

    db.commit()

    return {"message": "Test request submitted successfully", "trq_number": trq_number}


@router.post("/test-requests/{trq_number}/approve")
def approve_test_request(
    trq_number: str,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve a test request"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    request.status = "approved"
    request.approved_by = approved_by
    request.approved_date = date.today()

    db.commit()

    return {"message": "Test request approved successfully", "trq_number": trq_number}


@router.post("/test-requests/{trq_number}/generate-quote", response_model=QuoteResponse)
def generate_quote(trq_number: str, db: Session = Depends(get_db)):
    """Generate automated quote for a test request"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    quote = QuoteService.generate_quote(db, request.id)

    return quote


@router.post("/test-requests/{trq_number}/approve-quote")
def approve_quote(
    trq_number: str,
    approved_by: str,
    db: Session = Depends(get_db)
):
    """Approve a quote"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    success = QuoteService.approve_quote(db, request.id, approved_by)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to approve quote")

    return {"message": "Quote approved successfully", "quote_number": request.quote_number}


@router.delete("/test-requests/{trq_number}", status_code=204)
def delete_test_request(trq_number: str, db: Session = Depends(get_db)):
    """Delete a test request"""

    request = db.query(TestRequest).filter(TestRequest.trq_number == trq_number).first()

    if not request:
        raise HTTPException(status_code=404, detail="Test request not found")

    db.delete(request)
    db.commit()

    return None
