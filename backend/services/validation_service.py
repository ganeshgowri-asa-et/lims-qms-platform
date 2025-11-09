"""
Validation Service - Comprehensive field and cross-field validation
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from sqlalchemy.orm import Session
from backend.models import (
    FormField, FormFieldValidation, FormTemplate, FormRecord, FormValue,
    FormValidationHistory, ValidationSeverityEnum, DataQualityRule
)


class ValidationService:
    """Service for validating form data"""

    def __init__(self, db: Session):
        self.db = db
        self.errors = []
        self.warnings = []

    def validate_record(
        self,
        template_id: int,
        values: Dict[str, Any],
        record_id: Optional[int] = None
    ) -> Tuple[bool, List[Dict], List[Dict]]:
        """
        Validate form record data
        Returns: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Get template and fields
        template = self.db.query(FormTemplate).filter_by(id=template_id).first()
        if not template:
            self.errors.append({
                "field": "template",
                "message": f"Template with id {template_id} not found",
                "severity": "error"
            })
            return False, self.errors, self.warnings

        fields = self.db.query(FormField).filter_by(template_id=template_id).all()

        # Validate each field
        for field in fields:
            field_value = values.get(field.field_name)
            self._validate_field(field, field_value, values)

        # Cross-field validations
        self._validate_cross_field(fields, values)

        # Data quality rules
        self._validate_data_quality(template_id, values)

        # Save validation history if record exists
        if record_id:
            self._save_validation_history(record_id)

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_field(
        self,
        field: FormField,
        value: Any,
        all_values: Dict[str, Any]
    ) -> None:
        """Validate single field"""
        # Required field check
        if field.is_required and (value is None or value == "" or value == []):
            self.errors.append({
                "field": field.field_name,
                "message": f"{field.field_label} is required",
                "severity": "error",
                "rule": "required"
            })
            return

        # Skip further validation if field is empty and not required
        if value is None or value == "":
            return

        # Type-specific validation
        if field.field_type.value == "number":
            self._validate_number(field, value)
        elif field.field_type.value == "date":
            self._validate_date(field, value)
        elif field.field_type.value == "datetime":
            self._validate_datetime(field, value)
        elif field.field_type.value == "text":
            self._validate_text(field, value)
        elif field.field_type.value in ["dropdown", "radio"]:
            self._validate_options(field, value)
        elif field.field_type.value == "multiselect":
            self._validate_multiselect(field, value)
        elif field.field_type.value == "file":
            self._validate_file(field, value)

        # Custom validation rules from validation_rules JSON
        if field.validation_rules:
            self._validate_custom_rules(field, value)

        # Database validation rules
        validations = self.db.query(FormFieldValidation).filter_by(
            field_id=field.id,
            is_active=True
        ).order_by(FormFieldValidation.order).all()

        for validation in validations:
            self._apply_validation_rule(field, value, validation, all_values)

    def _validate_number(self, field: FormField, value: Any) -> None:
        """Validate numeric field"""
        try:
            num_value = float(value)

            # Check min/max from validation_rules
            if field.validation_rules:
                min_val = field.validation_rules.get("min")
                max_val = field.validation_rules.get("max")

                if min_val is not None and num_value < min_val:
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"{field.field_label} must be at least {min_val}",
                        "severity": "error",
                        "rule": "min"
                    })

                if max_val is not None and num_value > max_val:
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"{field.field_label} must be at most {max_val}",
                        "severity": "error",
                        "rule": "max"
                    })
        except (ValueError, TypeError):
            self.errors.append({
                "field": field.field_name,
                "message": f"{field.field_label} must be a valid number",
                "severity": "error",
                "rule": "type"
            })

    def _validate_date(self, field: FormField, value: Any) -> None:
        """Validate date field"""
        try:
            # Try parsing ISO format date
            datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            self.errors.append({
                "field": field.field_name,
                "message": f"{field.field_label} must be a valid date (YYYY-MM-DD)",
                "severity": "error",
                "rule": "format"
            })

    def _validate_datetime(self, field: FormField, value: Any) -> None:
        """Validate datetime field"""
        try:
            datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            self.errors.append({
                "field": field.field_name,
                "message": f"{field.field_label} must be a valid datetime",
                "severity": "error",
                "rule": "format"
            })

    def _validate_text(self, field: FormField, value: Any) -> None:
        """Validate text field"""
        text_value = str(value)

        if field.validation_rules:
            # Min/max length
            min_length = field.validation_rules.get("minLength")
            max_length = field.validation_rules.get("maxLength")

            if min_length is not None and len(text_value) < min_length:
                self.errors.append({
                    "field": field.field_name,
                    "message": f"{field.field_label} must be at least {min_length} characters",
                    "severity": "error",
                    "rule": "minLength"
                })

            if max_length is not None and len(text_value) > max_length:
                self.errors.append({
                    "field": field.field_name,
                    "message": f"{field.field_label} must be at most {max_length} characters",
                    "severity": "error",
                    "rule": "maxLength"
                })

            # Pattern validation
            pattern = field.validation_rules.get("pattern")
            if pattern:
                if not re.match(pattern, text_value):
                    error_msg = field.validation_rules.get("patternMessage",
                                                          f"{field.field_label} format is invalid")
                    self.errors.append({
                        "field": field.field_name,
                        "message": error_msg,
                        "severity": "error",
                        "rule": "pattern"
                    })

            # Email validation
            if field.validation_rules.get("email"):
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, text_value):
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"{field.field_label} must be a valid email address",
                        "severity": "error",
                        "rule": "email"
                    })

            # URL validation
            if field.validation_rules.get("url"):
                url_pattern = r'^https?://[^\s]+$'
                if not re.match(url_pattern, text_value):
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"{field.field_label} must be a valid URL",
                        "severity": "error",
                        "rule": "url"
                    })

    def _validate_options(self, field: FormField, value: Any) -> None:
        """Validate dropdown/radio selection"""
        if field.options:
            valid_options = [opt["value"] if isinstance(opt, dict) else opt
                           for opt in field.options]
            if value not in valid_options:
                self.errors.append({
                    "field": field.field_name,
                    "message": f"{field.field_label} must be one of: {', '.join(map(str, valid_options))}",
                    "severity": "error",
                    "rule": "options"
                })

    def _validate_multiselect(self, field: FormField, value: Any) -> None:
        """Validate multiselect field"""
        if not isinstance(value, list):
            self.errors.append({
                "field": field.field_name,
                "message": f"{field.field_label} must be a list",
                "severity": "error",
                "rule": "type"
            })
            return

        if field.options:
            valid_options = [opt["value"] if isinstance(opt, dict) else opt
                           for opt in field.options]
            for item in value:
                if item not in valid_options:
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"Invalid selection in {field.field_label}: {item}",
                        "severity": "error",
                        "rule": "options"
                    })

    def _validate_file(self, field: FormField, value: Any) -> None:
        """Validate file field"""
        if field.validation_rules:
            max_size = field.validation_rules.get("maxSize")
            allowed_types = field.validation_rules.get("allowedTypes")

            # These validations would be done during file upload
            # Here we just validate the file path/reference exists
            if isinstance(value, dict):
                if "path" not in value:
                    self.errors.append({
                        "field": field.field_name,
                        "message": f"{field.field_label} file path is missing",
                        "severity": "error",
                        "rule": "file"
                    })

    def _validate_custom_rules(self, field: FormField, value: Any) -> None:
        """Validate custom rules from validation_rules JSON"""
        rules = field.validation_rules

        # Custom validation expressions
        if "custom" in rules:
            custom_expr = rules["custom"]
            # Safe evaluation context
            context = {"value": value, "re": re}
            try:
                result = eval(custom_expr, {"__builtins__": {}}, context)
                if not result:
                    error_msg = rules.get("customMessage", f"{field.field_label} validation failed")
                    self.errors.append({
                        "field": field.field_name,
                        "message": error_msg,
                        "severity": "error",
                        "rule": "custom"
                    })
            except Exception as e:
                self.warnings.append({
                    "field": field.field_name,
                    "message": f"Custom validation error: {str(e)}",
                    "severity": "warning"
                })

    def _apply_validation_rule(
        self,
        field: FormField,
        value: Any,
        validation: FormFieldValidation,
        all_values: Dict[str, Any]
    ) -> None:
        """Apply database-defined validation rule"""
        val_type = validation.validation_type

        if val_type == "custom" and validation.custom_validator:
            # Execute custom validator
            context = {
                "value": value,
                "all_values": all_values,
                "re": re,
                "datetime": datetime
            }
            try:
                result = eval(validation.custom_validator, {"__builtins__": {}}, context)
                if not result:
                    error = {
                        "field": field.field_name,
                        "message": validation.error_message,
                        "severity": validation.severity.value,
                        "rule": val_type
                    }
                    if validation.severity == ValidationSeverityEnum.ERROR:
                        self.errors.append(error)
                    else:
                        self.warnings.append(error)
            except Exception as e:
                self.warnings.append({
                    "field": field.field_name,
                    "message": f"Validation execution error: {str(e)}",
                    "severity": "warning"
                })

    def _validate_cross_field(self, fields: List[FormField], values: Dict[str, Any]) -> None:
        """Validate cross-field dependencies"""
        # Get all cross-field validations
        field_ids = [f.id for f in fields]
        cross_validations = self.db.query(FormFieldValidation).filter(
            FormFieldValidation.field_id.in_(field_ids),
            FormFieldValidation.validation_type == 'cross_field',
            FormFieldValidation.is_active == True
        ).all()

        for validation in cross_validations:
            if validation.depends_on_fields:
                # Build context with all field values
                context = {"values": values, "datetime": datetime}
                try:
                    result = eval(validation.custom_validator, {"__builtins__": {}}, context)
                    if not result:
                        error = {
                            "field": "cross_field",
                            "message": validation.error_message,
                            "severity": validation.severity.value,
                            "rule": "cross_field",
                            "affected_fields": validation.depends_on_fields
                        }
                        if validation.severity == ValidationSeverityEnum.ERROR:
                            self.errors.append(error)
                        else:
                            self.warnings.append(error)
                except Exception as e:
                    self.warnings.append({
                        "field": "cross_field",
                        "message": f"Cross-field validation error: {str(e)}",
                        "severity": "warning"
                    })

    def _validate_data_quality(self, template_id: int, values: Dict[str, Any]) -> None:
        """Validate data quality rules"""
        rules = self.db.query(DataQualityRule).filter_by(
            template_id=template_id,
            is_active=True
        ).all()

        for rule in rules:
            context = {"values": values, "datetime": datetime, "re": re}
            try:
                result = eval(rule.rule_expression, {"__builtins__": {}}, context)
                if not result:
                    error = {
                        "field": "data_quality",
                        "message": f"{rule.rule_name}: {rule.description}",
                        "severity": rule.severity.value,
                        "rule": rule.rule_type,
                        "rule_name": rule.rule_name
                    }
                    if rule.severity == ValidationSeverityEnum.ERROR:
                        self.errors.append(error)
                    else:
                        self.warnings.append(error)
            except Exception as e:
                self.warnings.append({
                    "field": "data_quality",
                    "message": f"Data quality rule '{rule.rule_name}' error: {str(e)}",
                    "severity": "warning"
                })

    def _save_validation_history(self, record_id: int) -> None:
        """Save validation errors/warnings to history"""
        for error in self.errors:
            validation_history = FormValidationHistory(
                record_id=record_id,
                field_name=error.get("field", "unknown"),
                validation_rule=error.get("rule", "unknown"),
                severity=ValidationSeverityEnum.ERROR,
                error_message=error.get("message", ""),
                field_value=str(error.get("value", "")),
                is_resolved=False
            )
            self.db.add(validation_history)

        for warning in self.warnings:
            validation_history = FormValidationHistory(
                record_id=record_id,
                field_name=warning.get("field", "unknown"),
                validation_rule=warning.get("rule", "unknown"),
                severity=ValidationSeverityEnum.WARNING,
                error_message=warning.get("message", ""),
                field_value=str(warning.get("value", "")),
                is_resolved=True  # Warnings are auto-resolved
            )
            self.db.add(validation_history)

        self.db.commit()

    def check_duplicates(
        self,
        template_id: int,
        values: Dict[str, Any],
        exclude_record_id: Optional[int] = None
    ) -> List[Dict]:
        """Check for duplicate records"""
        from backend.models import DuplicateDetectionConfig

        config = self.db.query(DuplicateDetectionConfig).filter_by(
            template_id=template_id,
            is_active=True
        ).first()

        if not config:
            return []

        duplicates = []

        # Build query to find duplicates
        for field_combo in config.field_combinations:
            # Get all records with matching field values
            query = self.db.query(FormRecord).filter_by(template_id=template_id)

            if exclude_record_id:
                query = query.filter(FormRecord.id != exclude_record_id)

            # Check time window if configured
            if config.time_window_hours:
                from datetime import datetime, timedelta
                cutoff = datetime.utcnow() - timedelta(hours=config.time_window_hours)
                query = query.filter(FormRecord.created_at >= cutoff.isoformat())

            records = query.all()

            # Check each record for matching field values
            for record in records:
                match = True
                for field_name in field_combo:
                    record_value = self._get_field_value(record.id, field_name)
                    new_value = values.get(field_name)

                    if config.detection_method == "exact":
                        if record_value != new_value:
                            match = False
                            break
                    # Fuzzy and phonetic matching would require additional libraries

                if match:
                    duplicates.append({
                        "record_id": record.id,
                        "record_number": record.record_number,
                        "matching_fields": field_combo,
                        "action": config.action
                    })

        return duplicates

    def _get_field_value(self, record_id: int, field_name: str) -> Any:
        """Get field value from a record"""
        value = self.db.query(FormValue).filter_by(
            record_id=record_id,
            field_name=field_name
        ).first()

        if value:
            return value.value_json if value.value_json else value.value
        return None

    def calculate_completion_percentage(self, template_id: int, values: Dict[str, Any]) -> int:
        """Calculate form completion percentage"""
        fields = self.db.query(FormField).filter_by(template_id=template_id).all()

        if not fields:
            return 0

        total_fields = len(fields)
        filled_fields = 0

        for field in fields:
            value = values.get(field.field_name)
            if value is not None and value != "" and value != []:
                filled_fields += 1

        return int((filled_fields / total_fields) * 100)

    def calculate_validation_score(self, errors: List[Dict], warnings: List[Dict]) -> int:
        """Calculate validation score (100 = perfect, 0 = many errors)"""
        error_weight = 10
        warning_weight = 2

        score = 100 - (len(errors) * error_weight) - (len(warnings) * warning_weight)
        return max(0, min(100, score))
