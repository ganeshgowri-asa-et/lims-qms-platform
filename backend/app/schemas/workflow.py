"""
Pydantic schemas for Workflow (Doer-Checker-Approver)
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WorkflowSubmit(BaseModel):
    """Submit record for checking"""
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class WorkflowCheck(BaseModel):
    """Checker reviews and approves/rejects"""
    approved: bool
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class WorkflowApprove(BaseModel):
    """Final approval"""
    approved: bool
    comments: Optional[str] = None
    signature_data: Optional[str] = None


class WorkflowReject(BaseModel):
    """Reject record with reason"""
    reason: str
    comments: Optional[str] = None


class WorkflowStatus(BaseModel):
    """Current workflow status"""
    status: str
    doer_id: Optional[int] = None
    doer_timestamp: Optional[datetime] = None
    doer_comments: Optional[str] = None
    checker_id: Optional[int] = None
    checker_timestamp: Optional[datetime] = None
    checker_comments: Optional[str] = None
    approver_id: Optional[int] = None
    approver_timestamp: Optional[datetime] = None
    approver_comments: Optional[str] = None
    rejected_by_id: Optional[int] = None
    rejection_timestamp: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True
