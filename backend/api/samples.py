"""
Sample Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
from backend.database import get_db
from backend.models import Sample, TestRequest

router = APIRouter()


@router.get("/status-summary")
async def get_sample_status_summary(db: Session = Depends(get_db)):
    """Get summary of samples by status"""

    summary = db.query(
        Sample.status,
        func.count(Sample.id).label('count')
    ).group_by(Sample.status).all()

    return {
        "status_summary": [
            {"status": status, "count": count}
            for status, count in summary
        ],
        "total": sum(count for _, count in summary)
    }


@router.get("/{sample_id}")
async def get_sample(sample_id: str, db: Session = Depends(get_db)):
    """Get sample by ID"""

    sample = db.query(Sample).filter(Sample.sample_id == sample_id).first()

    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")

    return {
        "sample_id": sample.sample_id,
        "sample_name": sample.sample_name,
        "sample_type": sample.sample_type,
        "manufacturer": sample.manufacturer,
        "model": sample.model,
        "serial_number": sample.serial_number,
        "received_date": sample.received_date.isoformat(),
        "status": sample.status,
        "storage_location": sample.storage_location,
        "test_request_number": sample.test_request.request_number if sample.test_request else None
    }
