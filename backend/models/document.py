"""
Document Management System models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum


class DocumentLevelEnum(str, enum.Enum):
    """Document hierarchy levels"""
    LEVEL_1 = "Level 1"  # Quality Manual, Policy
    LEVEL_2 = "Level 2"  # Quality System Procedures
    LEVEL_3 = "Level 3"  # Operation & Test Procedures
    LEVEL_4 = "Level 4"  # Templates, Formats, Checklists
    LEVEL_5 = "Level 5"  # Records


class DocumentStatusEnum(str, enum.Enum):
    """Document status"""
    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    OBSOLETE = "Obsolete"
    ARCHIVED = "Archived"


class DocumentLevel(BaseModel):
    """Document Level configuration"""
    __tablename__ = 'document_levels'

    level_number = Column(Integer, nullable=False, unique=True)
    level_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    numbering_format = Column(String(100), nullable=True)  # e.g., "L1-{year}-{seq:04d}"


class Document(BaseModel):
    """Document model"""
    __tablename__ = 'documents'

    document_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    level = Column(Enum(DocumentLevelEnum), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)  # ISO 17025, ISO 9001, etc.
    standard = Column(String(100), nullable=True)  # IEC 61215, 61730, etc.
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.DRAFT, nullable=False)
    description = Column(Text, nullable=True)
    current_version_id = Column(Integer, ForeignKey('document_versions.id'), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    parent_document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)
    tags = Column(JSON, nullable=True)  # ["calibration", "equipment", "quality"]
    metadata = Column(JSON, nullable=True)

    # Workflow fields
    doer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    checker_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(String(255), nullable=True)
    approved_at = Column(String(255), nullable=True)

    # Relationships
    versions = relationship('DocumentVersion', back_populates='document', foreign_keys='DocumentVersion.document_id')
    parent_document = relationship('Document', remote_side='Document.id', foreign_keys=[parent_document_id])


class DocumentVersion(BaseModel):
    """Document version history"""
    __tablename__ = 'document_versions'

    document_id = Column(Integer, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    version_number = Column(String(20), nullable=False)  # 1.0, 1.1, 2.0
    revision_number = Column(Integer, default=0)
    change_summary = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # SHA-256 hash
    released_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    released_at = Column(String(255), nullable=True)

    # Relationships
    document = relationship('Document', back_populates='versions', foreign_keys=[document_id])
