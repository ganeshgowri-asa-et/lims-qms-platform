"""
API routes for Sample management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleUpdate, SampleResponse
from app.services.numbering import NumberingService
from app.services.barcode import BarcodeService

router = APIRouter()


@router.post("/samples", response_model=SampleResponse, status_code=201)
def create_sample(sample: SampleCreate, db: Session = Depends(get_db)):
    """Create a new sample with auto-generated sample number"""

    # Generate sample number
    sample_number = NumberingService.generate_sample_number(db)

    # Generate barcode
    barcode_data = BarcodeService.generate_barcode_for_sample(sample_number)

    # Create sample
    db_sample = Sample(
        sample_number=sample_number,
        barcode_data=barcode_data,
        status="pending",
        **sample.model_dump()
    )

    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)

    return db_sample


@router.get("/samples", response_model=List[SampleResponse])
def list_samples(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    test_request_id: Optional[int] = None,
    sample_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all samples with optional filters"""

    query = db.query(Sample)

    if status:
        query = query.filter(Sample.status == status)

    if test_request_id:
        query = query.filter(Sample.test_request_id == test_request_id)

    if sample_type:
        query = query.filter(Sample.sample_type == sample_type)

    samples = query.order_by(Sample.created_at.desc()).offset(skip).limit(limit).all()
    return samples


@router.get("/samples/{sample_number}", response_model=SampleResponse)
def get_sample(sample_number: str, db: Session = Depends(get_db)):
    """Get a sample by sample number"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    return sample


@router.get("/samples/by-id/{sample_id}", response_model=SampleResponse)
def get_sample_by_id(sample_id: int, db: Session = Depends(get_db)):
    """Get a sample by ID"""

    sample = db.query(Sample).filter(Sample.id == sample_id).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    return sample


@router.put("/samples/{sample_number}", response_model=SampleResponse)
def update_sample(
    sample_number: str,
    sample_update: SampleUpdate,
    db: Session = Depends(get_db)
):
    """Update a sample"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    # Update fields
    update_data = sample_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sample, field, value)

    db.commit()
    db.refresh(sample)

    return sample


@router.post("/samples/{sample_number}/receive")
def receive_sample(
    sample_number: str,
    received_by: str,
    db: Session = Depends(get_db)
):
    """Mark a sample as received"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    sample.status = "received"
    sample.received_by = received_by
    sample.received_date = date.today()

    db.commit()

    return {"message": "Sample received successfully", "sample_number": sample_number}


@router.post("/samples/{sample_number}/start-testing")
def start_testing(
    sample_number: str,
    db: Session = Depends(get_db)
):
    """Mark sample as in testing"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    sample.status = "in_testing"
    sample.testing_start_date = date.today()

    db.commit()

    return {"message": "Testing started", "sample_number": sample_number}


@router.post("/samples/{sample_number}/complete-testing")
def complete_testing(
    sample_number: str,
    db: Session = Depends(get_db)
):
    """Mark sample testing as completed"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    sample.status = "completed"
    sample.testing_end_date = date.today()

    db.commit()

    return {"message": "Testing completed", "sample_number": sample_number}


@router.delete("/samples/{sample_number}", status_code=204)
def delete_sample(sample_number: str, db: Session = Depends(get_db)):
    """Delete a sample"""

    sample = db.query(Sample).filter(Sample.sample_number == sample_number).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    db.delete(sample)
    db.commit()

    return None
