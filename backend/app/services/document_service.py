"""Document management service with business logic."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from ..models.documents import QMSDocument, DocumentRevision, DocumentStatus, DocumentType
from ..schemas.documents import QMSDocumentCreate, QMSDocumentUpdate, DocumentRevisionCreate


class DocumentService:
    """Service for document management operations."""

    @staticmethod
    def generate_document_number(db: Session, doc_type: DocumentType) -> str:
        """
        Generate auto document number in format: QSF-YYYY-XXX
        where XXX is a sequential number.
        """
        current_year = datetime.now().year

        # Get the count of documents created this year
        count = db.query(QMSDocument).filter(
            QMSDocument.doc_number.like(f"QSF-{current_year}-%")
        ).count()

        # Generate next number
        next_number = count + 1
        doc_number = f"QSF-{current_year}-{next_number:03d}"

        return doc_number

    @staticmethod
    def create_document(db: Session, document: QMSDocumentCreate) -> QMSDocument:
        """Create a new document with auto-generated document number."""
        # Generate document number
        doc_number = DocumentService.generate_document_number(db, document.type)

        # Create document
        db_document = QMSDocument(
            doc_number=doc_number,
            title=document.title,
            type=document.type,
            owner=document.owner,
            department=document.department,
            description=document.description,
            keywords=document.keywords,
            created_by=document.created_by,
            full_text_content=document.full_text_content,
            current_revision="1.0",
            current_major_version=1,
            current_minor_version=0,
            status=DocumentStatus.DRAFT,
        )

        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        # Create initial revision record
        initial_revision = DocumentRevision(
            document_id=db_document.id,
            revision_number="1.0",
            major_version=1,
            minor_version=0,
            revision_reason="Initial version",
            revised_by=document.created_by,
        )
        db.add(initial_revision)
        db.commit()

        return db_document

    @staticmethod
    def update_document(
        db: Session, document_id: int, updates: QMSDocumentUpdate
    ) -> Optional[QMSDocument]:
        """Update document details."""
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def create_revision(
        db: Session, revision: DocumentRevisionCreate
    ) -> Optional[DocumentRevision]:
        """Create a new revision of a document."""
        document = db.query(QMSDocument).filter(
            QMSDocument.id == revision.document_id
        ).first()

        if not document:
            return None

        # Calculate new version numbers
        if revision.major_version_increment:
            new_major = document.current_major_version + 1
            new_minor = 0
        else:
            new_major = document.current_major_version
            new_minor = document.current_minor_version + 1

        revision_number = f"{new_major}.{new_minor}"

        # Create revision record
        db_revision = DocumentRevision(
            document_id=revision.document_id,
            revision_number=revision_number,
            major_version=new_major,
            minor_version=new_minor,
            revision_reason=revision.revision_reason,
            changes_summary=revision.changes_summary,
            change_category=revision.change_category,
            revised_by=revision.revised_by,
        )

        db.add(db_revision)

        # Update document version
        document.current_revision = revision_number
        document.current_major_version = new_major
        document.current_minor_version = new_minor
        document.status = DocumentStatus.DRAFT  # Reset to draft

        db.commit()
        db.refresh(db_revision)

        return db_revision

    @staticmethod
    def approve_document(
        db: Session, document_id: int, action: str, approver_name: str
    ) -> Optional[QMSDocument]:
        """
        Approve document through workflow: DRAFT -> PENDING_REVIEW -> PENDING_APPROVAL -> APPROVED
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            return None

        if action == "review":
            document.status = DocumentStatus.PENDING_APPROVAL
            document.reviewed_by = approver_name
            document.reviewed_at = datetime.utcnow()
        elif action == "approve":
            document.status = DocumentStatus.APPROVED
            document.approved_by = approver_name
            document.approved_at = datetime.utcnow()
            document.effective_date = datetime.utcnow()
        elif action == "reject":
            document.status = DocumentStatus.DRAFT

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def search_documents(
        db: Session,
        search_term: Optional[str] = None,
        doc_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
    ) -> List[QMSDocument]:
        """Search documents by various criteria."""
        query = db.query(QMSDocument)

        if search_term:
            search_filter = f"%{search_term}%"
            query = query.filter(
                (QMSDocument.title.ilike(search_filter))
                | (QMSDocument.doc_number.ilike(search_filter))
                | (QMSDocument.keywords.ilike(search_filter))
                | (QMSDocument.full_text_content.ilike(search_filter))
            )

        if doc_type:
            query = query.filter(QMSDocument.type == doc_type)

        if status:
            query = query.filter(QMSDocument.status == status)

        return query.all()

    @staticmethod
    def get_document(db: Session, document_id: int) -> Optional[QMSDocument]:
        """Get document by ID."""
        return db.query(QMSDocument).filter(QMSDocument.id == document_id).first()

    @staticmethod
    def get_all_documents(db: Session, skip: int = 0, limit: int = 100) -> List[QMSDocument]:
        """Get all documents with pagination."""
        return db.query(QMSDocument).offset(skip).limit(limit).all()

    @staticmethod
    def get_document_revisions(db: Session, document_id: int) -> List[DocumentRevision]:
        """Get all revisions for a document."""
        return (
            db.query(DocumentRevision)
            .filter(DocumentRevision.document_id == document_id)
            .order_by(DocumentRevision.created_at.desc())
            .all()
        )
