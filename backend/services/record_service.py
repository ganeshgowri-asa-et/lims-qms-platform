"""
Record Service - Level 5 record generation and management
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import (
    FormTemplate, FormField, FormRecord, FormValue, FormDraft,
    RecordStatusEnum, TraceabilityLink, AuditLog, User
)
import uuid


class RecordService:
    """Service for managing form records (Level 5)"""

    def __init__(self, db: Session):
        self.db = db

    def generate_record_number(self, template_id: int) -> str:
        """Generate unique record number"""
        template = self.db.query(FormTemplate).filter_by(id=template_id).first()
        if not template:
            raise ValueError("Template not found")

        # Count existing records for this template
        count = self.db.query(FormRecord).filter_by(template_id=template_id).count()

        # Format: TEMPLATE_CODE-YYYYMMDD-NNNN
        date_str = datetime.utcnow().strftime("%Y%m%d")
        record_number = f"{template.code}-{date_str}-{count + 1:04d}"

        # Ensure uniqueness
        while self.db.query(FormRecord).filter_by(record_number=record_number).first():
            count += 1
            record_number = f"{template.code}-{date_str}-{count + 1:04d}"

        return record_number

    def create_record(
        self,
        template_id: int,
        user_id: int,
        values: Dict[str, Any],
        title: Optional[str] = None,
        metadata: Optional[Dict] = None,
        auto_submit: bool = False
    ) -> FormRecord:
        """Create new form record"""
        # Generate record number
        record_number = self.generate_record_number(template_id)

        # Create record
        record = FormRecord(
            template_id=template_id,
            record_number=record_number,
            title=title,
            status=RecordStatusEnum.DRAFT,
            doer_id=user_id,
            metadata=metadata or {},
            last_modified_at=datetime.utcnow().isoformat()
        )
        self.db.add(record)
        self.db.flush()  # Get record.id

        # Save field values
        self._save_field_values(record.id, template_id, values)

        # Calculate completion and validation scores
        from .validation_service import ValidationService
        val_service = ValidationService(self.db)

        record.completion_percentage = val_service.calculate_completion_percentage(template_id, values)
        is_valid, errors, warnings = val_service.validate_record(template_id, values, record.id)
        record.validation_score = val_service.calculate_validation_score(errors, warnings)

        # Create traceability link to document if template is linked
        template = self.db.query(FormTemplate).filter_by(id=template_id).first()
        if template and template.document_id:
            link = TraceabilityLink(
                source_entity_type="FormRecord",
                source_entity_id=record.id,
                target_entity_type="Document",
                target_entity_id=template.document_id,
                link_type="derived_from",
                description=f"Record generated from template: {template.name}"
            )
            self.db.add(link)

        # Create audit log
        self._create_audit_log(
            user_id=user_id,
            entity_type="FormRecord",
            entity_id=record.id,
            action="CREATE",
            description=f"Created form record {record_number}",
            new_values={"values": values}
        )

        self.db.commit()

        return record

    def update_record(
        self,
        record_id: int,
        user_id: int,
        values: Dict[str, Any],
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> FormRecord:
        """Update existing form record"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            raise ValueError("Record not found")

        # Only allow updates to draft or revision required records
        if record.status not in [RecordStatusEnum.DRAFT, RecordStatusEnum.REVISION_REQUIRED]:
            raise ValueError(f"Cannot update record with status: {record.status.value}")

        # Get old values for audit
        old_values = self._get_record_values(record_id)

        # Update title and metadata
        if title:
            record.title = title
        if metadata:
            record.metadata = {**record.metadata, **metadata} if record.metadata else metadata

        record.last_modified_at = datetime.utcnow().isoformat()

        # Update field values
        self._save_field_values(record.id, record.template_id, values)

        # Recalculate completion and validation scores
        from .validation_service import ValidationService
        val_service = ValidationService(self.db)

        record.completion_percentage = val_service.calculate_completion_percentage(
            record.template_id,
            values
        )
        is_valid, errors, warnings = val_service.validate_record(
            record.template_id,
            values,
            record.id
        )
        record.validation_score = val_service.calculate_validation_score(errors, warnings)

        # Create audit log
        self._create_audit_log(
            user_id=user_id,
            entity_type="FormRecord",
            entity_id=record.id,
            action="UPDATE",
            description=f"Updated form record {record.record_number}",
            old_values={"values": old_values},
            new_values={"values": values}
        )

        self.db.commit()

        return record

    def get_record(self, record_id: int, include_values: bool = True) -> Dict:
        """Get record with all details"""
        record = self.db.query(FormRecord).filter_by(id=record_id).first()
        if not record:
            raise ValueError("Record not found")

        template = self.db.query(FormTemplate).filter_by(id=record.template_id).first()

        result = {
            "id": record.id,
            "record_number": record.record_number,
            "title": record.title,
            "status": record.status.value,
            "template": {
                "id": template.id,
                "name": template.name,
                "code": template.code
            } if template else None,
            "doer": self._get_user_info(record.doer_id),
            "checker": self._get_user_info(record.checker_id),
            "approver": self._get_user_info(record.approver_id),
            "submitted_at": record.submitted_at,
            "checked_at": record.checked_at,
            "approved_at": record.approved_at,
            "rejected_at": record.rejected_at,
            "rejection_reason": record.rejection_reason,
            "checker_comments": record.checker_comments,
            "approver_comments": record.approver_comments,
            "revision_number": record.revision_number,
            "completion_percentage": record.completion_percentage,
            "validation_score": record.validation_score,
            "metadata": record.metadata,
            "attachments": record.attachments,
            "tags": record.tags,
            "due_date": record.due_date,
            "last_modified_at": record.last_modified_at,
            "created_at": record.created_at,
            "created_by": self._get_user_info(record.created_by_id)
        }

        if include_values:
            result["values"] = self._get_record_values(record_id)

        return result

    def save_draft(
        self,
        template_id: int,
        user_id: int,
        values: Dict[str, Any],
        record_id: Optional[int] = None
    ) -> FormDraft:
        """Auto-save draft"""
        # Check if draft already exists
        draft = self.db.query(FormDraft).filter_by(
            template_id=template_id,
            user_id=user_id,
            record_id=record_id
        ).first()

        if draft:
            # Update existing draft
            draft.draft_data = values
            draft.last_saved_at = datetime.utcnow().isoformat()
        else:
            # Create new draft
            draft = FormDraft(
                template_id=template_id,
                user_id=user_id,
                record_id=record_id,
                draft_data=values,
                last_saved_at=datetime.utcnow().isoformat()
            )
            self.db.add(draft)

        self.db.commit()
        return draft

    def get_draft(
        self,
        template_id: int,
        user_id: int,
        record_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Get saved draft"""
        draft = self.db.query(FormDraft).filter_by(
            template_id=template_id,
            user_id=user_id,
            record_id=record_id
        ).first()

        if draft:
            return {
                "id": draft.id,
                "draft_data": draft.draft_data,
                "last_saved_at": draft.last_saved_at
            }

        return None

    def delete_draft(
        self,
        draft_id: int,
        user_id: int
    ) -> bool:
        """Delete draft"""
        draft = self.db.query(FormDraft).filter_by(
            id=draft_id,
            user_id=user_id
        ).first()

        if draft:
            self.db.delete(draft)
            self.db.commit()
            return True

        return False

    def link_to_parent(
        self,
        record_id: int,
        parent_type: str,
        parent_id: int,
        link_type: str = "related"
    ) -> TraceabilityLink:
        """Create traceability link to parent entity"""
        link = TraceabilityLink(
            source_entity_type="FormRecord",
            source_entity_id=record_id,
            target_entity_type=parent_type,
            target_entity_id=parent_id,
            link_type=link_type
        )
        self.db.add(link)
        self.db.commit()
        return link

    def get_record_links(self, record_id: int) -> List[Dict]:
        """Get all traceability links for a record"""
        links = self.db.query(TraceabilityLink).filter(
            ((TraceabilityLink.source_entity_type == "FormRecord") &
             (TraceabilityLink.source_entity_id == record_id)) |
            ((TraceabilityLink.target_entity_type == "FormRecord") &
             (TraceabilityLink.target_entity_id == record_id))
        ).all()

        result = []
        for link in links:
            result.append({
                "id": link.id,
                "source_type": link.source_entity_type,
                "source_id": link.source_entity_id,
                "target_type": link.target_entity_type,
                "target_id": link.target_entity_id,
                "link_type": link.link_type,
                "description": link.description,
                "created_at": link.created_at
            })

        return result

    def _save_field_values(
        self,
        record_id: int,
        template_id: int,
        values: Dict[str, Any]
    ) -> None:
        """Save or update field values"""
        # Delete existing values
        self.db.query(FormValue).filter_by(record_id=record_id).delete()

        # Get field definitions
        fields = {f.field_name: f for f in
                 self.db.query(FormField).filter_by(template_id=template_id).all()}

        # Save new values
        for field_name, value in values.items():
            field = fields.get(field_name)

            # Handle complex types (tables, arrays)
            if isinstance(value, (dict, list)):
                field_value = FormValue(
                    record_id=record_id,
                    field_id=field.id if field else None,
                    field_name=field_name,
                    value_json=value
                )
            else:
                field_value = FormValue(
                    record_id=record_id,
                    field_id=field.id if field else None,
                    field_name=field_name,
                    value=str(value) if value is not None else None,
                    value_json=None
                )

            self.db.add(field_value)

    def _get_record_values(self, record_id: int) -> Dict[str, Any]:
        """Get all field values for a record"""
        values = self.db.query(FormValue).filter_by(record_id=record_id).all()

        result = {}
        for value in values:
            if value.value_json is not None:
                result[value.field_name] = value.value_json
            else:
                result[value.field_name] = value.value

        return result

    def _get_user_info(self, user_id: Optional[int]) -> Optional[Dict]:
        """Get user info for response"""
        if not user_id:
            return None

        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            return None

        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email
        }

    def _create_audit_log(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        description: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None
    ) -> None:
        """Create audit log entry"""
        log = AuditLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            description=description,
            old_values=old_values,
            new_values=new_values
        )
        self.db.add(log)
