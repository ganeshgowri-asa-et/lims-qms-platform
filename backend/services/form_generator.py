"""
Dynamic Form Generator Service
Generates form templates from parsed template data
"""
from sqlalchemy.orm import Session
from backend.models.form import FormTemplate, FormField, FieldTypeEnum
from backend.models.form_workflow import FormValidationRule
from typing import Dict, Any, List
import shortuuid


class FormGenerator:
    """Generate form templates dynamically from parsed data"""

    def __init__(self, db: Session):
        self.db = db

    def create_form_from_template_data(
        self,
        template_data: Dict[str, Any],
        document_id: int = None,
        created_by_id: int = None
    ) -> FormTemplate:
        """
        Create FormTemplate and FormFields from parsed template data

        Args:
            template_data: Parsed template data from TemplateParser
            document_id: Link to Level 4 document
            created_by_id: User creating the template

        Returns:
            Created FormTemplate instance
        """
        # Generate unique code if not provided
        if not template_data.get('code'):
            template_data['code'] = self._generate_unique_code(template_data['name'])

        # Create form template
        form_template = FormTemplate(
            name=template_data['name'],
            code=template_data['code'],
            description=template_data.get('description'),
            category=template_data.get('category'),
            document_id=document_id,
            version=template_data.get('version', '1.0'),
            layout_config=template_data.get('layout_config'),
            is_published=False,
            created_by_id=created_by_id
        )

        self.db.add(form_template)
        self.db.flush()

        # Create form fields
        for field_data in template_data.get('fields', []):
            self._create_form_field(form_template.id, field_data, created_by_id)

        self.db.commit()
        self.db.refresh(form_template)

        return form_template

    def _create_form_field(
        self,
        template_id: int,
        field_data: Dict[str, Any],
        created_by_id: int = None
    ) -> FormField:
        """Create a form field"""
        # Normalize field type
        field_type = field_data.get('field_type', 'TEXT')
        if isinstance(field_type, str):
            try:
                field_type = FieldTypeEnum[field_type.upper()]
            except KeyError:
                field_type = FieldTypeEnum.TEXT

        # Create field
        field = FormField(
            template_id=template_id,
            field_name=field_data['field_name'],
            field_label=field_data['field_label'],
            field_type=field_type,
            order=field_data.get('order', 0),
            is_required=field_data.get('is_required', False),
            is_readonly=field_data.get('is_readonly', False),
            default_value=field_data.get('default_value'),
            placeholder=field_data.get('placeholder'),
            help_text=field_data.get('help_text'),
            section=field_data.get('section'),
            parent_field_id=field_data.get('parent_field_id'),
            formula=field_data.get('formula'),
            options=field_data.get('options'),
            validation_rules=field_data.get('validation_rules'),
            metadata=field_data.get('metadata'),
            created_by_id=created_by_id
        )

        self.db.add(field)
        self.db.flush()

        # Create validation rules if provided
        if field_data.get('validation_rules'):
            self._create_validation_rules(field.id, field_data['validation_rules'])

        return field

    def _create_validation_rules(self, field_id: int, rules: Dict[str, Any]):
        """Create validation rules for a field"""
        for rule_name, rule_value in rules.items():
            rule_config = {}
            error_message = ''

            if rule_name == 'min':
                rule_type = 'range'
                rule_config = {'min': rule_value}
                error_message = f'Value must be at least {rule_value}'
            elif rule_name == 'max':
                rule_type = 'range'
                rule_config = {'max': rule_value}
                error_message = f'Value must be at most {rule_value}'
            elif rule_name == 'pattern':
                rule_type = 'pattern'
                rule_config = {'pattern': rule_value}
                error_message = f'Value does not match required pattern'
            elif rule_name == 'minLength':
                rule_type = 'range'
                rule_config = {'minLength': rule_value}
                error_message = f'Minimum length is {rule_value} characters'
            elif rule_name == 'maxLength':
                rule_type = 'range'
                rule_config = {'maxLength': rule_value}
                error_message = f'Maximum length is {rule_value} characters'
            else:
                rule_type = 'custom'
                rule_config = {rule_name: rule_value}
                error_message = f'Validation failed for {rule_name}'

            validation_rule = FormValidationRule(
                field_id=field_id,
                rule_name=rule_name,
                rule_type=rule_type,
                rule_config=rule_config,
                error_message=error_message,
                is_active=True
            )
            self.db.add(validation_rule)

    def _generate_unique_code(self, name: str) -> str:
        """Generate unique code for form template"""
        # Extract initials
        words = name.split()
        initials = ''.join([w[0].upper() for w in words if w])[:4]

        # Add random suffix for uniqueness
        suffix = shortuuid.ShortUUID().random(length=4).upper()

        code = f"{initials}-{suffix}"

        # Check uniqueness
        existing = self.db.query(FormTemplate).filter(
            FormTemplate.code == code
        ).first()

        if existing:
            # Add another random suffix
            code = f"{code}-{shortuuid.ShortUUID().random(length=2).upper()}"

        return code

    def add_field_to_template(
        self,
        template_id: int,
        field_data: Dict[str, Any],
        created_by_id: int = None
    ) -> FormField:
        """Add a new field to an existing template"""
        # Get max order
        max_order = self.db.query(FormField).filter(
            FormField.template_id == template_id
        ).count()

        field_data['order'] = field_data.get('order', max_order)

        return self._create_form_field(template_id, field_data, created_by_id)

    def update_field(
        self,
        field_id: int,
        field_data: Dict[str, Any],
        updated_by_id: int = None
    ) -> FormField:
        """Update an existing field"""
        field = self.db.query(FormField).filter(FormField.id == field_id).first()
        if not field:
            raise ValueError(f"Field {field_id} not found")

        # Update allowed fields
        updatable_fields = [
            'field_label', 'is_required', 'is_readonly', 'default_value',
            'placeholder', 'help_text', 'validation_rules', 'options',
            'section', 'order', 'formula', 'metadata'
        ]

        for key in updatable_fields:
            if key in field_data:
                setattr(field, key, field_data[key])

        if updated_by_id:
            field.updated_by_id = updated_by_id

        self.db.commit()
        self.db.refresh(field)

        return field

    def publish_template(self, template_id: int) -> FormTemplate:
        """Publish a form template"""
        template = self.db.query(FormTemplate).filter(
            FormTemplate.id == template_id
        ).first()

        if not template:
            raise ValueError(f"Template {template_id} not found")

        template.is_published = True
        self.db.commit()
        self.db.refresh(template)

        return template

    def clone_template(
        self,
        template_id: int,
        new_name: str = None,
        created_by_id: int = None
    ) -> FormTemplate:
        """Clone an existing template"""
        original = self.db.query(FormTemplate).filter(
            FormTemplate.id == template_id
        ).first()

        if not original:
            raise ValueError(f"Template {template_id} not found")

        # Create new template
        new_template = FormTemplate(
            name=new_name or f"{original.name} (Copy)",
            code=self._generate_unique_code(new_name or original.name),
            description=original.description,
            category=original.category,
            document_id=original.document_id,
            version='1.0',
            layout_config=original.layout_config,
            is_published=False,
            created_by_id=created_by_id
        )

        self.db.add(new_template)
        self.db.flush()

        # Clone fields
        for field in original.fields:
            new_field = FormField(
                template_id=new_template.id,
                field_name=field.field_name,
                field_label=field.field_label,
                field_type=field.field_type,
                order=field.order,
                is_required=field.is_required,
                is_readonly=field.is_readonly,
                default_value=field.default_value,
                placeholder=field.placeholder,
                help_text=field.help_text,
                validation_rules=field.validation_rules,
                options=field.options,
                section=field.section,
                parent_field_id=field.parent_field_id,
                formula=field.formula,
                metadata=field.metadata,
                created_by_id=created_by_id
            )
            self.db.add(new_field)

        self.db.commit()
        self.db.refresh(new_template)

        return new_template
