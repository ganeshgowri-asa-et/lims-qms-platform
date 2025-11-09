"""
Pydantic schemas for request/response validation
"""
from .auth import *
from .user import *
from .role import *
from .permission import *
from .session import *
from .activity import *
from .competency import *
from .delegation import *

__all__ = [
    # Auth schemas
    "Token",
    "TokenData",
    "LoginRequest",
    "RegisterRequest",
    "PasswordResetRequest",
    "PasswordChangeRequest",
    "MFASetupResponse",
    "MFAVerifyRequest",

    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserList",
    "UserProfile",

    # Role schemas
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "RoleWithPermissions",

    # Permission schemas
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",

    # Session schemas
    "SessionResponse",
    "SessionList",

    # Activity schemas
    "ActivityResponse",
    "ActivityList",

    # Competency schemas
    "CompetencyBase",
    "CompetencyCreate",
    "CompetencyUpdate",
    "CompetencyResponse",

    # Delegation schemas
    "DelegationBase",
    "DelegationCreate",
    "DelegationUpdate",
    "DelegationResponse",
]
