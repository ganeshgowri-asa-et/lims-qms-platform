"""
Advanced Validation Engine
Real-time validation with custom rules and cross-field validation
"""
from sqlalchemy.orm import Session
from backend.models.form import FormTemplate, FormField, FormValue, FieldTypeEnum
from backend.models.form_workflow import FormValidationRule, FormDuplicateCheck
from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from difflib import SequenceMatcher


class ValidationError(Exception):
    """Validation error exception"""
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"{field_name}: {message}")


class ValidationEngine:
    """Validate form data against field definitions and rules"""

    def __init__(self, db: Session):
        self.db = db

    def validate_form_data(
        self,
        template_id: int,
        form_data: Dict[str, Any],
        record_id: Optional[int] = None
    ) -> Dict[str, List[str]]:
        """
        Validate complete form data

        Returns:
            Dict of field_name: [error_messages]
        """
        errors = {}

        # Get template and fields
        template = self.db.query(FormTemplate).filter(
            FormTemplate.id == template_id
        ).first()

        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Validate each field
        for field in template.fields:
            field_errors = self.validate_field(
                field=field,
                value=form_data.get(field.field_name),
                all_data=form_data
            )

            if field_errors:
                errors[field.field_name] = field_errors

        # Check for duplicates
        duplicate_errors = self.check_duplicates(
            template_id=template_id,
            form_data=form_data,
            exclude_record_id=record_id
        )

        if duplicate_errors:
            if '_form' not in errors:
                errors['_form'] = []
            errors['_form'].extend(duplicate_errors)

        return errors

    def validate_field(
        self,
        field: FormField,
        value: Any,
        all_data: Dict[str, Any] = None
    ) -> List[str]:
        """
        Validate a single field

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Required field validation
        if field.is_required and (value is None or value == ''):
            errors.append(f"{field.field_label} is required")
            return errors  # Don't continue if required field is empty

        # Skip further validation if value is empty and field is not required
        if value is None or value == '':
            return errors

        # Type-specific validation
        type_errors = self._validate_field_type(field, value)
        errors.extend(type_errors)

        # Custom validation rules
        if field.validation_rules:
            rule_errors = self._validate_rules(field, value, field.validation_rules)
            errors.extend(rule_errors)

        # Database validation rules
        db_rule_errors = self._validate_db_rules(field, value, all_data)
        errors.extend(db_rule_errors)

        return errors

    def _validate_field_type(self, field: FormField, value: Any) -> List[str]:
        """Validate value matches field type"""
        errors = []

        if field.field_type == FieldTypeEnum.NUMBER:
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"{field.field_label} must be a number")

        elif field.field_type == FieldTypeEnum.DATE:
            if not self._is_valid_date(value):
                errors.append(f"{field.field_label} must be a valid date (YYYY-MM-DD)")

        elif field.field_type == FieldTypeEnum.DATETIME:
            if not self._is_valid_datetime(value):
                errors.append(f"{field.field_label} must be a valid datetime")

        elif field.field_type in [FieldTypeEnum.DROPDOWN, FieldTypeEnum.RADIO]:
            if field.options and value not in field.options:
                errors.append(f"{field.field_label} must be one of: {', '.join(field.options)}")

        elif field.field_type == FieldTypeEnum.MULTISELECT:
            if field.options:
                values = value if isinstance(value, list) else [value]
                invalid = [v for v in values if v not in field.options]
                if invalid:
                    errors.append(f"Invalid options for {field.field_label}: {', '.join(invalid)}")

        elif field.field_type == FieldTypeEnum.CHECKBOX:
            if not isinstance(value, bool) and value not in ['true', 'false', '1', '0', True, False]:
                errors.append(f"{field.field_label} must be a boolean value")

        return errors

    def _validate_rules(
        self,
        field: FormField,
        value: Any,
        rules: Dict[str, Any]
    ) -> List[str]:
        """Validate against JSON validation rules"""
        errors = []

        # Min/Max for numbers
        if 'min' in rules:
            try:
                if float(value) < float(rules['min']):
                    errors.append(f"{field.field_label} must be at least {rules['min']}")
            except (ValueError, TypeError):
                pass

        if 'max' in rules:
            try:
                if float(value) > float(rules['max']):
                    errors.append(f"{field.field_label} must be at most {rules['max']}")
            except (ValueError, TypeError):
                pass

        # Min/Max length for strings
        if 'minLength' in rules:
            if len(str(value)) < int(rules['minLength']):
                errors.append(f"{field.field_label} must be at least {rules['minLength']} characters")

        if 'maxLength' in rules:
            if len(str(value)) > int(rules['maxLength']):
                errors.append(f"{field.field_label} must be at most {rules['maxLength']} characters")

        # Pattern matching
        if 'pattern' in rules:
            if not re.match(rules['pattern'], str(value)):
                error_msg = rules.get('patternMessage', f"{field.field_label} format is invalid")
                errors.append(error_msg)

        # Custom validation function
        if 'custom' in rules:
            custom_error = self._validate_custom(field, value, rules['custom'])
            if custom_error:
                errors.append(custom_error)

        return errors

    def _validate_db_rules(
        self,
        field: FormField,
        value: Any,
        all_data: Dict[str, Any] = None
    ) -> List[str]:
        """Validate against database validation rules"""
        errors = []

        # Get validation rules from database
        db_rules = self.db.query(FormValidationRule).filter(
            FormValidationRule.field_id == field.id,
            FormValidationRule.is_active == True
        ).order_by(FormValidationRule.priority.desc()).all()

        for rule in db_rules:
            error = self._apply_validation_rule(rule, value, all_data)
            if error:
                errors.append(error)

        return errors

    def _apply_validation_rule(
        self,
        rule: FormValidationRule,
        value: Any,
        all_data: Dict[str, Any] = None
    ) -> Optional[str]:
        """Apply a single validation rule"""
        config = rule.rule_config

        if rule.rule_type == 'required':
            if value is None or value == '':
                return rule.error_message

        elif rule.rule_type == 'range':
            try:
                num_value = float(value)
                if 'min' in config and num_value < config['min']:
                    return rule.error_message
                if 'max' in config and num_value > config['max']:
                    return rule.error_message
            except (ValueError, TypeError):
                pass

        elif rule.rule_type == 'pattern':
            if not re.match(config['pattern'], str(value)):
                return rule.error_message

        elif rule.rule_type == 'cross_field':
            # Cross-field validation
            if all_data and rule.depends_on_fields:
                dependent_values = {
                    field_id: all_data.get(field_id)
                    for field_id in rule.depends_on_fields
                }
                # Apply custom cross-field logic
                if not self._validate_cross_field(value, dependent_values, config):
                    return rule.error_message

        elif rule.rule_type == 'custom':
            # Custom validation logic
            if not self._validate_custom_rule(value, config):
                return rule.error_message

        return None

    def _validate_cross_field(
        self,
        value: Any,
        dependent_values: Dict[str, Any],
        config: Dict[str, Any]
    ) -> bool:
        """Validate cross-field dependencies"""
        operator = config.get('operator', 'equals')

        if operator == 'equals':
            target_field = config.get('target_field')
            return value == dependent_values.get(target_field)

        elif operator == 'greater_than':
            target_field = config.get('target_field')
            try:
                return float(value) > float(dependent_values.get(target_field, 0))
            except (ValueError, TypeError):
                return False

        elif operator == 'less_than':
            target_field = config.get('target_field')
            try:
                return float(value) < float(dependent_values.get(target_field, float('inf')))
            except (ValueError, TypeError):
                return False

        elif operator == 'date_after':
            target_field = config.get('target_field')
            try:
                date1 = datetime.fromisoformat(str(value))
                date2 = datetime.fromisoformat(str(dependent_values.get(target_field)))
                return date1 > date2
            except (ValueError, TypeError):
                return False

        return True

    def _validate_custom(self, field: FormField, value: Any, custom_config: Any) -> Optional[str]:
        """Apply custom validation logic"""
        # Placeholder for custom validation
        # Can be extended with eval() or custom function registry
        return None

    def _validate_custom_rule(self, value: Any, config: Dict[str, Any]) -> bool:
        """Apply custom validation rule"""
        # Placeholder for custom rule logic
        return True

    def _is_valid_date(self, value: str) -> bool:
        """Check if value is a valid date"""
        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False

    def _is_valid_datetime(self, value: str) -> bool:
        """Check if value is a valid datetime"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M'
        ]

        for fmt in formats:
            try:
                datetime.strptime(str(value), fmt)
                return True
            except (ValueError, TypeError):
                continue

        return False

    def check_duplicates(
        self,
        template_id: int,
        form_data: Dict[str, Any],
        exclude_record_id: Optional[int] = None
    ) -> List[str]:
        """Check for duplicate records"""
        errors = []

        # Get duplicate check configurations
        duplicate_checks = self.db.query(FormDuplicateCheck).filter(
            FormDuplicateCheck.template_id == template_id,
            FormDuplicateCheck.is_active == True
        ).all()

        for check in duplicate_checks:
            if self._is_duplicate(check, form_data, exclude_record_id):
                error_msg = check.error_message or f"Duplicate record detected based on {', '.join(check.check_fields)}"
                errors.append(error_msg)

        return errors

    def _is_duplicate(
        self,
        check: FormDuplicateCheck,
        form_data: Dict[str, Any],
        exclude_record_id: Optional[int] = None
    ) -> bool:
        """Check if record is duplicate"""
        from backend.models.form import FormRecord

        # Get all records for this template
        query = self.db.query(FormRecord).filter(
            FormRecord.template_id == check.template_id,
            FormRecord.is_deleted == False
        )

        if exclude_record_id:
            query = query.filter(FormRecord.id != exclude_record_id)

        existing_records = query.all()

        # Check each existing record
        for record in existing_records:
            # Get values for check fields
            record_values = {}
            for value in record.values:
                if value.field_name in check.check_fields:
                    record_values[value.field_name] = value.value

            # Compare with form data
            if check.check_logic == 'exact':
                is_match = all(
                    str(form_data.get(field)) == str(record_values.get(field))
                    for field in check.check_fields
                )
                if is_match:
                    return True

            elif check.check_logic == 'fuzzy':
                # Fuzzy matching
                similarity_threshold = (100 - check.tolerance) / 100.0
                total_similarity = 0
                count = 0

                for field in check.check_fields:
                    val1 = str(form_data.get(field, ''))
                    val2 = str(record_values.get(field, ''))

                    similarity = SequenceMatcher(None, val1, val2).ratio()
                    total_similarity += similarity
                    count += 1

                if count > 0 and (total_similarity / count) >= similarity_threshold:
                    return True

        return False

    def validate_calculated_field(
        self,
        field: FormField,
        all_data: Dict[str, Any]
    ) -> Any:
        """Calculate and validate calculated field"""
        if not field.formula:
            return None

        try:
            # Safe eval with limited context
            # Replace field names with values
            formula = field.formula
            for field_name, value in all_data.items():
                formula = formula.replace(f'{{{field_name}}}', str(value))

            # Simple arithmetic evaluation
            # Note: In production, use a safer expression evaluator
            result = eval(formula, {"__builtins__": {}}, {})
            return result

        except Exception as e:
            return None

    def get_validation_summary(self, template_id: int) -> Dict[str, Any]:
        """Get validation summary for a template"""
        template = self.db.query(FormTemplate).filter(
            FormTemplate.id == template_id
        ).first()

        if not template:
            return {}

        required_fields = []
        validated_fields = []

        for field in template.fields:
            if field.is_required:
                required_fields.append({
                    'field_name': field.field_name,
                    'field_label': field.field_label
                })

            if field.validation_rules or len(field.validation_rules_obj) > 0:
                validated_fields.append({
                    'field_name': field.field_name,
                    'field_label': field.field_label,
                    'rules': field.validation_rules
                })

        return {
            'template_id': template_id,
            'template_name': template.name,
            'required_fields': required_fields,
            'validated_fields': validated_fields,
            'total_fields': len(template.fields)
        }
