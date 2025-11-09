"""API routes for CAPA management."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.database.models import CAPAStatus, CAPAType
from backend.api.schemas import (
    CAPAActionCreate,
    CAPAActionUpdate,
    CAPAActionResponse
)
from backend.services.capa_service import CAPAService


router = APIRouter(prefix="/api/capa", tags=["CAPA"])


@router.post("/", response_model=CAPAActionResponse, status_code=201)
def create_capa(
    capa_data: CAPAActionCreate,
    db: Session = Depends(get_db)
):
    """Create a new CAPA Action."""
    try:
        capa = CAPAService.create_capa(db, capa_data)
        return capa
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating CAPA: {str(e)}")


@router.get("/", response_model=List[CAPAActionResponse])
def get_capas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[CAPAStatus] = None,
    capa_type: Optional[CAPAType] = None,
    db: Session = Depends(get_db)
):
    """Get all CAPA Actions with optional filtering."""
    capas = CAPAService.get_all_capas(db, skip=skip, limit=limit, status=status, capa_type=capa_type)
    return capas


@router.get("/statistics")
def get_capa_statistics(db: Session = Depends(get_db)):
    """Get CAPA statistics."""
    stats = CAPAService.get_capa_statistics(db)
    return stats


@router.get("/overdue", response_model=List[CAPAActionResponse])
def get_overdue_capas(db: Session = Depends(get_db)):
    """Get all overdue CAPA actions."""
    capas = CAPAService.get_overdue_capas(db)
    return capas


@router.get("/{capa_id}", response_model=CAPAActionResponse)
def get_capa(capa_id: int, db: Session = Depends(get_db)):
    """Get a specific CAPA Action by ID."""
    capa = CAPAService.get_capa_by_id(db, capa_id)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return capa


@router.get("/number/{capa_number}", response_model=CAPAActionResponse)
def get_capa_by_number(capa_number: str, db: Session = Depends(get_db)):
    """Get a specific CAPA Action by CAPA number."""
    capa = CAPAService.get_capa_by_number(db, capa_number)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return capa


@router.get("/nc/{nc_id}", response_model=List[CAPAActionResponse])
def get_capas_by_nc(nc_id: int, db: Session = Depends(get_db)):
    """Get all CAPA Actions for a specific NC."""
    capas = CAPAService.get_capas_by_nc(db, nc_id)
    return capas


@router.put("/{capa_id}", response_model=CAPAActionResponse)
def update_capa(
    capa_id: int,
    capa_update: CAPAActionUpdate,
    db: Session = Depends(get_db)
):
    """Update a CAPA Action."""
    capa = CAPAService.update_capa(db, capa_id, capa_update)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return capa


@router.delete("/{capa_id}", status_code=204)
def delete_capa(capa_id: int, db: Session = Depends(get_db)):
    """Delete a CAPA Action."""
    success = CAPAService.delete_capa(db, capa_id)
    if not success:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return None
