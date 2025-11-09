"""
Form Data Capture Service
Orchestrates form record creation, validation, and workflow
"""
from sqlalchemy.orm import Session
from backend.models.form import FormRecord, FormValue, FormTemplate, FormField
from backend.models.form_workflow import WorkflowStatus
from backend.services.validation_engine import ValidationEngine, ValidationError
from backend.services.workflow_engine import WorkflowEngine
from backend.services.signature_service import SignatureService
from typing import Dict, Any, List, Optional
from datetime import datetime
import shortuuid


class FormDataService:
    """Service layer for form data capture and management"""

    def __init__(self, db: Session):
        self.db = db
        self.validation_engine = ValidationEngine(db)
        self.workflow_engine = WorkflowEngine(db)
        self.signature_service = SignatureService()

    def create_record(
        self,
        template_id: int,
        form_data: Dict[str, Any],
        created_by_id: int,
        title: str = None,
        auto_submit: bool = False
    ) -> FormRecord:
        """
        Create a new form record

        Args:
            template_id: ID of the form template
            form_data: Dictionary of field_name: value
            created_by_id: User creating the record
            title: Optional record title
            auto_submit: If True, automatically submit after creation

        Returns:
            Created FormRecord
        """
        # Get template
        template = self._get_template(template_id)

        # Validate form data
        validation_errors = self.validation_engine.validate_form_data(
            template_id=template_id,
            form_data=form_data
        )

        if validation_errors:
            raise ValidationError(
                field_name='_form',
                message=f"Validation failed: {validation_errors}"
            )

        # Generate unique record number
        record_number = self._generate_record_number(template)

        # Create form record
        record = FormRecord(
            template_id=template_id,
            record_number=record_number,
            title=title or f"{template.name} - {record_number}",
            status=WorkflowStatus.DRAFT.value,
            doer_id=created_by_id,
            created_by_id=created_by_id,
            metadata={
                'created_at': datetime.utcnow().isoformat(),
                'template_version': template.version
            }
        )

        self.db.add(record)
        self.db.flush()

        # Save form values
        self._save_form_values(
            record_id=record.id,
            form_data=form_data,
            template=template,
            created_by_id=created_by_id
        )

        # Auto-submit if requested
        if auto_submit:
            self.workflow_engine.submit_record(
                record_id=record.id,
                user_id=created_by_id
            )

        self.db.commit()
        self.db.refresh(record)

        return record

    def update_record(
        self,
        record_id: int,
        form_data: Dict[str, Any],
        updated_by_id: int,
        partial: bool = True
    ) -> FormRecord:
        """
        Update an existing form record

        Args:
            record_id: ID of the record to update
            form_data: Updated field values
            updated_by_id: User performing the update
            partial: If True, only update provided fields. If False, replace all values

        Returns:
            Updated FormRecord
        """
        record = self._get_record(record_id)

        # Only allow updates to draft records
        if record.status != WorkflowStatus.DRAFT.value:
            raise ValueError(f"Cannot update record in status: {record.status}")

        # Get current values if partial update
        if partial:
            current_data = self.get_record_data(record_id)
            current_data.update(form_data)
            form_data = current_data

        # Validate form data
        validation_errors = self.validation_engine.validate_form_data(
            template_id=record.template_id,
            form_data=form_data,
            record_id=record_id
        )

        if validation_errors:
            raise ValidationError(
                field_name='_form',
                message=f"Validation failed: {validation_errors}"
            )

        # Delete old values
        self.db.query(FormValue).filter(
            FormValue.record_id == record_id
        ).delete()

        # Save new values
        self._save_form_values(
            record_id=record.id,
            form_data=form_data,
            template=record.template,
            created_by_id=updated_by_id
        )

        # Update record metadata
        record.updated_by_id = updated_by_id

        self.db.commit()
        self.db.refresh(record)

        return record

    def get_record_data(self, record_id: int) -> Dict[str, Any]:
        """
        Get form data for a record

        Returns:
            Dictionary of field_name: value
        """
        record = self._get_record(record_id)

        form_data = {}
        for value in record.values:
            # Use value_json for complex values, otherwise use value
            if value.value_json is not None:
                form_data[value.field_name] = value.value_json
            else:
                form_data[value.field_name] = value.value

        return form_data

    def get_record_with_template(self, record_id: int) -> Dict[str, Any]:
        """
        Get complete record data with template definition

        Returns:
            Dictionary with record, template, and form data
        """
        record = self._get_record(record_id)
        form_data = self.get_record_data(record_id)

        # Build field definitions
        fields = []
        for field in record.template.fields:
            field_def = {
                'id': field.id,
                'field_name': field.field_name,
                'field_label': field.field_label,
                'field_type': field.field_type.value,
                'is_required': field.is_required,
                'is_readonly': field.is_readonly,
                'placeholder': field.placeholder,
                'help_text': field.help_text,
                'options': field.options,
                'default_value': field.default_value,
                'section': field.section,
                'order': field.order,
                'validation_rules': field.validation_rules,
                'value': form_data.get(field.field_name)
            }
            fields.append(field_def)

        # Sort fields by order
        fields.sort(key=lambda x: x['order'])

        return {
            'record': {
                'id': record.id,
                'record_number': record.record_number,
                'title': record.title,
                'status': record.status,
                'doer_id': record.doer_id,
                'checker_id': record.checker_id,
                'approver_id': record.approver_id,
                'submitted_at': record.submitted_at,
                'checked_at': record.checked_at,
                'approved_at': record.approved_at,
                'checker_comments': record.checker_comments,
                'approver_comments': record.approver_comments,
                'created_at': str(record.created_at),
                'updated_at': str(record.updated_at)
            },
            'template': {
                'id': record.template.id,
                'name': record.template.name,
                'code': record.template.code,
                'description': record.template.description,
                'category': record.template.category,
                'version': record.template.version
            },
            'fields': fields,
            'workflow_history': self.workflow_engine.get_workflow_history(record_id),
            'signatures': self.workflow_engine.get_signatures(record_id)
        }

    def submit_record(
        self,
        record_id: int,
        user_id: int,
        comments: str = None,
        signature_data: str = None
    ) -> FormRecord:
        """Submit a record for review"""
        # Validate before submission
        record = self._get_record(record_id)
        form_data = self.get_record_data(record_id)

        validation_errors = self.validation_engine.validate_form_data(
            template_id=record.template_id,
            form_data=form_data,
            record_id=record_id
        )

        if validation_errors:
            raise ValidationError(
                field_name='_form',
                message=f"Cannot submit: {validation_errors}"
            )

        # Submit via workflow engine
        return self.workflow_engine.submit_record(
            record_id=record_id,
            user_id=user_id,
            comments=comments,
            signature_data=signature_data
        )

    def auto_populate_fields(
        self,
        template_id: int,
        user_id: int,
        base_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Auto-populate form fields from various sources

        Args:
            template_id: ID of the template
            user_id: User requesting auto-population
            base_data: Base data to start with

        Returns:
            Dictionary of auto-populated field values
        """
        template = self._get_template(template_id)
        populated_data = base_data or {}

        # Auto-populate from default values
        for field in template.fields:
            if field.field_name not in populated_data and field.default_value:
                populated_data[field.field_name] = field.default_value

        # Auto-populate calculated fields
        for field in template.fields:
            if field.field_type.value == 'CALCULATED' and field.formula:
                calculated_value = self.validation_engine.validate_calculated_field(
                    field=field,
                    all_data=populated_data
                )
                if calculated_value is not None:
                    populated_data[field.field_name] = calculated_value

        # Auto-populate from user's previous records (last used values)
        last_record = self.db.query(FormRecord).filter(
            FormRecord.template_id == template_id,
            FormRecord.doer_id == user_id,
            FormRecord.is_deleted == False
        ).order_by(FormRecord.created_at.desc()).first()

        if last_record:
            last_data = self.get_record_data(last_record.id)
            # Only populate non-required fields from last record
            for field in template.fields:
                if (field.field_name not in populated_data and
                    field.field_name in last_data and
                    not field.is_required):
                    populated_data[field.field_name] = last_data[field.field_name]

        return populated_data

    def bulk_create_records(
        self,
        template_id: int,
        records_data: List[Dict[str, Any]],
        created_by_id: int
    ) -> List[FormRecord]:
        """
        Create multiple records in batch

        Args:
            template_id: ID of the template
            records_data: List of form data dictionaries
            created_by_id: User creating the records

        Returns:
            List of created FormRecord instances
        """
        created_records = []

        for record_data in records_data:
            try:
                record = self.create_record(
                    template_id=template_id,
                    form_data=record_data,
                    created_by_id=created_by_id
                )
                created_records.append(record)
            except Exception as e:
                # Log error but continue with other records
                print(f"Failed to create record: {e}")
                continue

        return created_records

    def _get_template(self, template_id: int) -> FormTemplate:
        """Get template by ID"""
        template = self.db.query(FormTemplate).filter(
            FormTemplate.id == template_id,
            FormTemplate.is_deleted == False
        ).first()

        if not template:
            raise ValueError(f"Template {template_id} not found")

        return template

    def _get_record(self, record_id: int) -> FormRecord:
        """Get record by ID"""
        record = self.db.query(FormRecord).filter(
            FormRecord.id == record_id,
            FormRecord.is_deleted == False
        ).first()

        if not record:
            raise ValueError(f"Record {record_id} not found")

        return record

    def _generate_record_number(self, template: FormTemplate) -> str:
        """
        Generate unique record number

        Format: {TEMPLATE_CODE}-{YEAR}-{SEQUENCE}
        Example: EQP-2024-0001
        """
        year = datetime.now().year

        # Get count of records for this template in current year
        count = self.db.query(FormRecord).filter(
            FormRecord.template_id == template.id,
            FormRecord.record_number.like(f"{template.code}-{year}-%")
        ).count()

        sequence = count + 1
        record_number = f"{template.code}-{year}-{sequence:04d}"

        # Ensure uniqueness
        while self.db.query(FormRecord).filter(
            FormRecord.record_number == record_number
        ).first():
            sequence += 1
            record_number = f"{template.code}-{year}-{sequence:04d}"

        return record_number

    def _save_form_values(
        self,
        record_id: int,
        form_data: Dict[str, Any],
        template: FormTemplate,
        created_by_id: int
    ):
        """Save form field values"""
        for field in template.fields:
            value = form_data.get(field.field_name)

            if value is not None:
                # Determine if value should be stored as JSON
                use_json = isinstance(value, (dict, list))

                form_value = FormValue(
                    record_id=record_id,
                    field_id=field.id,
                    field_name=field.field_name,
                    value=str(value) if not use_json else None,
                    value_json=value if use_json else None,
                    created_by_id=created_by_id
                )

                self.db.add(form_value)

    def delete_record(self, record_id: int, deleted_by_id: int) -> bool:
        """
        Soft delete a record

        Args:
            record_id: ID of the record to delete
            deleted_by_id: User performing the deletion

        Returns:
            True if successful
        """
        record = self._get_record(record_id)

        # Only allow deletion of draft records
        if record.status != WorkflowStatus.DRAFT.value:
            raise ValueError(f"Cannot delete record in status: {record.status}")

        record.is_deleted = True
        record.updated_by_id = deleted_by_id

        self.db.commit()

        return True

    def get_record_statistics(self, template_id: int) -> Dict[str, Any]:
        """Get statistics for records of a template"""
        from sqlalchemy import func

        stats = self.db.query(
            FormRecord.status,
            func.count(FormRecord.id).label('count')
        ).filter(
            FormRecord.template_id == template_id,
            FormRecord.is_deleted == False
        ).group_by(FormRecord.status).all()

        return {
            'template_id': template_id,
            'total_records': sum(s.count for s in stats),
            'by_status': {s.status: s.count for s in stats}
        }
