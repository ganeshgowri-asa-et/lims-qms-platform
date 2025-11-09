"""
Document Management System Models (Session 2)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from backend.core.database import Base


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    OBSOLETE = "obsolete"


class DocumentType(str, enum.Enum):
    QUALITY_MANUAL = "quality_manual"
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    RECORD = "record"
    POLICY = "policy"


class QMSDocument(Base):
    """QMS Document master table"""
    __tablename__ = "qms_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(50), unique=True, nullable=False, index=True)  # QSF-YYYY-XXX
    title = Column(String(200), nullable=False)
    doc_type = Column(SQLEnum(DocumentType), nullable=False)
    current_revision = Column(String(20), default="1.0")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    description = Column(Text)
    file_path = Column(String(500))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    revisions = relationship("DocumentRevision", back_populates="document")
    distributions = relationship("DocumentDistribution", back_populates="document")


class DocumentRevision(Base):
    """Document revision history"""
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)
    revision = Column(String(20), nullable=False)
    changes_description = Column(Text, nullable=False)
    revised_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    revision_date = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String(500))
    digital_signature = Column(Text)  # JSON with signatures

    # Relationships
    document = relationship("QMSDocument", back_populates="revisions")


class DocumentDistribution(Base):
    """Controlled document distribution"""
    __tablename__ = "document_distribution"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id"), nullable=False)
    copy_number = Column(Integer, nullable=False)
    issued_to = Column(String(100), nullable=False)
    department = Column(String(100))
    issued_date = Column(DateTime(timezone=True), server_default=func.now())
    returned_date = Column(DateTime(timezone=True))
    is_controlled = Column(String(20), default="Controlled")

    # Relationships
    document = relationship("QMSDocument", back_populates="distributions")
