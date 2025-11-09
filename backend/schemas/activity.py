"""
User activity and audit log schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ActivityResponse(BaseModel):
    """User activity response"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    activity_type: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_suspicious: bool = False
    risk_score: int = 0
    occurred_at: datetime

    class Config:
        from_attributes = True


class ActivityList(BaseModel):
    """Activity list response"""
    total: int
    page: int
    page_size: int
    activities: List[ActivityResponse]


class ActivitySearchRequest(BaseModel):
    """Activity search request"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    activity_type: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    is_suspicious: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ActivityStats(BaseModel):
    """Activity statistics"""
    total_activities: int
    activities_by_type: Dict[str, int]
    activities_by_user: List[Dict[str, Any]]
    suspicious_activities: int
    date_range: Dict[str, datetime]


class AuditLogExportRequest(BaseModel):
    """Audit log export request"""
    from_date: datetime
    to_date: datetime
    user_ids: Optional[List[int]] = None
    activity_types: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    format: str = Field('csv', regex='^(csv|json|pdf)$')
