"""
Document Management System API (Session 2)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.core.database import get_db
from backend.models.documents import QMSDocument, DocumentRevision, DocumentDistribution
from backend.models.common import AuditLog
from pydantic import BaseModel


router = APIRouter()


# Pydantic schemas
class DocumentCreate(BaseModel):
    title: str
    doc_type: str
    owner_id: int
    description: str = None


class DocumentResponse(BaseModel):
    id: int
    doc_number: str
    title: str
    doc_type: str
    current_revision: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RevisionCreate(BaseModel):
    changes_description: str
    revised_by: int


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """Create new QMS document with auto-generated doc number"""

    # Generate doc number: QSF-YYYY-XXX
    year = datetime.now().year
    last_doc = db.query(QMSDocument).filter(
        QMSDocument.doc_number.like(f"QSF-{year}-%")
    ).order_by(QMSDocument.id.desc()).first()

    if last_doc:
        last_num = int(last_doc.doc_number.split("-")[-1])
        doc_number = f"QSF-{year}-{last_num + 1:03d}"
    else:
        doc_number = f"QSF-{year}-001"

    # Create document
    db_document = QMSDocument(
        doc_number=doc_number,
        title=document.title,
        doc_type=document.doc_type,
        owner_id=document.owner_id,
        description=document.description,
        created_by=document.owner_id
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Create audit log
    audit_log = AuditLog(
        user_id=document.owner_id,
        module="documents",
        action="create",
        entity_type="qms_documents",
        entity_id=db_document.id,
        description=f"Created document {doc_number}"
    )
    db.add(audit_log)
    db.commit()

    return db_document


@router.get("/", response_model=List[DocumentResponse])
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all QMS documents"""
    documents = db.query(QMSDocument).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/revise", status_code=status.HTTP_201_CREATED)
def revise_document(document_id: int, revision: RevisionCreate, db: Session = Depends(get_db)):
    """Create new revision of document"""
    document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Parse current revision
    major, minor = document.current_revision.split(".")
    new_revision = f"{major}.{int(minor) + 1}"

    # Create revision record
    db_revision = DocumentRevision(
        document_id=document_id,
        revision=new_revision,
        changes_description=revision.changes_description,
        revised_by=revision.revised_by
    )

    # Update document
    document.current_revision = new_revision

    db.add(db_revision)
    db.commit()

    # Audit log
    audit_log = AuditLog(
        user_id=revision.revised_by,
        module="documents",
        action="revise",
        entity_type="qms_documents",
        entity_id=document_id,
        description=f"Created revision {new_revision}"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Revision created", "new_revision": new_revision}


@router.put("/{document_id}/approve")
def approve_document(document_id: int, approved_by: int, db: Session = Depends(get_db)):
    """Approve document"""
    document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "approved"
    db.commit()

    # Audit log
    audit_log = AuditLog(
        user_id=approved_by,
        module="documents",
        action="approve",
        entity_type="qms_documents",
        entity_id=document_id,
        description=f"Approved document {document.doc_number}"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Document approved"}


@router.get("/{document_id}/revisions")
def get_document_revisions(document_id: int, db: Session = Depends(get_db)):
    """Get all revisions of a document"""
    revisions = db.query(DocumentRevision).filter(
        DocumentRevision.document_id == document_id
    ).all()
    return revisions
