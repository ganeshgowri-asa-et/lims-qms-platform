"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from backend.database.models import (
    NCStatus, NCSeverity, NCSource, CAPAType, CAPAStatus, RCAMethod
)


# ============= Non-Conformance Schemas =============

class NonConformanceCreate(BaseModel):
    """Schema for creating a new Non-Conformance."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    source: NCSource
    severity: NCSeverity
    detected_date: Optional[datetime] = None
    detected_by: str
    department: Optional[str] = None
    location: Optional[str] = None
    related_document: Optional[str] = None
    related_equipment: Optional[str] = None
    related_test_request: Optional[str] = None
    related_batch: Optional[str] = None
    impact_description: Optional[str] = None
    quantity_affected: Optional[int] = None
    cost_impact: Optional[float] = None
    immediate_action: Optional[str] = None
    assigned_to: Optional[str] = None
    target_closure_date: Optional[date] = None
    created_by: str


class NonConformanceUpdate(BaseModel):
    """Schema for updating a Non-Conformance."""
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[NCSource] = None
    severity: Optional[NCSeverity] = None
    status: Optional[NCStatus] = None
    department: Optional[str] = None
    location: Optional[str] = None
    impact_description: Optional[str] = None
    quantity_affected: Optional[int] = None
    cost_impact: Optional[float] = None
    immediate_action: Optional[str] = None
    containment_date: Optional[datetime] = None
    containment_by: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_date: Optional[datetime] = None
    target_closure_date: Optional[date] = None
    actual_closure_date: Optional[date] = None
    updated_by: str


class NonConformanceResponse(BaseModel):
    """Schema for Non-Conformance response."""
    id: int
    nc_number: str
    title: str
    description: str
    source: NCSource
    severity: NCSeverity
    status: NCStatus
    detected_date: datetime
    detected_by: str
    department: Optional[str]
    location: Optional[str]
    related_document: Optional[str]
    related_equipment: Optional[str]
    related_test_request: Optional[str]
    related_batch: Optional[str]
    impact_description: Optional[str]
    quantity_affected: Optional[int]
    cost_impact: Optional[float]
    immediate_action: Optional[str]
    containment_date: Optional[datetime]
    containment_by: Optional[str]
    assigned_to: Optional[str]
    assigned_date: Optional[datetime]
    target_closure_date: Optional[date]
    actual_closure_date: Optional[date]
    verified_by: Optional[str]
    verification_date: Optional[datetime]
    verification_comments: Optional[str]
    effectiveness_verified: bool
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


# ============= Root Cause Analysis Schemas =============

class FiveWhyStep(BaseModel):
    """Schema for a single step in 5-Why analysis."""
    level: int = Field(..., ge=1, le=5)
    why: str
    answer: str


class FishboneCategory(BaseModel):
    """Schema for fishbone diagram categories."""
    man: List[str] = []
    machine: List[str] = []
    method: List[str] = []
    material: List[str] = []
    measurement: List[str] = []
    environment: List[str] = []


class RootCauseAnalysisCreate(BaseModel):
    """Schema for creating Root Cause Analysis."""
    nc_id: int
    method: RCAMethod
    analyzed_by: str
    five_why_data: Optional[List[FiveWhyStep]] = None
    fishbone_data: Optional[FishboneCategory] = None
    root_cause: str = Field(..., min_length=10)
    contributing_factors: Optional[List[str]] = None
    supporting_data: Optional[str] = None


class RootCauseAnalysisUpdate(BaseModel):
    """Schema for updating Root Cause Analysis."""
    method: Optional[RCAMethod] = None
    five_why_data: Optional[List[FiveWhyStep]] = None
    fishbone_data: Optional[FishboneCategory] = None
    root_cause: Optional[str] = None
    contributing_factors: Optional[List[str]] = None
    supporting_data: Optional[str] = None
    approved_by: Optional[str] = None
    approval_comments: Optional[str] = None


class RootCauseAnalysisResponse(BaseModel):
    """Schema for Root Cause Analysis response."""
    id: int
    nc_id: int
    method: RCAMethod
    analysis_date: datetime
    analyzed_by: str
    five_why_data: Optional[Dict[str, Any]]
    fishbone_data: Optional[Dict[str, Any]]
    ai_suggestions: Optional[Dict[str, Any]]
    ai_model_used: Optional[str]
    ai_confidence_score: Optional[float]
    root_cause: str
    contributing_factors: Optional[Dict[str, Any]]
    evidence_attachments: Optional[Dict[str, Any]]
    supporting_data: Optional[str]
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    approval_comments: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============= CAPA Action Schemas =============

class CAPAActionCreate(BaseModel):
    """Schema for creating a CAPA Action."""
    nc_id: int
    capa_type: CAPAType
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    assigned_to: str
    assigned_by: str
    due_date: date
    implementation_plan: Optional[str] = None
    resources_required: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    verification_method: Optional[str] = None
    verification_criteria: Optional[str] = None
    created_by: str


class CAPAActionUpdate(BaseModel):
    """Schema for updating a CAPA Action."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CAPAStatus] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    completed_date: Optional[date] = None
    implementation_plan: Optional[str] = None
    resources_required: Optional[List[str]] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    action_taken: Optional[str] = None
    completion_comments: Optional[str] = None
    verification_method: Optional[str] = None
    verification_criteria: Optional[str] = None
    verification_due_date: Optional[date] = None
    verification_date: Optional[date] = None
    verified_by: Optional[str] = None
    verification_result: Optional[bool] = None
    verification_comments: Optional[str] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[date] = None
    follow_up_comments: Optional[str] = None
    updated_by: str


class CAPAActionResponse(BaseModel):
    """Schema for CAPA Action response."""
    id: int
    capa_number: str
    nc_id: int
    capa_type: CAPAType
    title: str
    description: str
    status: CAPAStatus
    assigned_to: str
    assigned_date: datetime
    assigned_by: str
    due_date: date
    completed_date: Optional[date]
    implementation_plan: Optional[str]
    resources_required: Optional[Dict[str, Any]]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    action_taken: Optional[str]
    completion_evidence: Optional[Dict[str, Any]]
    completion_comments: Optional[str]
    verification_method: Optional[str]
    verification_criteria: Optional[str]
    verification_due_date: Optional[date]
    verification_date: Optional[date]
    verified_by: Optional[str]
    verification_result: Optional[bool]
    verification_comments: Optional[str]
    effectiveness_rating: Optional[int]
    follow_up_required: bool
    follow_up_date: Optional[date]
    follow_up_comments: Optional[str]
    closed_by: Optional[str]
    closure_date: Optional[datetime]
    closure_comments: Optional[str]
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


# ============= AI Request Schemas =============

class AIRootCauseSuggestionRequest(BaseModel):
    """Schema for requesting AI root cause suggestions."""
    nc_description: str
    problem_details: str
    context: Optional[str] = None


class AIRootCauseSuggestionResponse(BaseModel):
    """Schema for AI root cause suggestion response."""
    suggestions: List[str]
    model_used: str
    confidence_score: float
