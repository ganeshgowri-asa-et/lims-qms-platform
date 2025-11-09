"""Document management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....schemas.documents import (
    QMSDocumentCreate,
    QMSDocumentUpdate,
    QMSDocumentResponse,
    DocumentRevisionCreate,
    DocumentRevisionResponse,
    DocumentApprovalRequest,
)
from ....services.document_service import DocumentService
from ....models.documents import DocumentType, DocumentStatus
from ....utils.pdf_generator import generate_document_pdf

router = APIRouter()


@router.post("/", response_model=QMSDocumentResponse, status_code=201)
def create_document(
    document: QMSDocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new QMS document with auto-generated document number."""
    try:
        db_document = DocumentService.create_document(db, document)
        return db_document
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[QMSDocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all documents with pagination."""
    documents = DocumentService.get_all_documents(db, skip=skip, limit=limit)
    return documents


@router.get("/{document_id}", response_model=QMSDocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/{document_id}", response_model=QMSDocumentResponse)
def update_document(
    document_id: int,
    updates: QMSDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document details."""
    document = DocumentService.update_document(db, document_id, updates)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/{document_id}/revise", response_model=DocumentRevisionResponse, status_code=201)
def create_revision(
    document_id: int,
    revision: DocumentRevisionCreate,
    db: Session = Depends(get_db)
):
    """Create a new revision of a document."""
    # Ensure document_id matches
    revision.document_id = document_id

    db_revision = DocumentService.create_revision(db, revision)
    if not db_revision:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_revision


@router.post("/{document_id}/approve", response_model=QMSDocumentResponse)
def approve_document(
    document_id: int,
    approval: DocumentApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve document through workflow.
    Actions: 'review', 'approve', 'reject'
    """
    if approval.action not in ["review", "approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'review', 'approve', or 'reject'")

    document = DocumentService.approve_document(
        db, document_id, approval.action, approval.reviewer_name
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/revisions", response_model=List[DocumentRevisionResponse])
def get_document_revisions(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get all revisions for a document."""
    revisions = DocumentService.get_document_revisions(db, document_id)
    return revisions


@router.get("/search/", response_model=List[QMSDocumentResponse])
def search_documents(
    q: Optional[str] = Query(None, description="Search term"),
    doc_type: Optional[DocumentType] = Query(None, description="Document type"),
    status: Optional[DocumentStatus] = Query(None, description="Document status"),
    db: Session = Depends(get_db)
):
    """Search documents by term, type, or status."""
    documents = DocumentService.search_documents(
        db, search_term=q, doc_type=doc_type, status=status
    )
    return documents


@router.post("/{document_id}/generate-pdf")
def generate_pdf(
    document_id: int,
    watermark: Optional[str] = Query("CONTROLLED COPY", description="Watermark text"),
    db: Session = Depends(get_db)
):
    """Generate PDF for document with watermark."""
    document = DocumentService.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get revisions
    revisions = DocumentService.get_document_revisions(db, document_id)

    # Prepare document data
    document_data = {
        "title": document.title,
        "doc_number": document.doc_number,
        "current_revision": document.current_revision,
        "status": document.status.value,
        "owner": document.owner,
        "department": document.department,
        "effective_date": str(document.effective_date) if document.effective_date else "N/A",
        "created_by": document.created_by,
        "approved_by": document.approved_by or "N/A",
        "description": document.description or "",
        "revisions": [
            {
                "revision_number": rev.revision_number,
                "created_at": str(rev.created_at),
                "revised_by": rev.revised_by,
                "revision_reason": rev.revision_reason,
            }
            for rev in revisions
        ],
    }

    # Generate PDF
    output_path = f"/tmp/documents/{document.doc_number}_v{document.current_revision}.pdf"
    pdf_path = generate_document_pdf(document_data, output_path, watermark_text=watermark)

    return {"message": "PDF generated successfully", "path": pdf_path}
