"""
Document management service
Handles document lifecycle, version control, and approval workflows
"""
import os
import hashlib
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.document import (
    QMSDocument, DocumentRevision, DocumentDistribution,
    DocumentSignature, DocumentStatus, ApprovalRole, DocumentType
)
from app.services.document_numbering import DocumentNumbering
from app.core.config import settings


class DocumentService:
    """
    Service for managing QMS documents
    """

    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of file for integrity checking

        Args:
            file_path: Path to file

        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def create_document(
        db: Session,
        title: str,
        doc_type: DocumentType,
        owner: str,
        description: Optional[str] = None,
        department: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> QMSDocument:
        """
        Create a new document with auto-generated document number

        Args:
            db: Database session
            title: Document title
            doc_type: Document type
            owner: Document owner
            description: Optional description
            department: Optional department
            file_path: Optional file path

        Returns:
            Created document
        """
        # Generate document number
        doc_number = DocumentNumbering.generate_document_number(db, doc_type)

        # Calculate file hash if file provided
        file_hash = None
        file_size = None
        if file_path and os.path.exists(file_path):
            file_hash = DocumentService.calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path)

        # Create document
        document = QMSDocument(
            doc_number=doc_number,
            title=title,
            type=doc_type,
            owner=owner,
            description=description,
            department=department,
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            status=DocumentStatus.DRAFT,
            major_version=1,
            minor_version=0
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # Create initial revision
        DocumentService.create_revision(
            db=db,
            document_id=document.id,
            revised_by=owner,
            change_description="Initial document creation",
            file_path=file_path
        )

        return document

    @staticmethod
    def create_revision(
        db: Session,
        document_id: int,
        revised_by: str,
        change_description: str,
        change_reason: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> DocumentRevision:
        """
        Create a document revision record

        Args:
            db: Database session
            document_id: Document ID
            revised_by: User making revision
            change_description: Description of changes
            change_reason: Optional reason for changes
            file_path: Optional file path

        Returns:
            Created revision
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        revision_number = DocumentNumbering.get_next_revision_number(db, document_id)

        # Calculate file hash if file provided
        file_hash = None
        if file_path and os.path.exists(file_path):
            file_hash = DocumentService.calculate_file_hash(file_path)

        revision = DocumentRevision(
            document_id=document_id,
            major_version=document.major_version,
            minor_version=document.minor_version,
            revision_number=revision_number,
            revised_by=revised_by,
            change_description=change_description,
            change_reason=change_reason,
            file_path=file_path,
            file_hash=file_hash
        )

        db.add(revision)
        db.commit()
        db.refresh(revision)

        return revision

    @staticmethod
    def increment_version(
        db: Session,
        document_id: int,
        is_major: bool = False,
        revised_by: str = None,
        change_description: str = None
    ) -> QMSDocument:
        """
        Increment document version (major or minor)

        Args:
            db: Database session
            document_id: Document ID
            is_major: True for major version increment, False for minor
            revised_by: User making the revision
            change_description: Description of changes

        Returns:
            Updated document
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        if is_major:
            document.major_version += 1
            document.minor_version = 0
        else:
            document.minor_version += 1

        document.updated_at = datetime.now()
        document.status = DocumentStatus.DRAFT  # Reset to draft on new version

        db.commit()
        db.refresh(document)

        # Create revision record
        if revised_by and change_description:
            DocumentService.create_revision(
                db=db,
                document_id=document_id,
                revised_by=revised_by,
                change_description=change_description,
                file_path=document.file_path
            )

        return document

    @staticmethod
    def get_document_by_id(db: Session, document_id: int) -> Optional[QMSDocument]:
        """
        Get document by ID

        Args:
            db: Database session
            document_id: Document ID

        Returns:
            Document or None
        """
        return db.query(QMSDocument).filter(QMSDocument.id == document_id).first()

    @staticmethod
    def get_document_by_number(db: Session, doc_number: str) -> Optional[QMSDocument]:
        """
        Get document by document number

        Args:
            db: Database session
            doc_number: Document number

        Returns:
            Document or None
        """
        return db.query(QMSDocument).filter(QMSDocument.doc_number == doc_number).first()

    @staticmethod
    def list_documents(
        db: Session,
        status: Optional[DocumentStatus] = None,
        doc_type: Optional[DocumentType] = None,
        owner: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[QMSDocument]:
        """
        List documents with optional filters

        Args:
            db: Database session
            status: Optional status filter
            doc_type: Optional type filter
            owner: Optional owner filter
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of documents
        """
        query = db.query(QMSDocument)

        if status:
            query = query.filter(QMSDocument.status == status)
        if doc_type:
            query = query.filter(QMSDocument.type == doc_type)
        if owner:
            query = query.filter(QMSDocument.owner == owner)

        return query.order_by(QMSDocument.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def add_signature(
        db: Session,
        document_id: int,
        role: ApprovalRole,
        signer: str,
        signer_email: str,
        signature_hash: str,
        comments: Optional[str] = None,
        is_approved: bool = True,
        ip_address: Optional[str] = None
    ) -> DocumentSignature:
        """
        Add digital signature to document

        Args:
            db: Database session
            document_id: Document ID
            role: Approval role (DOER, CHECKER, APPROVER)
            signer: Name of signer
            signer_email: Email of signer
            signature_hash: Digital signature hash
            comments: Optional comments
            is_approved: Whether signature represents approval
            ip_address: Optional IP address

        Returns:
            Created signature
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Determine sequence based on role
        sequence_map = {
            ApprovalRole.DOER: 1,
            ApprovalRole.CHECKER: 2,
            ApprovalRole.APPROVER: 3
        }

        signature = DocumentSignature(
            document_id=document_id,
            role=role,
            signer=signer,
            signer_email=signer_email,
            signature_hash=signature_hash,
            major_version=document.major_version,
            minor_version=document.minor_version,
            sequence=sequence_map.get(role, 1),
            comments=comments,
            is_approved=is_approved,
            ip_address=ip_address
        )

        db.add(signature)
        db.commit()
        db.refresh(signature)

        # Update document status based on approval workflow
        DocumentService.update_approval_status(db, document_id)

        return signature

    @staticmethod
    def update_approval_status(db: Session, document_id: int):
        """
        Update document status based on approval signatures

        Args:
            db: Database session
            document_id: Document ID
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            return

        # Get signatures for current version
        signatures = db.query(DocumentSignature).filter(
            and_(
                DocumentSignature.document_id == document_id,
                DocumentSignature.major_version == document.major_version,
                DocumentSignature.minor_version == document.minor_version,
                DocumentSignature.is_approved == True
            )
        ).all()

        # Check approval workflow completion
        has_doer = any(s.role == ApprovalRole.DOER for s in signatures)
        has_checker = any(s.role == ApprovalRole.CHECKER for s in signatures)
        has_approver = any(s.role == ApprovalRole.APPROVER for s in signatures)

        if document.status == DocumentStatus.DRAFT and has_doer:
            document.status = DocumentStatus.PENDING_REVIEW

        if document.status == DocumentStatus.PENDING_REVIEW and has_checker:
            document.status = DocumentStatus.PENDING_APPROVAL

        if document.status == DocumentStatus.PENDING_APPROVAL and has_approver:
            document.status = DocumentStatus.APPROVED
            document.effective_date = datetime.now()

        db.commit()

    @staticmethod
    def distribute_document(
        db: Session,
        document_id: int,
        recipient: str,
        recipient_email: Optional[str] = None,
        department: Optional[str] = None,
        location: Optional[str] = None,
        distributed_by: Optional[str] = None,
        is_controlled: bool = True
    ) -> DocumentDistribution:
        """
        Distribute controlled copy of document

        Args:
            db: Database session
            document_id: Document ID
            recipient: Recipient name
            recipient_email: Optional email
            department: Optional department
            location: Optional location
            distributed_by: Optional distributor name
            is_controlled: Whether this is a controlled copy

        Returns:
            Created distribution record
        """
        document = db.query(QMSDocument).filter(QMSDocument.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Generate copy number
        existing_copies = db.query(DocumentDistribution).filter(
            DocumentDistribution.document_id == document_id
        ).count()
        copy_number = f"COPY-{existing_copies + 1:03d}"

        distribution = DocumentDistribution(
            document_id=document_id,
            copy_number=copy_number,
            recipient=recipient,
            recipient_email=recipient_email,
            department=department,
            location=location,
            distributed_by=distributed_by,
            is_controlled=is_controlled,
            version_distributed=document.version_string
        )

        db.add(distribution)
        db.commit()
        db.refresh(distribution)

        return distribution
