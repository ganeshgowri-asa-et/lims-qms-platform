"""
Document management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from app.core.database import get_db
from app.api.schemas import (
    DocumentCreate, DocumentUpdate, DocumentRevise, SignatureCreate,
    DistributionCreate, DocumentResponse, DocumentDetailResponse,
    RevisionResponse, SignatureResponse, DistributionResponse,
    SearchResult, MessageResponse, DocumentStatusEnum, DocumentTypeEnum
)
from app.models.document import QMSDocument, DocumentType, DocumentStatus
from app.services.document_service import DocumentService
from app.services.search_service import SearchService
from app.services.pdf_service import PDFService
from app.core.config import settings


router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize search service
search_service = SearchService()


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new QMS document

    - **title**: Document title (required)
    - **type**: Document type (required)
    - **owner**: Document owner (required)
    - **department**: Department (optional)
    - **description**: Description (optional)
    - **content_text**: Document content for search (optional)
    """
    try:
        # Create document
        new_doc = DocumentService.create_document(
            db=db,
            title=document.title,
            doc_type=DocumentType[document.type.value],
            owner=document.owner,
            description=document.description,
            department=document.department
        )

        # Update content if provided
        if document.content_text:
            new_doc.content_text = document.content_text
            db.commit()
            db.refresh(new_doc)

        # Index for search
        search_service.index_document(new_doc)

        # Add version_string property for response
        response_dict = {
            **new_doc.__dict__,
            'version_string': new_doc.version_string
        }

        return response_dict

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}"
        )


@router.post("/{document_id}/upload", response_model=MessageResponse)
async def upload_document_file(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload file for a document
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # Create storage directory
    storage_path = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(document_id))
    os.makedirs(storage_path, exist_ok=True)

    # Save file
    file_path = os.path.join(storage_path, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update document
    document.file_path = file_path
    document.file_size = os.path.getsize(file_path)
    document.file_hash = DocumentService.calculate_file_hash(file_path)

    db.commit()

    return MessageResponse(
        message="File uploaded successfully",
        detail=f"File saved to {file_path}"
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get document by ID
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    response_dict = {
        **document.__dict__,
        'version_string': document.version_string
    }

    return response_dict


@router.get("/number/{doc_number}", response_model=DocumentDetailResponse)
def get_document_by_number(
    doc_number: str,
    db: Session = Depends(get_db)
):
    """
    Get document by document number
    """
    document = DocumentService.get_document_by_number(db, doc_number)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_number} not found"
        )

    response_dict = {
        **document.__dict__,
        'version_string': document.version_string
    }

    return response_dict


@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    status: Optional[DocumentStatusEnum] = None,
    doc_type: Optional[DocumentTypeEnum] = None,
    owner: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List documents with optional filters

    - **status**: Filter by document status
    - **doc_type**: Filter by document type
    - **owner**: Filter by owner
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    status_filter = DocumentStatus[status.value] if status else None
    type_filter = DocumentType[doc_type.value] if doc_type else None

    documents = DocumentService.list_documents(
        db=db,
        status=status_filter,
        doc_type=type_filter,
        owner=owner,
        skip=skip,
        limit=limit
    )

    return [
        {
            **doc.__dict__,
            'version_string': doc.version_string
        }
        for doc in documents
    ]


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update document metadata
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # Update fields
    if update_data.title:
        document.title = update_data.title
    if update_data.description is not None:
        document.description = update_data.description
    if update_data.department is not None:
        document.department = update_data.department
    if update_data.content_text is not None:
        document.content_text = update_data.content_text

    db.commit()
    db.refresh(document)

    # Re-index for search
    search_service.index_document(document)

    response_dict = {
        **document.__dict__,
        'version_string': document.version_string
    }

    return response_dict


@router.put("/{document_id}/revise", response_model=DocumentResponse)
def revise_document(
    document_id: int,
    revision_data: DocumentRevise,
    db: Session = Depends(get_db)
):
    """
    Create new revision of document (increment version)

    - **is_major**: True for major version increment (e.g., 1.0 -> 2.0), False for minor (e.g., 1.0 -> 1.1)
    - **revised_by**: User making the revision
    - **change_description**: Description of changes
    - **change_reason**: Optional reason for changes
    """
    try:
        document = DocumentService.increment_version(
            db=db,
            document_id=document_id,
            is_major=revision_data.is_major,
            revised_by=revision_data.revised_by,
            change_description=revision_data.change_description
        )

        response_dict = {
            **document.__dict__,
            'version_string': document.version_string
        }

        return response_dict

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{document_id}/approve", response_model=SignatureResponse)
def approve_document(
    document_id: int,
    signature_data: SignatureCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Add approval signature to document

    Approval workflow: DOER -> CHECKER -> APPROVER

    - **role**: Approval role (DOER, CHECKER, APPROVER)
    - **signer**: Name of person signing
    - **signer_email**: Email of signer
    - **signature_hash**: Digital signature hash
    - **comments**: Optional comments
    - **is_approved**: Whether this is an approval (default: true)
    """
    try:
        from app.models.document import ApprovalRole

        # Get client IP
        ip_address = request.client.host if request.client else None

        signature = DocumentService.add_signature(
            db=db,
            document_id=document_id,
            role=ApprovalRole[signature_data.role.value],
            signer=signature_data.signer,
            signer_email=signature_data.signer_email,
            signature_hash=signature_data.signature_hash,
            comments=signature_data.comments,
            is_approved=signature_data.is_approved,
            ip_address=ip_address
        )

        response_dict = {
            **signature.__dict__,
            'version_string': signature.version_string
        }

        return response_dict

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{document_id}/revisions", response_model=List[RevisionResponse])
def get_document_revisions(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get revision history for a document
    """
    from app.models.document import DocumentRevision

    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    revisions = db.query(DocumentRevision).filter(
        DocumentRevision.document_id == document_id
    ).order_by(DocumentRevision.revision_date.desc()).all()

    return [
        {
            **rev.__dict__,
            'version_string': rev.version_string
        }
        for rev in revisions
    ]


@router.get("/{document_id}/signatures", response_model=List[SignatureResponse])
def get_document_signatures(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all signatures for a document
    """
    from app.models.document import DocumentSignature

    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    signatures = db.query(DocumentSignature).filter(
        DocumentSignature.document_id == document_id
    ).order_by(DocumentSignature.sequence, DocumentSignature.signature_timestamp).all()

    return [
        {
            **sig.__dict__,
            'version_string': sig.version_string
        }
        for sig in signatures
    ]


@router.post("/{document_id}/distribute", response_model=DistributionResponse)
def distribute_document(
    document_id: int,
    distribution_data: DistributionCreate,
    db: Session = Depends(get_db)
):
    """
    Create controlled copy distribution

    - **recipient**: Recipient name
    - **recipient_email**: Recipient email
    - **department**: Department
    - **location**: Physical location
    - **distributed_by**: Person distributing
    - **is_controlled**: Whether this is a controlled copy
    """
    try:
        distribution = DocumentService.distribute_document(
            db=db,
            document_id=document_id,
            recipient=distribution_data.recipient,
            recipient_email=distribution_data.recipient_email,
            department=distribution_data.department,
            location=distribution_data.location,
            distributed_by=distribution_data.distributed_by,
            is_controlled=distribution_data.is_controlled
        )

        return distribution

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{document_id}/distributions", response_model=List[DistributionResponse])
def get_document_distributions(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all distributions for a document
    """
    from app.models.document import DocumentDistribution

    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    distributions = db.query(DocumentDistribution).filter(
        DocumentDistribution.document_id == document_id
    ).order_by(DocumentDistribution.distributed_date.desc()).all()

    return distributions


@router.get("/search/", response_model=List[SearchResult])
def search_documents(
    q: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Full-text search across documents

    - **q**: Search query
    - **limit**: Maximum results to return
    """
    try:
        results = search_service.search(q, limit=limit)
        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/{document_id}/pdf", response_model=MessageResponse)
def generate_document_pdf(
    document_id: int,
    include_watermark: bool = True,
    db: Session = Depends(get_db)
):
    """
    Generate PDF for document with optional watermark

    - **include_watermark**: Include watermark for controlled copies
    """
    document = DocumentService.get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    try:
        # Create PDF output path
        pdf_dir = os.path.join(settings.DOCUMENT_STORAGE_PATH, str(document_id))
        os.makedirs(pdf_dir, exist_ok=True)

        pdf_path = os.path.join(pdf_dir, f"{document.doc_number}_v{document.version_string}.pdf")

        # Generate PDF
        PDFService.generate_document_pdf(
            document=document,
            output_path=pdf_path,
            include_watermark=include_watermark
        )

        return MessageResponse(
            message="PDF generated successfully",
            detail=pdf_path
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )
