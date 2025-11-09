"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class DocumentTypeEnum(str, Enum):
    PROCEDURE = "PROCEDURE"
    WORK_INSTRUCTION = "WORK_INSTRUCTION"
    FORM = "FORM"
    SPECIFICATION = "SPECIFICATION"
    MANUAL = "MANUAL"
    POLICY = "POLICY"
    RECORD = "RECORD"
    REPORT = "REPORT"


class DocumentStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    EFFECTIVE = "EFFECTIVE"
    OBSOLETE = "OBSOLETE"
    SUPERSEDED = "SUPERSEDED"


class ApprovalRoleEnum(str, Enum):
    DOER = "DOER"
    CHECKER = "CHECKER"
    APPROVER = "APPROVER"


# Request schemas
class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    type: DocumentTypeEnum
    owner: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    content_text: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    content_text: Optional[str] = None


class DocumentRevise(BaseModel):
    is_major: bool = Field(default=False)
    revised_by: str = Field(..., min_length=1, max_length=100)
    change_description: str = Field(..., min_length=1)
    change_reason: Optional[str] = None


class SignatureCreate(BaseModel):
    role: ApprovalRoleEnum
    signer: str = Field(..., min_length=1, max_length=100)
    signer_email: EmailStr
    signature_hash: str = Field(..., min_length=1, max_length=256)
    comments: Optional[str] = None
    is_approved: bool = Field(default=True)


class DistributionCreate(BaseModel):
    recipient: str = Field(..., min_length=1, max_length=100)
    recipient_email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    distributed_by: Optional[str] = Field(None, max_length=100)
    is_controlled: bool = Field(default=True)


# Response schemas
class DocumentResponse(BaseModel):
    id: int
    doc_number: str
    title: str
    type: DocumentTypeEnum
    major_version: int
    minor_version: int
    version_string: str
    owner: str
    department: Optional[str]
    status: DocumentStatusEnum
    description: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    effective_date: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    content_text: Optional[str]
    file_hash: Optional[str]
    review_date: Optional[datetime]
    obsolete_date: Optional[datetime]

    class Config:
        from_attributes = True


class RevisionResponse(BaseModel):
    id: int
    document_id: int
    major_version: int
    minor_version: int
    version_string: str
    revision_number: int
    revision_date: datetime
    revised_by: str
    change_description: str
    change_reason: Optional[str]

    class Config:
        from_attributes = True


class SignatureResponse(BaseModel):
    id: int
    document_id: int
    role: ApprovalRoleEnum
    signer: str
    signer_email: Optional[str]
    signature_timestamp: datetime
    major_version: int
    minor_version: int
    version_string: str
    sequence: int
    comments: Optional[str]
    is_approved: bool

    class Config:
        from_attributes = True


class DistributionResponse(BaseModel):
    id: int
    document_id: int
    copy_number: str
    recipient: str
    recipient_email: Optional[str]
    department: Optional[str]
    location: Optional[str]
    distributed_date: datetime
    distributed_by: Optional[str]
    is_controlled: bool
    is_active: bool
    version_distributed: Optional[str]

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    doc_id: int
    doc_number: str
    title: str
    score: Optional[float] = None


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
