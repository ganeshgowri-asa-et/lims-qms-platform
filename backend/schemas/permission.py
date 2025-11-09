"""
Permission schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=3, max_length=100)
    resource: str = Field(..., min_length=2, max_length=100)
    action: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Create permission schema"""
    scope: str = Field('all', regex='^(all|own|department|team)$')
    conditions: Optional[Dict[str, Any]] = None


class PermissionUpdate(BaseModel):
    """Update permission schema"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    scope: Optional[str] = Field(None, regex='^(all|own|department|team)$')
    conditions: Optional[Dict[str, Any]] = None


class PermissionResponse(BaseModel):
    """Permission response schema"""
    id: int
    uuid: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    scope: str
    conditions: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionList(BaseModel):
    """Permission list response"""
    total: int
    permissions: List[PermissionResponse]


class PermissionCheck(BaseModel):
    """Check if user has permission"""
    resource: str
    action: str
    resource_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PermissionCheckResponse(BaseModel):
    """Permission check response"""
    has_permission: bool
    reason: Optional[str] = None
    matched_permission: Optional[str] = None


class PermissionBulkCreate(BaseModel):
    """Bulk create permissions"""
    permissions: List[PermissionCreate] = Field(..., min_items=1)


class ResourcePermissions(BaseModel):
    """Permissions grouped by resource"""
    resource: str
    permissions: List[PermissionResponse]
