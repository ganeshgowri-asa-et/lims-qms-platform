"""
Role schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Create role schema"""
    parent_role_id: Optional[int] = None
    permission_ids: Optional[List[int]] = []
    is_custom: bool = True
    max_users: Optional[int] = Field(None, gt=0)


class RoleUpdate(BaseModel):
    """Update role schema"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    parent_role_id: Optional[int] = None
    permission_ids: Optional[List[int]] = None
    max_users: Optional[int] = Field(None, gt=0)


class RoleResponse(BaseModel):
    """Role response schema"""
    id: int
    uuid: str
    name: str
    code: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None
    level: int
    is_system_role: bool
    is_custom: bool
    max_users: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleResponse):
    """Role response with permissions"""
    permissions: List['PermissionResponse'] = []
    user_count: Optional[int] = None

    class Config:
        from_attributes = True


class RoleHierarchy(RoleResponse):
    """Role hierarchy response"""
    parent_role: Optional['RoleResponse'] = None
    child_roles: List['RoleResponse'] = []

    class Config:
        from_attributes = True


class RoleList(BaseModel):
    """Role list response"""
    total: int
    roles: List[RoleResponse]


class RolePermissionAssignment(BaseModel):
    """Assign/remove permissions to role"""
    permission_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., regex='^(add|remove|replace)$')


class RoleStats(BaseModel):
    """Role statistics"""
    role_id: int
    role_name: str
    user_count: int
    permission_count: int
    active_users: int
    inactive_users: int


# Import for forward references
from .permission import PermissionResponse
RoleWithPermissions.model_rebuild()
