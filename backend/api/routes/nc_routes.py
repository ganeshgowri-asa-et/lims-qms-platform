"""API routes for Non-Conformance management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.database.models import NCStatus, NCSeverity
from backend.api.schemas import (
    NonConformanceCreate,
    NonConformanceUpdate,
    NonConformanceResponse
)
from backend.services.nc_service import NCService


router = APIRouter(prefix="/api/nc", tags=["Non-Conformance"])


@router.post("/", response_model=NonConformanceResponse, status_code=201)
def create_nc(
    nc_data: NonConformanceCreate,
    db: Session = Depends(get_db)
):
    """Create a new Non-Conformance."""
    try:
        nc = NCService.create_nc(db, nc_data)
        return nc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating NC: {str(e)}")


@router.get("/", response_model=List[NonConformanceResponse])
def get_ncs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[NCStatus] = None,
    severity: Optional[NCSeverity] = None,
    db: Session = Depends(get_db)
):
    """Get all Non-Conformances with optional filtering."""
    ncs = NCService.get_all_ncs(db, skip=skip, limit=limit, status=status, severity=severity)
    return ncs


@router.get("/statistics")
def get_nc_statistics(db: Session = Depends(get_db)):
    """Get NC statistics."""
    stats = NCService.get_nc_statistics(db)
    return stats


@router.get("/{nc_id}", response_model=NonConformanceResponse)
def get_nc(nc_id: int, db: Session = Depends(get_db)):
    """Get a specific Non-Conformance by ID."""
    nc = NCService.get_nc_by_id(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-Conformance not found")
    return nc


@router.get("/number/{nc_number}", response_model=NonConformanceResponse)
def get_nc_by_number(nc_number: str, db: Session = Depends(get_db)):
    """Get a specific Non-Conformance by NC number."""
    nc = NCService.get_nc_by_number(db, nc_number)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-Conformance not found")
    return nc


@router.put("/{nc_id}", response_model=NonConformanceResponse)
def update_nc(
    nc_id: int,
    nc_update: NonConformanceUpdate,
    db: Session = Depends(get_db)
):
    """Update a Non-Conformance."""
    nc = NCService.update_nc(db, nc_id, nc_update)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-Conformance not found")
    return nc


@router.delete("/{nc_id}", status_code=204)
def delete_nc(nc_id: int, db: Session = Depends(get_db)):
    """Delete a Non-Conformance."""
    success = NCService.delete_nc(db, nc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Non-Conformance not found")
    return None
