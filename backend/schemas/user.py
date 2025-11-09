"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    employee_id: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Create user schema"""
    password: str = Field(..., min_length=8)
    role_ids: Optional[List[int]] = []
    manager_id: Optional[int] = None
    is_superuser: bool = False
    force_password_change: bool = True

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Update user schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)
    profile_image: Optional[str] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    manager_id: Optional[int] = None


class UserAdminUpdate(UserUpdate):
    """Admin update user schema with additional fields"""
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    role_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None
    force_password_change: Optional[bool] = None
    concurrent_sessions_limit: Optional[int] = Field(None, ge=1, le=10)


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    uuid: str
    username: str
    email: str
    full_name: str
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    is_superuser: bool
    is_verified: bool
    is_active: bool
    mfa_enabled: bool
    profile_image: Optional[str] = None
    preferred_language: str
    timezone: str
    last_login: Optional[datetime] = None
    date_joined: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithRoles(UserResponse):
    """User response with roles"""
    roles: List['RoleResponse'] = []

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Detailed user profile"""
    email_verified: bool
    phone_verified: bool
    manager_id: Optional[int] = None
    last_login_ip: Optional[str] = None
    last_activity: Optional[datetime] = None
    roles: List['RoleResponse'] = []
    permissions: List[str] = []  # Computed permissions

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """User list response"""
    total: int
    page: int
    page_size: int
    users: List[UserResponse]


class UserSearchRequest(BaseModel):
    """User search request"""
    query: Optional[str] = None
    department: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UserActivateRequest(BaseModel):
    """User activation request"""
    reason: Optional[str] = None


class UserDeactivateRequest(BaseModel):
    """User deactivation request"""
    reason: str = Field(..., min_length=10)
    date_terminated: Optional[datetime] = None


class UserRoleAssignment(BaseModel):
    """Assign/remove roles"""
    role_ids: List[int] = Field(..., min_items=1)
    reason: Optional[str] = None


class UserBulkAction(BaseModel):
    """Bulk user action"""
    user_ids: List[int] = Field(..., min_items=1)
    action: str = Field(..., regex='^(activate|deactivate|delete|assign_role|remove_role)$')
    role_id: Optional[int] = None
    reason: Optional[str] = None


# Import for forward references
from .role import RoleResponse
UserWithRoles.model_rebuild()
UserProfile.model_rebuild()
