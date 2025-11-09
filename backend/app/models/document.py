"""
Document Management System Models
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class QMSDocument(Base):
    """QMS Document Master table"""
    __tablename__ = "qms_documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    category = Column(String(100))
    owner = Column(String(100), nullable=False, index=True)
    status = Column(String(50), default="Draft", index=True)
    current_revision = Column(String(20), default="0.1")
    effective_date = Column(Date)
    review_date = Column(Date)
    file_path = Column(String(500))
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    revisions = relationship("DocumentRevision", back_populates="document")
    distributions = relationship("DocumentDistribution", back_populates="document")


class DocumentRevision(Base):
    """Document Revision History"""
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id", ondelete="CASCADE"))
    revision = Column(String(20), nullable=False)
    change_description = Column(Text)
    revised_by = Column(String(100), nullable=False)
    revision_date = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String(500))
    doer = Column(String(100))
    checker = Column(String(100))
    approver = Column(String(100))
    doer_signature = Column(String(500))
    checker_signature = Column(String(500))
    approver_signature = Column(String(500))
    doer_date = Column(DateTime(timezone=True))
    checker_date = Column(DateTime(timezone=True))
    approver_date = Column(DateTime(timezone=True))
    approval_status = Column(String(50), default="Pending")

    # Relationships
    document = relationship("QMSDocument", back_populates="revisions")


class DocumentDistribution(Base):
    """Document Distribution & Control"""
    __tablename__ = "document_distribution"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("qms_documents.id", ondelete="CASCADE"))
    copy_number = Column(Integer, nullable=False)
    issued_to = Column(String(100), nullable=False)
    department = Column(String(100))
    issue_date = Column(Date, nullable=False)
    acknowledgment_date = Column(Date)
    is_controlled = Column(Boolean, default=True)
    status = Column(String(50), default="Active")

    # Relationships
    document = relationship("QMSDocument", back_populates="distributions")
