"""
Main Document Service
Integrates all document management services and provides unified interface
"""
from typing import List, Optional, Dict, BinaryIO
from sqlalchemy.orm import Session
from datetime import datetime
from backend.models.document import (
    Document,
    DocumentMetadata,
    DocumentVersion,
    DocumentLevelEnum,
    DocumentTypeEnum,
    DocumentStatusEnum,
    DocumentAuditLog
)
from backend.models.user import User
from .file_storage_service import FileStorageService
from .numbering_service import NumberingService
from .workflow_service import WorkflowService
from .linking_service import LinkingService
from .template_service import TemplateService
from .access_control_service import AccessControlService
from .retention_service import RetentionService


class DocumentService:
    """Main service for document management operations"""

    def __init__(self, db: Session):
        self.db = db
        self.file_storage = FileStorageService()
        self.numbering = NumberingService(db)
        self.workflow = WorkflowService(db)
        self.linking = LinkingService(db)
        self.template = TemplateService(db)
        self.access_control = AccessControlService(db)
        self.retention = RetentionService(db)

    def create_document(
        self,
        title: str,
        level: DocumentLevelEnum,
        created_by_id: int,
        document_type: Optional[DocumentTypeEnum] = None,
        category: Optional[str] = None,
        standard: Optional[str] = None,
        department: Optional[str] = None,
        description: Optional[str] = None,
        purpose: Optional[str] = None,
        scope: Optional[str] = None,
        parent_document_id: Optional[int] = None,
        is_template: bool = False,
        template_document_id: Optional[int] = None,
        document_owner_id: Optional[int] = None,
        manual_number: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Create a new document

        Args:
            title: Document title
            level: Document level (1-5)
            created_by_id: User creating the document
            document_type: Type of document
            category: Document category
            standard: Applicable standard
            department: Owning department
            description: Document description
            purpose: Document purpose
            scope: Document scope
            parent_document_id: Parent document (for hierarchy)
            is_template: Whether this is a template
            template_document_id: Template used to create this document
            document_owner_id: Document owner
            manual_number: Manual document number (optional)
            tags: Document tags
            keywords: Search keywords
            metadata: Additional metadata

        Returns:
            Created document information
        """
        # Generate document number
        document_number = self.numbering.generate_document_number(
            level=level,
            category=category,
            manual_number=manual_number
        )

        # Create document
        document = Document(
            document_number=document_number,
            title=title,
            level=level,
            document_type=document_type,
            category=category,
            standard=standard,
            department=department,
            description=description,
            purpose=purpose,
            scope=scope,
            parent_document_id=parent_document_id,
            is_template=is_template,
            template_document_id=template_document_id,
            document_owner_id=document_owner_id or created_by_id,
            tags=tags,
            keywords=keywords,
            metadata=metadata,
            status=DocumentStatusEnum.DRAFT,
            version="1.0",
            revision_number=0,
            created_by_id=created_by_id
        )

        self.db.add(document)
        self.db.flush()  # Get document ID without committing

        # Create metadata record
        doc_metadata = DocumentMetadata(
            document_id=document.id
        )
        self.db.add(doc_metadata)

        # Apply retention policy
        self.retention.apply_retention_policy(document.id, created_by_id)

        # If created from template, link to template
        if template_document_id:
            self.linking.create_link(
                source_document_id=document.id,
                target_document_id=template_document_id,
                link_type="implements",
                description="Created from template",
                user_id=created_by_id
            )

        # Create audit log
        self._create_audit_log(
            document_id=document.id,
            user_id=created_by_id,
            action="document_created",
            notes=f"Document created: {document_number}"
        )

        self.db.commit()
        self.db.refresh(document)

        return {
            'status': 'success',
            'message': 'Document created successfully',
            'document': self._document_to_dict(document)
        }

    def upload_document_file(
        self,
        document_id: int,
        file_stream: BinaryIO,
        filename: str,
        user_id: int
    ) -> dict:
        """
        Upload file for a document

        Args:
            document_id: Document ID
            file_stream: File stream to upload
            filename: Original filename
            user_id: User uploading file

        Returns:
            Upload result
        """
        document = self._get_document(document_id)

        # Save file
        file_info = self.file_storage.save_file(
            file_stream=file_stream,
            level=document.level.value,
            document_number=document.document_number,
            version=document.version,
            original_filename=filename,
            is_template=document.is_template
        )

        # Update document
        document.file_path = file_info['file_path']
        document.file_type = file_info['file_type']
        document.file_size = file_info['file_size']
        document.checksum = file_info['checksum']

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action="file_uploaded",
            notes=f"File uploaded: {filename}"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'File uploaded successfully',
            'file_info': file_info
        }

    def update_document(
        self,
        document_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        purpose: Optional[str] = None,
        scope: Optional[str] = None,
        category: Optional[str] = None,
        standard: Optional[str] = None,
        department: Optional[str] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """Update document fields"""
        document = self._get_document(document_id)

        # Check permission
        if not self.access_control.check_permission(document_id, user_id, 'edit'):
            raise PermissionError("User does not have edit permission for this document")

        # Track changes
        changes = []

        if title and title != document.title:
            changes.append(f"Title: {document.title} → {title}")
            document.title = title

        if description and description != document.description:
            document.description = description
            changes.append("Description updated")

        if purpose and purpose != document.purpose:
            document.purpose = purpose
            changes.append("Purpose updated")

        if scope and scope != document.scope:
            document.scope = scope
            changes.append("Scope updated")

        if category and category != document.category:
            changes.append(f"Category: {document.category} → {category}")
            document.category = category

        if standard and standard != document.standard:
            changes.append(f"Standard: {document.standard} → {standard}")
            document.standard = standard

        if department and department != document.department:
            document.department = department
            changes.append("Department updated")

        if tags:
            document.tags = tags
            changes.append("Tags updated")

        if keywords:
            document.keywords = keywords
            changes.append("Keywords updated")

        if metadata:
            document.metadata = {**(document.metadata or {}), **metadata}
            changes.append("Metadata updated")

        if changes:
            # Create audit log
            self._create_audit_log(
                document_id=document_id,
                user_id=user_id,
                action="document_updated",
                notes="; ".join(changes)
            )

            self.db.commit()

        return {
            'status': 'success',
            'message': 'Document updated successfully',
            'changes': changes
        }

    def update_document_metadata(
        self,
        document_id: int,
        user_id: int,
        table_of_contents: Optional[List[dict]] = None,
        responsibilities: Optional[List[dict]] = None,
        equipment_required: Optional[List[dict]] = None,
        software_required: Optional[List[dict]] = None,
        resources_required: Optional[List[dict]] = None,
        process_flowchart: Optional[str] = None,
        value_stream_map: Optional[str] = None,
        turtle_diagram: Optional[str] = None,
        infographics: Optional[List[dict]] = None,
        kpi_definitions: Optional[List[dict]] = None,
        measurement_frequency: Optional[str] = None,
        annexures: Optional[List[dict]] = None,
        references: Optional[List[dict]] = None,
        risk_assessment: Optional[List[dict]] = None,
        process_analysis: Optional[str] = None,
        nc_control_procedure: Optional[str] = None,
        nc_escalation_matrix: Optional[List[dict]] = None,
        training_required: Optional[List[dict]] = None,
        safety_requirements: Optional[List[dict]] = None,
        compliance_checklist: Optional[List[dict]] = None,
        custom_fields: Optional[dict] = None
    ) -> dict:
        """
        Update extended document metadata

        Args:
            document_id: Document ID
            user_id: User updating metadata
            (various metadata fields)

        Returns:
            Update result
        """
        document = self._get_document(document_id)

        # Check permission
        if not self.access_control.check_permission(document_id, user_id, 'edit'):
            raise PermissionError("User does not have edit permission for this document")

        # Get or create metadata
        metadata = self.db.query(DocumentMetadata).filter(
            DocumentMetadata.document_id == document_id
        ).first()

        if not metadata:
            metadata = DocumentMetadata(document_id=document_id)
            self.db.add(metadata)

        # Update fields
        if table_of_contents is not None:
            metadata.table_of_contents = table_of_contents
        if responsibilities is not None:
            metadata.responsibilities = responsibilities
        if equipment_required is not None:
            metadata.equipment_required = equipment_required
        if software_required is not None:
            metadata.software_required = software_required
        if resources_required is not None:
            metadata.resources_required = resources_required
        if process_flowchart is not None:
            metadata.process_flowchart = process_flowchart
        if value_stream_map is not None:
            metadata.value_stream_map = value_stream_map
        if turtle_diagram is not None:
            metadata.turtle_diagram = turtle_diagram
        if infographics is not None:
            metadata.infographics = infographics
        if kpi_definitions is not None:
            metadata.kpi_definitions = kpi_definitions
        if measurement_frequency is not None:
            metadata.measurement_frequency = measurement_frequency
        if annexures is not None:
            metadata.annexures = annexures
        if references is not None:
            metadata.references = references
        if risk_assessment is not None:
            metadata.risk_assessment = risk_assessment
        if process_analysis is not None:
            metadata.process_analysis = process_analysis
        if nc_control_procedure is not None:
            metadata.nc_control_procedure = nc_control_procedure
        if nc_escalation_matrix is not None:
            metadata.nc_escalation_matrix = nc_escalation_matrix
        if training_required is not None:
            metadata.training_required = training_required
        if safety_requirements is not None:
            metadata.safety_requirements = safety_requirements
        if compliance_checklist is not None:
            metadata.compliance_checklist = compliance_checklist
        if custom_fields is not None:
            metadata.custom_fields = custom_fields

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action="metadata_updated",
            notes="Extended metadata updated"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document metadata updated successfully'
        }

    def create_new_version(
        self,
        document_id: int,
        user_id: int,
        file_stream: Optional[BinaryIO] = None,
        filename: Optional[str] = None,
        change_summary: Optional[str] = None,
        change_reason: Optional[str] = None,
        is_major_version: bool = False
    ) -> dict:
        """
        Create a new version of a document

        Args:
            document_id: Document ID
            user_id: User creating new version
            file_stream: New file (optional)
            filename: Filename (if file provided)
            change_summary: Summary of changes
            change_reason: Reason for new version
            is_major_version: Whether this is a major version (1.0 → 2.0) or minor (1.0 → 1.1)

        Returns:
            New version information
        """
        document = self._get_document(document_id)

        # Check permission
        if not self.access_control.check_permission(document_id, user_id, 'edit'):
            raise PermissionError("User does not have edit permission for this document")

        # Calculate new version number
        current_parts = document.version.split('.')
        if is_major_version:
            new_version = f"{int(current_parts[0]) + 1}.0"
        else:
            new_version = f"{current_parts[0]}.{int(current_parts[1]) + 1}"

        # Create version record for current version
        if document.file_path:
            # Archive current version
            current_version = DocumentVersion(
                document_id=document_id,
                version_number=document.version,
                revision_number=document.revision_number,
                change_summary=change_summary,
                change_reason=change_reason,
                file_path=document.file_path,
                file_size=document.file_size,
                file_type=document.file_type,
                checksum=document.checksum,
                released_by_id=user_id,
                released_at=datetime.now(),
                is_current=False
            )
            self.db.add(current_version)

        # If new file provided, save it
        if file_stream and filename:
            file_info = self.file_storage.save_file(
                file_stream=file_stream,
                level=document.level.value,
                document_number=document.document_number,
                version=new_version,
                original_filename=filename,
                is_template=document.is_template
            )

            document.file_path = file_info['file_path']
            document.file_type = file_info['file_type']
            document.file_size = file_info['file_size']
            document.checksum = file_info['checksum']

        # Update document
        document.version = new_version
        document.revision_number += 1
        document.status = DocumentStatusEnum.DRAFT  # New version goes to draft

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action="version_created",
            notes=f"New version created: {new_version}. {change_summary}"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'New version created successfully',
            'version': new_version,
            'revision': document.revision_number
        }

    def get_document(
        self,
        document_id: int,
        user_id: Optional[int] = None,
        include_metadata: bool = False,
        include_versions: bool = False,
        include_links: bool = False,
        include_approvals: bool = False
    ) -> dict:
        """
        Get document with optional related data

        Args:
            document_id: Document ID
            user_id: User requesting document (for permission check)
            include_metadata: Include extended metadata
            include_versions: Include version history
            include_links: Include document links
            include_approvals: Include approval history

        Returns:
            Document information
        """
        document = self._get_document(document_id)

        # Check permission if user provided
        if user_id and not self.access_control.check_permission(document_id, user_id, 'view'):
            raise PermissionError("User does not have view permission for this document")

        # Create audit log for viewing
        if user_id:
            self._create_audit_log(
                document_id=document_id,
                user_id=user_id,
                action="document_viewed",
                notes="Document accessed"
            )

        result = self._document_to_dict(document)

        # Add optional data
        if include_metadata:
            metadata = self.db.query(DocumentMetadata).filter(
                DocumentMetadata.document_id == document_id
            ).first()
            if metadata:
                result['metadata'] = self._metadata_to_dict(metadata)

        if include_versions:
            versions = self.db.query(DocumentVersion).filter(
                DocumentVersion.document_id == document_id
            ).order_by(DocumentVersion.version_number.desc()).all()
            result['versions'] = [self._version_to_dict(v) for v in versions]

        if include_links:
            result['links'] = self.linking.get_document_links(document_id)

        if include_approvals:
            result['approvals'] = self.workflow.get_approval_history(document_id)

        return result

    def search_documents(
        self,
        query: Optional[str] = None,
        level: Optional[DocumentLevelEnum] = None,
        document_type: Optional[DocumentTypeEnum] = None,
        status: Optional[DocumentStatusEnum] = None,
        category: Optional[str] = None,
        standard: Optional[str] = None,
        department: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> dict:
        """
        Search documents with various filters

        Args:
            query: Text search query
            level: Filter by document level
            document_type: Filter by document type
            status: Filter by status
            category: Filter by category
            standard: Filter by standard
            department: Filter by department
            tags: Filter by tags
            created_from: Filter by creation date (from)
            created_to: Filter by creation date (to)
            user_id: User performing search
            skip: Pagination offset
            limit: Page size

        Returns:
            Search results
        """
        from sqlalchemy import or_, and_

        db_query = self.db.query(Document).filter(Document.is_deleted == False)

        # Apply filters
        if query:
            db_query = db_query.filter(
                or_(
                    Document.title.ilike(f'%{query}%'),
                    Document.document_number.ilike(f'%{query}%'),
                    Document.description.ilike(f'%{query}%')
                )
            )

        if level:
            db_query = db_query.filter(Document.level == level)

        if document_type:
            db_query = db_query.filter(Document.document_type == document_type)

        if status:
            db_query = db_query.filter(Document.status == status)

        if category:
            db_query = db_query.filter(Document.category == category)

        if standard:
            db_query = db_query.filter(Document.standard == standard)

        if department:
            db_query = db_query.filter(Document.department == department)

        if created_from:
            db_query = db_query.filter(Document.created_at >= created_from)

        if created_to:
            db_query = db_query.filter(Document.created_at <= created_to)

        # Get total count
        total = db_query.count()

        # Get documents
        documents = db_query.offset(skip).limit(limit).all()

        return {
            'total': total,
            'page_size': limit,
            'offset': skip,
            'documents': [self._document_to_dict(doc) for doc in documents]
        }

    def delete_document(
        self,
        document_id: int,
        user_id: int,
        reason: Optional[str] = None,
        permanent: bool = False
    ) -> dict:
        """
        Delete a document (soft delete by default)

        Args:
            document_id: Document ID
            user_id: User deleting document
            reason: Reason for deletion
            permanent: Whether to permanently delete (admin only)

        Returns:
            Deletion result
        """
        document = self._get_document(document_id)

        # Check permission
        if not self.access_control.check_permission(document_id, user_id, 'delete'):
            raise PermissionError("User does not have delete permission for this document")

        if permanent:
            # Permanent delete (use with caution)
            self.db.delete(document)
            action = "document_permanently_deleted"
        else:
            # Soft delete
            document.is_deleted = True
            document.is_active = False
            action = "document_deleted"

        # Create audit log
        self._create_audit_log(
            document_id=document_id,
            user_id=user_id,
            action=action,
            notes=f"Reason: {reason}"
        )

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Document deleted successfully',
            'permanent': permanent
        }

    def _get_document(self, document_id: int) -> Document:
        """Get document or raise error"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return document

    def _document_to_dict(self, document: Document) -> dict:
        """Convert document to dictionary"""
        return {
            'id': document.id,
            'document_number': document.document_number,
            'title': document.title,
            'level': document.level.value,
            'document_type': document.document_type.value if document.document_type else None,
            'category': document.category,
            'standard': document.standard.value if document.standard else None,
            'department': document.department,
            'status': document.status.value,
            'version': document.version,
            'revision_number': document.revision_number,
            'description': document.description,
            'purpose': document.purpose,
            'scope': document.scope,
            'file_path': document.file_path,
            'file_type': document.file_type,
            'file_size': document.file_size,
            'is_template': document.is_template,
            'is_confidential': document.is_confidential,
            'access_level': document.access_level,
            'tags': document.tags,
            'keywords': document.keywords,
            'created_at': document.created_at.isoformat() if document.created_at else None,
            'updated_at': document.updated_at.isoformat() if document.updated_at else None,
            'effective_date': document.effective_date.isoformat() if document.effective_date else None,
            'next_review_date': document.next_review_date.isoformat() if document.next_review_date else None
        }

    def _metadata_to_dict(self, metadata: DocumentMetadata) -> dict:
        """Convert metadata to dictionary"""
        return {
            'table_of_contents': metadata.table_of_contents,
            'responsibilities': metadata.responsibilities,
            'equipment_required': metadata.equipment_required,
            'software_required': metadata.software_required,
            'resources_required': metadata.resources_required,
            'kpi_definitions': metadata.kpi_definitions,
            'measurement_frequency': metadata.measurement_frequency,
            'annexures': metadata.annexures,
            'references': metadata.references,
            'risk_assessment': metadata.risk_assessment,
            'training_required': metadata.training_required,
            'safety_requirements': metadata.safety_requirements,
            'compliance_checklist': metadata.compliance_checklist
        }

    def _version_to_dict(self, version: DocumentVersion) -> dict:
        """Convert version to dictionary"""
        return {
            'id': version.id,
            'version_number': version.version_number,
            'revision_number': version.revision_number,
            'change_summary': version.change_summary,
            'file_path': version.file_path,
            'file_size': version.file_size,
            'released_at': version.released_at.isoformat() if version.released_at else None,
            'is_current': version.is_current
        }

    def _create_audit_log(
        self,
        document_id: int,
        user_id: int,
        action: str,
        notes: Optional[str] = None
    ):
        """Create audit log entry"""
        audit = DocumentAuditLog(
            document_id=document_id,
            user_id=user_id,
            action=action,
            notes=notes
        )
        self.db.add(audit)
