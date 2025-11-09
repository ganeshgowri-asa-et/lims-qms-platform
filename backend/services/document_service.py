"""
Document Management Service
Business logic for document and template management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import hashlib
import os
from pathlib import Path

from backend.models.document import (
    Document, DocumentVersion, DocumentLevel, DocumentLink,
    DocumentTableOfContents, DocumentResponsibility, DocumentEquipment,
    DocumentKPI, DocumentFlowchart, TemplateCategory, DocumentNumberingSequence,
    DocumentLevelEnum, DocumentStatusEnum, DocumentTypeEnum, ISOStandardEnum,
    RetentionPolicyEnum
)


class DocumentNumberingService:
    """Service for generating document numbers"""

    @staticmethod
    def generate_document_number(
        db: Session,
        level: DocumentLevelEnum,
        document_type: Optional[DocumentTypeEnum] = None,
        department: Optional[str] = None,
        custom_prefix: Optional[str] = None
    ) -> str:
        """
        Generate unique document number based on level, type, and year
        Format: {prefix}-{year}-{sequence:04d}
        Example: QM-2025-0001, PROC-2025-0015, FORM-2025-0123
        """
        current_year = datetime.now().year

        # Determine prefix
        if custom_prefix:
            prefix = custom_prefix
        elif document_type:
            prefix_map = {
                DocumentTypeEnum.QUALITY_MANUAL: "QM",
                DocumentTypeEnum.POLICY: "POL",
                DocumentTypeEnum.PROCEDURE: "PROC",
                DocumentTypeEnum.WORK_INSTRUCTION: "WI",
                DocumentTypeEnum.FORM: "FORM",
                DocumentTypeEnum.TEMPLATE: "TMPL",
                DocumentTypeEnum.CHECKLIST: "CHK",
                DocumentTypeEnum.TEST_PROTOCOL: "TP",
                DocumentTypeEnum.RECORD: "REC",
                DocumentTypeEnum.SPECIFICATION: "SPEC",
                DocumentTypeEnum.REPORT: "RPT",
                DocumentTypeEnum.FLOWCHART: "FC",
            }
            prefix = prefix_map.get(document_type, "DOC")
        else:
            # Use level-based prefix
            level_map = {
                DocumentLevelEnum.LEVEL_1: "L1",
                DocumentLevelEnum.LEVEL_2: "L2",
                DocumentLevelEnum.LEVEL_3: "L3",
                DocumentLevelEnum.LEVEL_4: "L4",
                DocumentLevelEnum.LEVEL_5: "L5",
            }
            prefix = level_map.get(level, "DOC")

        # Get or create numbering sequence
        sequence_record = db.query(DocumentNumberingSequence).filter(
            and_(
                DocumentNumberingSequence.level == level,
                DocumentNumberingSequence.year == current_year,
                DocumentNumberingSequence.is_deleted == False
            )
        ).first()

        if document_type and sequence_record:
            sequence_record = db.query(DocumentNumberingSequence).filter(
                and_(
                    DocumentNumberingSequence.level == level,
                    DocumentNumberingSequence.document_type == document_type,
                    DocumentNumberingSequence.year == current_year,
                    DocumentNumberingSequence.is_deleted == False
                )
            ).first()

        if not sequence_record:
            sequence_record = DocumentNumberingSequence(
                level=level,
                document_type=document_type,
                year=current_year,
                department=department,
                current_sequence=0,
                prefix=prefix,
                format_template=f"{{prefix}}-{{year}}-{{seq:04d}}"
            )
            db.add(sequence_record)
            db.flush()

        # Increment sequence
        sequence_record.current_sequence += 1
        sequence_number = sequence_record.current_sequence

        # Generate document number
        document_number = f"{prefix}-{current_year}-{sequence_number:04d}"

        # Update sequence metadata
        sequence_record.last_generated_number = document_number
        sequence_record.last_generated_at = datetime.now().isoformat()

        db.commit()
        db.refresh(sequence_record)

        return document_number

    @staticmethod
    def validate_document_number(db: Session, document_number: str) -> bool:
        """Check if document number is unique"""
        exists = db.query(Document).filter(
            and_(
                Document.document_number == document_number,
                Document.is_deleted == False
            )
        ).first()
        return exists is None


class DocumentVersionService:
    """Service for managing document versions"""

    @staticmethod
    def create_version(
        db: Session,
        document_id: int,
        file_path: str,
        change_summary: str,
        change_type: str = "Minor",
        change_reason: Optional[str] = None,
        released_by_id: Optional[int] = None
    ) -> DocumentVersion:
        """Create a new document version"""

        # Get current version
        latest_version = db.query(DocumentVersion).filter(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.is_deleted == False
            )
        ).order_by(DocumentVersion.revision_number.desc()).first()

        # Calculate new version number
        if latest_version:
            # Mark previous version as not current
            db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).update({"is_current": False})

            revision_number = latest_version.revision_number + 1

            # Determine version number based on change type
            if change_type == "Major":
                # Increment major version (e.g., 1.0 -> 2.0)
                major = int(float(latest_version.version_number))
                version_number = f"{major + 1}.0"
            else:
                # Increment minor version (e.g., 1.0 -> 1.1)
                parts = latest_version.version_number.split('.')
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                version_number = f"{major}.{minor + 1}"
        else:
            revision_number = 1
            version_number = "1.0"

        # Calculate file size and checksum
        file_size = None
        checksum = None
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            checksum = DocumentVersionService.calculate_checksum(file_path)

        # Get document for retention policy
        document = db.query(Document).filter(Document.id == document_id).first()
        retention_until = DocumentVersionService.calculate_retention_date(
            document.retention_policy if document else RetentionPolicyEnum.PERMANENT
        )

        # Create new version
        new_version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            revision_number=revision_number,
            change_summary=change_summary,
            change_type=change_type,
            change_reason=change_reason,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            released_by_id=released_by_id,
            released_at=datetime.now().isoformat(),
            effective_date=date.today(),
            retention_until=retention_until,
            is_current=True,
            is_obsolete=False
        )

        db.add(new_version)
        db.commit()
        db.refresh(new_version)

        # Update document's current version
        if document:
            document.current_version_id = new_version.id
            db.commit()

        return new_version

    @staticmethod
    def calculate_checksum(file_path: str) -> str:
        """Calculate SHA-256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def calculate_retention_date(retention_policy: RetentionPolicyEnum) -> Optional[date]:
        """Calculate retention end date based on policy"""
        if retention_policy == RetentionPolicyEnum.PERMANENT:
            return None
        elif retention_policy == RetentionPolicyEnum.SEVEN_YEARS:
            return date.today() + timedelta(days=365*7)
        elif retention_policy == RetentionPolicyEnum.FIVE_YEARS:
            return date.today() + timedelta(days=365*5)
        elif retention_policy == RetentionPolicyEnum.THREE_YEARS:
            return date.today() + timedelta(days=365*3)
        elif retention_policy == RetentionPolicyEnum.ONE_YEAR:
            return date.today() + timedelta(days=365)
        else:
            return None


class DocumentLinkingService:
    """Service for managing document relationships and traceability"""

    @staticmethod
    def create_link(
        db: Session,
        parent_document_id: int,
        child_document_id: int,
        link_type: str = "references",
        description: Optional[str] = None,
        section_reference: Optional[str] = None,
        compliance_reference: Optional[str] = None
    ) -> DocumentLink:
        """Create bidirectional link between documents"""

        # Check if link already exists
        existing_link = db.query(DocumentLink).filter(
            and_(
                DocumentLink.parent_document_id == parent_document_id,
                DocumentLink.child_document_id == child_document_id,
                DocumentLink.is_deleted == False
            )
        ).first()

        if existing_link:
            return existing_link

        # Create new link
        link = DocumentLink(
            parent_document_id=parent_document_id,
            child_document_id=child_document_id,
            link_type=link_type,
            description=description,
            section_reference=section_reference,
            compliance_reference=compliance_reference,
            traceability_level="direct"
        )

        db.add(link)
        db.commit()
        db.refresh(link)

        return link

    @staticmethod
    def get_document_hierarchy(
        db: Session,
        document_id: int,
        direction: str = "both"  # "up", "down", "both"
    ) -> Dict[str, Any]:
        """Get document hierarchy (upside-down and downside-up traceability)"""

        result = {
            "document_id": document_id,
            "parent_documents": [],
            "child_documents": []
        }

        if direction in ["up", "both"]:
            # Get parent documents (upside-down traceability)
            parent_links = db.query(DocumentLink).filter(
                and_(
                    DocumentLink.child_document_id == document_id,
                    DocumentLink.is_deleted == False
                )
            ).all()

            for link in parent_links:
                parent_doc = db.query(Document).filter(
                    Document.id == link.parent_document_id
                ).first()
                if parent_doc:
                    result["parent_documents"].append({
                        "id": parent_doc.id,
                        "document_number": parent_doc.document_number,
                        "title": parent_doc.title,
                        "level": parent_doc.level,
                        "link_type": link.link_type,
                        "section_reference": link.section_reference
                    })

        if direction in ["down", "both"]:
            # Get child documents (downside-up traceability)
            child_links = db.query(DocumentLink).filter(
                and_(
                    DocumentLink.parent_document_id == document_id,
                    DocumentLink.is_deleted == False
                )
            ).all()

            for link in child_links:
                child_doc = db.query(Document).filter(
                    Document.id == link.child_document_id
                ).first()
                if child_doc:
                    result["child_documents"].append({
                        "id": child_doc.id,
                        "document_number": child_doc.document_number,
                        "title": child_doc.title,
                        "level": child_doc.level,
                        "link_type": link.link_type,
                        "section_reference": link.section_reference
                    })

        return result


class DocumentLifecycleService:
    """Service for managing document lifecycle"""

    @staticmethod
    def submit_for_review(db: Session, document_id: int, checker_id: int) -> Document:
        """Submit document for review"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatusEnum.IN_REVIEW
        document.checker_id = checker_id
        document.reviewed_at = None  # Reset review timestamp

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def approve_document(
        db: Session,
        document_id: int,
        approver_id: int,
        effective_date: Optional[date] = None
    ) -> Document:
        """Approve document and set it as active"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatusEnum.APPROVED
        document.approver_id = approver_id
        document.approved_at = datetime.now().isoformat()
        document.effective_date = effective_date or date.today()

        # Calculate next review date based on review frequency
        if document.review_frequency_months:
            document.next_review_date = date.today() + timedelta(
                days=document.review_frequency_months * 30
            )

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def mark_obsolete(db: Session, document_id: int, reason: str) -> Document:
        """Mark document as obsolete"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatusEnum.OBSOLETE
        document.is_active = False

        # Mark all versions as obsolete
        db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).update({"is_obsolete": True})

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def archive_document(db: Session, document_id: int) -> Document:
        """Archive document"""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        document.status = DocumentStatusEnum.ARCHIVED
        document.is_active = False

        db.commit()
        db.refresh(document)
        return document


class TemplateIndexingService:
    """Service for indexing and categorizing templates"""

    @staticmethod
    def index_template(
        db: Session,
        document_id: int,
        category_name: str,
        tags: List[str],
        keywords: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Index a template document with categorization and searchable metadata"""

        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError("Document not found")

        # Get or create template category
        category = db.query(TemplateCategory).filter(
            and_(
                TemplateCategory.name == category_name,
                TemplateCategory.is_deleted == False
            )
        ).first()

        if not category:
            category = TemplateCategory(
                name=category_name,
                description=f"Auto-created category for {category_name}"
            )
            db.add(category)
            db.flush()

        # Update document
        document.is_template = True
        document.template_category_id = category.id
        document.tags = tags
        document.keywords = keywords
        if metadata:
            document.metadata = metadata

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def bulk_index_templates(
        db: Session,
        templates_data: List[Dict[str, Any]]
    ) -> List[Document]:
        """Bulk index multiple templates"""
        indexed_templates = []

        for template_data in templates_data:
            try:
                template = TemplateIndexingService.index_template(
                    db=db,
                    document_id=template_data["document_id"],
                    category_name=template_data["category"],
                    tags=template_data.get("tags", []),
                    keywords=template_data.get("keywords", []),
                    metadata=template_data.get("metadata")
                )
                indexed_templates.append(template)
            except Exception as e:
                # Log error and continue
                print(f"Error indexing template {template_data.get('document_id')}: {str(e)}")
                continue

        return indexed_templates

    @staticmethod
    def search_templates(
        db: Session,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        iso_standard: Optional[ISOStandardEnum] = None,
        department: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Document]:
        """Advanced search for templates"""

        filters = [
            Document.is_template == True,
            Document.is_deleted == False,
            Document.level == DocumentLevelEnum.LEVEL_4
        ]

        if category_id:
            filters.append(Document.template_category_id == category_id)

        if iso_standard:
            filters.append(Document.iso_standard == iso_standard)

        if department:
            filters.append(Document.department == department)

        if query:
            # Search in title, description, tags, keywords
            search_filter = or_(
                Document.title.ilike(f"%{query}%"),
                Document.description.ilike(f"%{query}%"),
                Document.document_number.ilike(f"%{query}%")
            )
            filters.append(search_filter)

        templates = db.query(Document).filter(and_(*filters)).all()

        # Filter by tags if provided
        if tags:
            templates = [
                t for t in templates
                if t.tags and any(tag in t.tags for tag in tags)
            ]

        return templates
