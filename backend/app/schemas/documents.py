"""Pydantic schemas for document management."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.documents import DocumentType, DocumentStatus


# QMS Document Schemas
class QMSDocumentBase(BaseModel):
    """Base schema for QMS documents."""
    title: str = Field(..., min_length=1, max_length=255)
    type: DocumentType
    owner: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    keywords: Optional[str] = Field(None, max_length=500)


class QMSDocumentCreate(QMSDocumentBase):
    """Schema for creating a new document."""
    created_by: str = Field(..., min_length=1, max_length=100)
    full_text_content: Optional[str] = None


class QMSDocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[DocumentType] = None
    owner: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    keywords: Optional[str] = Field(None, max_length=500)
    status: Optional[DocumentStatus] = None


class QMSDocumentResponse(QMSDocumentBase):
    """Schema for document response."""
    id: int
    doc_number: str
    current_revision: str
    current_major_version: int
    current_minor_version: int
    status: DocumentStatus
    created_by: str
    reviewed_by: Optional[str]
    approved_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    effective_date: Optional[datetime]
    obsolete_date: Optional[datetime]
    file_path: Optional[str]
    file_size: Optional[int]

    class Config:
        from_attributes = True


# Document Revision Schemas
class DocumentRevisionBase(BaseModel):
    """Base schema for document revisions."""
    revision_reason: str = Field(..., min_length=1)
    changes_summary: Optional[str] = None
    change_category: Optional[str] = Field(None, max_length=50)


class DocumentRevisionCreate(DocumentRevisionBase):
    """Schema for creating a revision."""
    document_id: int
    revised_by: str = Field(..., min_length=1, max_length=100)
    major_version_increment: bool = False


class DocumentRevisionResponse(DocumentRevisionBase):
    """Schema for revision response."""
    id: int
    document_id: int
    revision_number: str
    major_version: int
    minor_version: int
    revised_by: str
    reviewed_by: Optional[str]
    approved_by: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    approved_at: Optional[datetime]
    effective_date: Optional[datetime]

    class Config:
        from_attributes = True


# Document Distribution Schemas
class DocumentDistributionCreate(BaseModel):
    """Schema for creating document distribution."""
    document_id: int
    copy_type: str = Field(..., max_length=50)
    recipient_name: str = Field(..., min_length=1, max_length=100)
    recipient_email: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    distributed_by: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


# Approval Workflow Schemas
class DocumentApprovalRequest(BaseModel):
    """Schema for document approval."""
    action: str  # review, approve, reject
    comments: Optional[str] = None
    reviewer_name: str = Field(..., min_length=1, max_length=100)
