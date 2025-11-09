"""Document Management System models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration."""
    PROCEDURE = "procedure"
    FORM = "form"
    POLICY = "policy"
    MANUAL = "manual"
    WORK_INSTRUCTION = "work_instruction"
    SPECIFICATION = "specification"
    RECORD = "record"


class DocumentStatus(str, enum.Enum):
    """Document status enumeration."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class QMSDocument(Base):
    """QMS Document master table."""
    __tablename__ = "qms_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    type = Column(Enum(DocumentType), nullable=False)

    # Current version info
    current_revision = Column(String(20), default="1.0")
    current_major_version = Column(Integer, default=1)
    current_minor_version = Column(Integer, default=0)

    # Ownership and responsibility
    owner = Column(String(100), nullable=False)
    department = Column(String(100))

    # Status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)

    # Approval workflow
    created_by = Column(String(100), nullable=False)
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)
    approved_at = Column(DateTime)
    effective_date = Column(DateTime)
    obsolete_date = Column(DateTime)

    # Content
    description = Column(Text)
    keywords = Column(String(500))
    full_text_content = Column(Text)  # For full-text search

    # File storage
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(64))  # SHA-256 hash

    # Additional metadata
    metadata = Column(JSON)

    # Relationships
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    distributions = relationship("DocumentDistribution", back_populates="document", cascade="all, delete-orphan")


class DocumentRevision(Base):
    """Document revision history."""
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)

    # Version information
    revision_number = Column(String(20), nullable=False)
    major_version = Column(Integer, nullable=False)
    minor_version = Column(Integer, nullable=False)

    # Change details
    revision_reason = Column(Text, nullable=False)
    changes_summary = Column(Text)
    change_category = Column(String(50))  # minor, major, critical

    # Approval details
    revised_by = Column(String(100), nullable=False)
    reviewed_by = Column(String(100))
    approved_by = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime)
    approved_at = Column(DateTime)
    effective_date = Column(DateTime)

    # File reference
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(64))

    # Digital signature
    digital_signature = Column(Text)
    signature_timestamp = Column(DateTime)

    # Metadata
    metadata = Column(JSON)

    # Relationships
    document = relationship("QMSDocument", back_populates="revisions")


class DocumentDistribution(Base):
    """Controlled copy distribution tracking."""
    __tablename__ = "document_distribution"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)

    # Distribution details
    copy_number = Column(String(20), nullable=False)
    copy_type = Column(String(50))  # controlled, uncontrolled, electronic, hardcopy

    # Recipient information
    recipient_name = Column(String(100), nullable=False)
    recipient_email = Column(String(100))
    department = Column(String(100))
    location = Column(String(100))

    # Distribution tracking
    distributed_by = Column(String(100))
    distributed_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)

    # Status
    is_active = Column(Boolean, default=True)
    returned_at = Column(DateTime)

    # Metadata
    notes = Column(Text)
    metadata = Column(JSON)

    # Relationships
    document = relationship("QMSDocument", back_populates="distributions")
