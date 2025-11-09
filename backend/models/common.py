"""
Common Models - Users, Audit Logs, etc.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from backend.core.database import Base


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # admin, quality_manager, technician, customer
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit trail for all system changes"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module = Column(String(50), nullable=False)  # documents, equipment, lims, etc.
    action = Column(String(50), nullable=False)  # create, update, delete, approve
    entity_type = Column(String(100), nullable=False)  # table name
    entity_id = Column(Integer, nullable=False)
    description = Column(Text)
    changes = Column(Text)  # JSON string of changes
    ip_address = Column(String(50))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
