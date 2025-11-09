"""
SQLAlchemy ORM models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AuditLog(Base):
    """Audit log model for tracking all database changes"""

    __tablename__ = "audit_log"

    audit_id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)
