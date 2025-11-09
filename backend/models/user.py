"""
User, Role, and Permission models
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

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
    """User model"""
    __tablename__ = 'users'

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    profile_image = Column(String(500), nullable=True)
    preferred_language = Column(String(10), default='en')
    last_login = Column(String(255), nullable=True)

    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), unique=True, nullable=False)

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')


class Permission(BaseModel):
    """Permission model for fine-grained access control"""
    __tablename__ = 'permissions'

    name = Column(String(100), unique=True, nullable=False)
    resource = Column(String(100), nullable=False)  # e.g., 'document', 'user', 'project'
    action = Column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
