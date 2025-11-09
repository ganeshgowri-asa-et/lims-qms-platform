"""
Document Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from backend.core import get_db
from backend.models.document import Document, DocumentVersion, DocumentLevelEnum, DocumentStatusEnum
from backend.api.dependencies.auth import get_current_user
from backend.models.user import User
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from datetime import datetime

router = APIRouter()


class DocumentCreate(BaseModel):
    title: str
    level: DocumentLevelEnum
    category: Optional[str] = None
    standard: Optional[str] = None
    description: Optional[str] = None
    parent_document_id: Optional[int] = None


class DocumentResponse(BaseModel):
    id: int
    document_number: str
    title: str
    level: str
    status: str
    category: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    # Generate document number
    level_prefix = document.level.value.replace(" ", "")[1]
    year = datetime.now().year
    count = db.query(Document).filter(Document.level == document.level).count() + 1
    document_number = f"L{level_prefix}-{year}-{count:04d}"

    new_document = Document(
        document_number=document_number,
        title=document.title,
        level=document.level,
        category=document.category,
        standard=document.standard,
        description=document.description,
        parent_document_id=document.parent_document_id,
        status=DocumentStatusEnum.DRAFT,
        doer_id=current_user.id,
        created_by_id=current_user.id
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    level: Optional[DocumentLevelEnum] = None,
    status: Optional[DocumentStatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents with optional filters"""
    query = db.query(Document).filter(Document.is_deleted == False)

    if level:
        query = query.filter(Document.level == level)
    if status:
        query = query.filter(Document.status == status)

    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get document by ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == False
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.put("/{document_id}/approve")
async def approve_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a document"""
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.status = DocumentStatusEnum.APPROVED
    document.approver_id = current_user.id
    document.approved_at = str(datetime.now())

    db.commit()

    return {"message": "Document approved successfully"}
