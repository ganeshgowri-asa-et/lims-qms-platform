"""
Document management models
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text,
    Boolean, Float, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PROCEDURE = "PROCEDURE"
    WORK_INSTRUCTION = "WORK_INSTRUCTION"
    FORM = "FORM"
    SPECIFICATION = "SPECIFICATION"
    MANUAL = "MANUAL"
    POLICY = "POLICY"
    RECORD = "RECORD"
    REPORT = "REPORT"


class DocumentStatus(str, enum.Enum):
    """Document status enumeration"""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EFFECTIVE = "EFFECTIVE"
    OBSOLETE = "OBSOLETE"
    SUPERSEDED = "SUPERSEDED"


class ApprovalRole(str, enum.Enum):
    """Approval workflow role enumeration"""
    DOER = "DOER"
    CHECKER = "CHECKER"
    APPROVER = "APPROVER"


class QMSDocument(Base):
    """
    Main document table for QMS document control
    """
    __tablename__ = "qms_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    type = Column(SQLEnum(DocumentType), nullable=False)

    # Version tracking (major.minor format)
    major_version = Column(Integer, default=1, nullable=False)
    minor_version = Column(Integer, default=0, nullable=False)

    # Document metadata
    owner = Column(String(100), nullable=False)
    department = Column(String(100))
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)

    # Content and storage
    description = Column(Text)
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(64))  # SHA-256 hash for integrity

    # Full-text search
    content_text = Column(Text)  # Extracted text for search

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    effective_date = Column(DateTime(timezone=True))
    review_date = Column(DateTime(timezone=True))
    obsolete_date = Column(DateTime(timezone=True))

    # Relationships
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")
    distributions = relationship("DocumentDistribution", back_populates="document", cascade="all, delete-orphan")
    signatures = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_doc_status', 'status'),
        Index('idx_doc_type', 'type'),
        Index('idx_doc_owner', 'owner'),
        Index('idx_doc_created', 'created_at'),
    )

    @property
    def version_string(self):
        """Return version in major.minor format"""
        return f"{self.major_version}.{self.minor_version}"

    def __repr__(self):
        return f"<QMSDocument {self.doc_number} v{self.version_string} - {self.title}>"


class DocumentRevision(Base):
    """
    Document revision history tracking
    """
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)

    # Version at time of revision
    major_version = Column(Integer, nullable=False)
    minor_version = Column(Integer, nullable=False)

    # Revision details
    revision_number = Column(Integer, nullable=False)
    revision_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revised_by = Column(String(100), nullable=False)

    # Change tracking
    change_description = Column(Text, nullable=False)
    change_reason = Column(Text)

    # File snapshot
    file_path = Column(String(500))
    file_hash = Column(String(64))

    # Previous version reference
    previous_revision_id = Column(Integer, ForeignKey("document_revisions.id"))

    # Relationship
    document = relationship("QMSDocument", back_populates="revisions")

    __table_args__ = (
        Index('idx_rev_document', 'document_id'),
        Index('idx_rev_date', 'revision_date'),
    )

    @property
    def version_string(self):
        """Return version in major.minor format"""
        return f"{self.major_version}.{self.minor_version}"

    def __repr__(self):
        return f"<DocumentRevision {self.revision_number} - v{self.version_string}>"


class DocumentDistribution(Base):
    """
    Controlled copy distribution tracking
    """
    __tablename__ = "document_distribution"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)

    # Distribution details
    copy_number = Column(String(20), nullable=False)
    recipient = Column(String(100), nullable=False)
    recipient_email = Column(String(255))
    department = Column(String(100))
    location = Column(String(200))

    # Distribution tracking
    distributed_date = Column(DateTime(timezone=True), server_default=func.now())
    distributed_by = Column(String(100))

    # Control
    is_controlled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    returned_date = Column(DateTime(timezone=True))

    # Version distributed
    version_distributed = Column(String(20))

    # Relationship
    document = relationship("QMSDocument", back_populates="distributions")

    __table_args__ = (
        Index('idx_dist_document', 'document_id'),
        Index('idx_dist_recipient', 'recipient'),
        Index('idx_dist_active', 'is_active'),
    )

    def __repr__(self):
        return f"<DocumentDistribution {self.copy_number} to {self.recipient}>"


class DocumentSignature(Base):
    """
    Digital signature tracking for approval workflow
    """
    __tablename__ = "document_signatures"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)

    # Signature details
    role = Column(SQLEnum(ApprovalRole), nullable=False)
    signer = Column(String(100), nullable=False)
    signer_email = Column(String(255))

    # Signature data
    signature_hash = Column(String(256), nullable=False)  # Digital signature
    signature_data = Column(Text)  # Optional: signature image/data
    signature_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Document version signed
    major_version = Column(Integer, nullable=False)
    minor_version = Column(Integer, nullable=False)

    # Approval workflow
    sequence = Column(Integer, default=1)  # Order in approval chain
    comments = Column(Text)
    is_approved = Column(Boolean, default=True)

    # IP and audit trail
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Relationship
    document = relationship("QMSDocument", back_populates="signatures")

    __table_args__ = (
        Index('idx_sig_document', 'document_id'),
        Index('idx_sig_role', 'role'),
        Index('idx_sig_signer', 'signer'),
        Index('idx_sig_timestamp', 'signature_timestamp'),
    )

    @property
    def version_string(self):
        """Return version in major.minor format"""
        return f"{self.major_version}.{self.minor_version}"

    def __repr__(self):
        return f"<DocumentSignature {self.role} by {self.signer}>"
