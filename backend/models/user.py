"""
User, Role, and Permission models with comprehensive authentication and authorization
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel

# Enums
class MFAType(str, enum.Enum):
    """Multi-Factor Authentication types"""
    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, Authy)
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class SessionStatus(str, enum.Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOGGED_OUT = "logged_out"


class ActivityType(str, enum.Enum):
    """User activity types"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    PROFILE_UPDATE = "profile_update"
    PERMISSION_CHANGE = "permission_change"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class DocumentClassification(str, enum.Enum):
    """Document classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# Many-to-many relationship tables
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)

role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)


class User(BaseModel):
    """User model with comprehensive authentication and authorization"""
    __tablename__ = 'users'

    # Basic Information
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    designation = Column(String(100), nullable=True)

    # Authentication & Authorization
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    # Multi-Factor Authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)  # Encrypted TOTP secret
    mfa_backup_codes = Column(JSON, nullable=True)  # Encrypted backup codes

    # Password Security
    password_changed_at = Column(DateTime, nullable=True)
    password_expires_at = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)

    # Session Management
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    last_activity = Column(DateTime, nullable=True)
    concurrent_sessions_limit = Column(Integer, default=5)

    # Profile
    profile_image = Column(String(500), nullable=True)
    preferred_language = Column(String(10), default='en')
    timezone = Column(String(50), default='UTC')

    # SSO Integration
    sso_provider = Column(String(50), nullable=True)  # 'google', 'microsoft', 'saml'
    sso_id = Column(String(255), nullable=True)
    sso_data = Column(JSON, nullable=True)

    # Additional Fields
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    date_joined = Column(DateTime, default=datetime.utcnow)
    date_terminated = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    manager = relationship('User', remote_side='User.id', foreign_keys=[manager_id])
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    login_history = relationship('LoginHistory', back_populates='user', cascade='all, delete-orphan')
    api_keys = relationship('UserAPIKey', back_populates='user', cascade='all, delete-orphan')
    activities = relationship('UserActivity', back_populates='user', cascade='all, delete-orphan')
    password_history = relationship('PasswordHistory', back_populates='user', cascade='all, delete-orphan')
    competencies = relationship('UserCompetency', back_populates='user', cascade='all, delete-orphan')
    delegations_given = relationship('RoleDelegation', foreign_keys='RoleDelegation.delegator_id', back_populates='delegator')
    delegations_received = relationship('RoleDelegation', foreign_keys='RoleDelegation.delegate_id', back_populates='delegate')


class Role(BaseModel):
    """Role model for RBAC with hierarchy support"""
    __tablename__ = 'roles'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Role Hierarchy
    parent_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    level = Column(Integer, default=0)  # Hierarchy level

    # Role Configuration
    is_system_role = Column(Boolean, default=False)  # Cannot be deleted
    is_custom = Column(Boolean, default=False)
    max_users = Column(Integer, nullable=True)  # Maximum users allowed for this role

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    parent_role = relationship('Role', remote_side='Role.id', foreign_keys=[parent_role_id])


class Permission(BaseModel):
    """Permission model for fine-grained access control"""
    __tablename__ = 'permissions'

    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False, index=True)  # e.g., 'document', 'user', 'project'
    action = Column(String(50), nullable=False, index=True)  # e.g., 'create', 'read', 'update', 'delete', 'approve'
    description = Column(Text, nullable=True)

    # Permission Scope
    scope = Column(String(50), default='all')  # 'all', 'own', 'department', 'team'
    conditions = Column(JSON, nullable=True)  # Additional permission conditions

    # Relationships
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')


class UserSession(BaseModel):
    """User session management for tracking active sessions"""
    __tablename__ = 'user_sessions'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = Column(String(500), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500), nullable=True)

    # Session Details
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    location = Column(String(255), nullable=True)

    # Session Status
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.ACTIVE, index=True)
    login_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    logout_at = Column(DateTime, nullable=True)

    # Security
    is_suspicious = Column(Boolean, default=False)

    # Relationships
    user = relationship('User', back_populates='sessions')


class LoginHistory(BaseModel):
    """Track all login attempts for security auditing"""
    __tablename__ = 'login_history'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    username = Column(String(100), nullable=True, index=True)  # Store even if login failed

    # Login Details
    success = Column(Boolean, nullable=False, index=True)
    ip_address = Column(String(50), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    location = Column(String(255), nullable=True)

    # Failure Details
    failure_reason = Column(String(255), nullable=True)

    # Timestamps
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='login_history')


class UserAPIKey(BaseModel):
    """API keys for programmatic access"""
    __tablename__ = 'user_api_keys'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Descriptive name for the key
    key_hash = Column(String(255), unique=True, nullable=False, index=True)  # Hashed API key
    key_prefix = Column(String(20), nullable=False)  # First few chars for identification

    # Permissions & Scope
    scopes = Column(JSON, nullable=True)  # List of allowed scopes/permissions
    ip_whitelist = Column(JSON, nullable=True)  # Allowed IP addresses

    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    last_used_ip = Column(String(50), nullable=True)
    usage_count = Column(Integer, default=0)

    # Expiration
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship('User', back_populates='api_keys')


class UserActivity(BaseModel):
    """Comprehensive user activity tracking and audit log"""
    __tablename__ = 'user_activities'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    username = Column(String(100), nullable=True)  # Cache username for deleted users

    # Activity Details
    activity_type = Column(SQLEnum(ActivityType), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True, index=True)  # e.g., 'document', 'user', 'project'
    resource_id = Column(String(100), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # e.g., 'create', 'update', 'delete', 'view'
    description = Column(Text, nullable=True)

    # Request Context
    ip_address = Column(String(50), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)

    # Changes Tracking
    changes = Column(JSON, nullable=True)  # Before/after values
    metadata = Column(JSON, nullable=True)  # Additional context

    # Security
    is_suspicious = Column(Boolean, default=False, index=True)
    risk_score = Column(Integer, default=0)

    # Timestamps
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship('User', back_populates='activities')


class PasswordHistory(BaseModel):
    """Track password history to prevent reuse"""
    __tablename__ = 'password_history'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    user = relationship('User', back_populates='password_history')


class UserCompetency(BaseModel):
    """Track employee certifications, training, and competencies"""
    __tablename__ = 'user_competencies'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Competency Details
    competency_type = Column(String(50), nullable=False)  # 'certification', 'training', 'equipment', 'test_method'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Certification/Training Details
    issuing_authority = Column(String(255), nullable=True)
    certificate_number = Column(String(100), nullable=True)
    document_path = Column(String(500), nullable=True)

    # Equipment/Test Method Authorization
    equipment_id = Column(String(100), nullable=True)  # Reference to equipment
    test_method_id = Column(String(100), nullable=True)  # Reference to test method
    approval_level = Column(Integer, default=1)  # Authority level (1-5)

    # Validity
    obtained_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True, index=True)
    is_valid = Column(Boolean, default=True)

    # Verification
    verified_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship('User', back_populates='competencies')


class RoleDelegation(BaseModel):
    """Temporary role delegation and substitution"""
    __tablename__ = 'role_delegations'

    delegator_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    delegate_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=True)

    # Delegation Details
    reason = Column(Text, nullable=True)
    scope = Column(String(50), default='all')  # 'all', 'specific_permissions'
    permissions = Column(JSON, nullable=True)  # Specific permissions if scope is 'specific_permissions'

    # Validity Period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True)

    # Approval
    approved_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Auto-routing
    auto_route_approvals = Column(Boolean, default=True)

    # Relationships
    delegator = relationship('User', foreign_keys=[delegator_id], back_populates='delegations_given')
    delegate = relationship('User', foreign_keys=[delegate_id], back_populates='delegations_received')


class IPWhitelist(BaseModel):
    """IP whitelisting for enhanced security"""
    __tablename__ = 'ip_whitelists'

    # Scope
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=True, index=True)
    is_global = Column(Boolean, default=False)  # Global whitelist for all users

    # IP Configuration
    ip_address = Column(String(50), nullable=False, index=True)
    ip_range_start = Column(String(50), nullable=True)
    ip_range_end = Column(String(50), nullable=True)
    cidr_notation = Column(String(50), nullable=True)

    # Details
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)


class SSOProvider(BaseModel):
    """SSO Provider Configuration (OAuth2, SAML)"""
    __tablename__ = 'sso_providers'

    name = Column(String(100), unique=True, nullable=False)
    provider_type = Column(String(50), nullable=False)  # 'oauth2', 'saml', 'oidc'
    display_name = Column(String(255), nullable=False)

    # OAuth2 Configuration
    client_id = Column(String(255), nullable=True)
    client_secret = Column(String(500), nullable=True)  # Encrypted
    authorize_url = Column(String(500), nullable=True)
    token_url = Column(String(500), nullable=True)
    userinfo_url = Column(String(500), nullable=True)
    scopes = Column(JSON, nullable=True)

    # SAML Configuration
    saml_entity_id = Column(String(500), nullable=True)
    saml_sso_url = Column(String(500), nullable=True)
    saml_certificate = Column(Text, nullable=True)
    saml_metadata_url = Column(String(500), nullable=True)

    # Attribute Mapping
    attribute_mapping = Column(JSON, nullable=True)  # Map SSO attributes to user fields

    # Settings
    auto_create_users = Column(Boolean, default=True)
    default_role_id = Column(Integer, ForeignKey('roles.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    # Domain Restrictions
    allowed_domains = Column(JSON, nullable=True)  # Email domains allowed for this provider
