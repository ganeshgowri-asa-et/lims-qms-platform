"""
Role delegation and substitution schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class DelegationBase(BaseModel):
    """Base delegation schema"""
    delegate_id: int = Field(..., gt=0)
    role_id: Optional[int] = None
    reason: Optional[str] = None
    scope: str = Field('all', regex='^(all|specific_permissions)$')


class DelegationCreate(DelegationBase):
    """Create delegation schema"""
    start_date: datetime
    end_date: datetime
    permissions: Optional[List[str]] = None
    auto_route_approvals: bool = True

    @validator('end_date')
    def end_date_after_start(cls, v, values):
        """Validate end date is after start date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

    @validator('permissions')
    def permissions_required_for_specific_scope(cls, v, values):
        """Validate permissions are provided for specific scope"""
        if 'scope' in values and values['scope'] == 'specific_permissions':
            if not v or len(v) == 0:
                raise ValueError('Permissions must be specified for specific_permissions scope')
        return v


class DelegationUpdate(BaseModel):
    """Update delegation schema"""
    end_date: Optional[datetime] = None
    reason: Optional[str] = None
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None
    auto_route_approvals: Optional[bool] = None


class DelegationResponse(BaseModel):
    """Delegation response schema"""
    id: int
    uuid: str
    delegator_id: int
    delegator_name: str
    delegate_id: int
    delegate_name: str
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    reason: Optional[str] = None
    scope: str
    permissions: Optional[List[str]] = None
    start_date: datetime
    end_date: datetime
    is_active: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    auto_route_approvals: bool
    created_at: datetime
    is_current: bool = False

    class Config:
        from_attributes = True


class DelegationList(BaseModel):
    """Delegation list response"""
    total: int
    page: int
    page_size: int
    delegations: List[DelegationResponse]


class DelegationApprove(BaseModel):
    """Approve delegation request"""
    approved: bool
    notes: Optional[str] = None


class DelegationSearchRequest(BaseModel):
    """Delegation search request"""
    delegator_id: Optional[int] = None
    delegate_id: Optional[int] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    current_only: bool = False  # Only show current delegations
    pending_approval: bool = False  # Only show pending approvals
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class DelegationStats(BaseModel):
    """Delegation statistics"""
    total_delegations: int
    active_delegations: int
    pending_approvals: int
    expired_delegations: int
    by_role: Dict[str, int]


class ActiveDelegationCheck(BaseModel):
    """Check if user has active delegation"""
    user_id: int
    role_id: Optional[int] = None


class ActiveDelegationResponse(BaseModel):
    """Active delegation check response"""
    has_delegation: bool
    delegations: List[DelegationResponse]
    effective_permissions: List[str]
