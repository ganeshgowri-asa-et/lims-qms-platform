"""API routes for Root Cause Analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.api.schemas import (
    RootCauseAnalysisCreate,
    RootCauseAnalysisUpdate,
    RootCauseAnalysisResponse,
    AIRootCauseSuggestionRequest,
    AIRootCauseSuggestionResponse
)
from backend.services.rca_service import RCAService
from backend.services.ai_service import AIService


router = APIRouter(prefix="/api/rca", tags=["Root Cause Analysis"])


@router.post("/", response_model=RootCauseAnalysisResponse, status_code=201)
def create_rca(
    rca_data: RootCauseAnalysisCreate,
    db: Session = Depends(get_db)
):
    """Create a new Root Cause Analysis."""
    try:
        rca = RCAService.create_rca(db, rca_data)
        return rca
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating RCA: {str(e)}")


@router.get("/{rca_id}", response_model=RootCauseAnalysisResponse)
def get_rca(rca_id: int, db: Session = Depends(get_db)):
    """Get a specific Root Cause Analysis by ID."""
    rca = RCAService.get_rca_by_id(db, rca_id)
    if not rca:
        raise HTTPException(status_code=404, detail="RCA not found")
    return rca


@router.get("/nc/{nc_id}", response_model=List[RootCauseAnalysisResponse])
def get_rcas_by_nc(nc_id: int, db: Session = Depends(get_db)):
    """Get all Root Cause Analyses for a specific NC."""
    rcas = RCAService.get_rcas_by_nc(db, nc_id)
    return rcas


@router.put("/{rca_id}", response_model=RootCauseAnalysisResponse)
def update_rca(
    rca_id: int,
    rca_update: RootCauseAnalysisUpdate,
    db: Session = Depends(get_db)
):
    """Update a Root Cause Analysis."""
    rca = RCAService.update_rca(db, rca_id, rca_update)
    if not rca:
        raise HTTPException(status_code=404, detail="RCA not found")
    return rca


@router.post("/{rca_id}/approve", response_model=RootCauseAnalysisResponse)
def approve_rca(
    rca_id: int,
    approved_by: str,
    comments: str = None,
    db: Session = Depends(get_db)
):
    """Approve a Root Cause Analysis."""
    rca = RCAService.approve_rca(db, rca_id, approved_by, comments)
    if not rca:
        raise HTTPException(status_code=404, detail="RCA not found")
    return rca


@router.delete("/{rca_id}", status_code=204)
def delete_rca(rca_id: int, db: Session = Depends(get_db)):
    """Delete a Root Cause Analysis."""
    success = RCAService.delete_rca(db, rca_id)
    if not success:
        raise HTTPException(status_code=404, detail="RCA not found")
    return None


@router.get("/templates/5why")
def get_5why_template():
    """Get a template for 5-Why analysis."""
    return RCAService.generate_5why_template()


@router.get("/templates/fishbone")
def get_fishbone_template():
    """Get a template for Fishbone diagram."""
    return RCAService.generate_fishbone_template()


@router.post("/ai/suggestions", response_model=AIRootCauseSuggestionResponse)
def get_ai_suggestions(request: AIRootCauseSuggestionRequest):
    """Get AI-powered root cause suggestions."""
    try:
        result = AIService.get_root_cause_suggestions(
            nc_description=request.nc_description,
            problem_details=request.problem_details,
            context=request.context
        )
        return AIRootCauseSuggestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI suggestions: {str(e)}")
