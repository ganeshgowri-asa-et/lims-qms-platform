"""
Template Service
Dynamic template indexing and management for Level 4 templates
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from backend.models.document import (
    Document,
    TemplateIndex,
    DocumentLevelEnum,
    DocumentTypeEnum
)
import os
import json


class TemplateService:
    """Service for managing document templates"""

    def __init__(self, db: Session):
        self.db = db

    def index_template(
        self,
        document_id: int,
        template_name: str,
        template_code: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        is_dynamic: bool = False,
        fields_schema: Optional[dict] = None,
        validation_rules: Optional[dict] = None,
        search_keywords: Optional[List[str]] = None,
        description: Optional[str] = None,
        auto_indexed: bool = True
    ) -> dict:
        """
        Index a template for quick search and usage

        Args:
            document_id: Document ID of the template
            template_name: Name of the template
            template_code: Unique template code
            category: Template category
            subcategory: Template subcategory
            is_dynamic: Whether template has dynamic fields
            fields_schema: JSON schema for template fields
            validation_rules: Validation rules for fields
            search_keywords: Keywords for search optimization
            description: Template description
            auto_indexed: Whether automatically indexed

        Returns:
            Index information
        """
        # Validate document exists and is a template
        document = self._get_document(document_id)

        if not document.is_template:
            raise ValueError("Document is not marked as a template")

        # Check if already indexed
        existing = self.db.query(TemplateIndex).filter(
            TemplateIndex.document_id == document_id
        ).first()

        if existing:
            raise ValueError("Template already indexed")

        # Create template index
        template_index = TemplateIndex(
            document_id=document_id,
            template_name=template_name,
            template_code=template_code,
            category=category,
            subcategory=subcategory,
            is_dynamic=is_dynamic,
            fields_schema=fields_schema,
            validation_rules=validation_rules,
            search_keywords=search_keywords,
            description=description,
            auto_indexed=auto_indexed
        )

        self.db.add(template_index)
        self.db.commit()
        self.db.refresh(template_index)

        return {
            'status': 'success',
            'message': 'Template indexed successfully',
            'index_id': template_index.id,
            'template_code': template_code
        }

    def auto_index_templates(self, template_directory: Optional[str] = None) -> dict:
        """
        Automatically index all Level 4 templates in the system

        Args:
            template_directory: Directory to scan for templates

        Returns:
            Indexing results
        """
        # Get all Level 4 documents marked as templates
        templates = self.db.query(Document).filter(
            and_(
                Document.level == DocumentLevelEnum.LEVEL_4,
                Document.is_template == True,
                Document.is_deleted == False
            )
        ).all()

        indexed_count = 0
        skipped_count = 0
        errors = []

        for doc in templates:
            # Check if already indexed
            existing = self.db.query(TemplateIndex).filter(
                TemplateIndex.document_id == doc.id
            ).first()

            if existing:
                skipped_count += 1
                continue

            try:
                # Extract metadata from document
                template_code = self._generate_template_code(doc)
                category = doc.category or "General"
                keywords = self._extract_keywords(doc)

                # Create index
                template_index = TemplateIndex(
                    document_id=doc.id,
                    template_name=doc.title,
                    template_code=template_code,
                    category=category,
                    is_dynamic=False,
                    search_keywords=keywords,
                    description=doc.description,
                    auto_indexed=True
                )

                self.db.add(template_index)
                indexed_count += 1

            except Exception as e:
                errors.append({
                    'document_id': doc.id,
                    'document_number': doc.document_number,
                    'error': str(e)
                })

        if indexed_count > 0:
            self.db.commit()

        return {
            'status': 'success',
            'indexed': indexed_count,
            'skipped': skipped_count,
            'errors': errors,
            'total_templates': len(templates)
        }

    def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        is_dynamic: Optional[bool] = None,
        limit: int = 50
    ) -> List[dict]:
        """
        Search templates by various criteria

        Args:
            query: Search query (searches name, code, keywords, description)
            category: Filter by category
            subcategory: Filter by subcategory
            is_dynamic: Filter by dynamic flag
            limit: Maximum results to return

        Returns:
            List of matching templates
        """
        db_query = self.db.query(TemplateIndex).join(Document)

        # Apply filters
        if query:
            db_query = db_query.filter(
                or_(
                    TemplateIndex.template_name.ilike(f'%{query}%'),
                    TemplateIndex.template_code.ilike(f'%{query}%'),
                    TemplateIndex.description.ilike(f'%{query}%'),
                    Document.title.ilike(f'%{query}%')
                )
            )

        if category:
            db_query = db_query.filter(TemplateIndex.category == category)

        if subcategory:
            db_query = db_query.filter(TemplateIndex.subcategory == subcategory)

        if is_dynamic is not None:
            db_query = db_query.filter(TemplateIndex.is_dynamic == is_dynamic)

        # Execute query
        templates = db_query.limit(limit).all()

        results = []
        for template in templates:
            doc = self._get_document(template.document_id)
            results.append({
                'id': template.id,
                'document_id': doc.id,
                'document_number': doc.document_number,
                'template_name': template.template_name,
                'template_code': template.template_code,
                'category': template.category,
                'subcategory': template.subcategory,
                'is_dynamic': template.is_dynamic,
                'usage_count': template.usage_count,
                'last_used': template.last_used_at.isoformat() if template.last_used_at else None,
                'description': template.description,
                'file_path': doc.file_path
            })

        return results

    def get_template_by_code(self, template_code: str) -> dict:
        """Get template by unique code"""
        template = self.db.query(TemplateIndex).filter(
            TemplateIndex.template_code == template_code
        ).first()

        if not template:
            raise ValueError(f"Template not found: {template_code}")

        doc = self._get_document(template.document_id)

        return {
            'id': template.id,
            'document_id': doc.id,
            'document_number': doc.document_number,
            'template_name': template.template_name,
            'template_code': template.template_code,
            'category': template.category,
            'subcategory': template.subcategory,
            'is_dynamic': template.is_dynamic,
            'fields_schema': template.fields_schema,
            'validation_rules': template.validation_rules,
            'usage_count': template.usage_count,
            'description': template.description,
            'file_path': doc.file_path,
            'file_type': doc.file_type
        }

    def increment_usage(self, template_code: str) -> bool:
        """Increment template usage counter"""
        template = self.db.query(TemplateIndex).filter(
            TemplateIndex.template_code == template_code
        ).first()

        if template:
            template.usage_count += 1
            template.last_used_at = datetime.now()
            self.db.commit()
            return True
        return False

    def get_popular_templates(self, limit: int = 10) -> List[dict]:
        """Get most popular templates by usage"""
        templates = self.db.query(TemplateIndex).order_by(
            TemplateIndex.usage_count.desc()
        ).limit(limit).all()

        results = []
        for template in templates:
            doc = self._get_document(template.document_id)
            results.append({
                'template_code': template.template_code,
                'template_name': template.template_name,
                'category': template.category,
                'usage_count': template.usage_count,
                'last_used': template.last_used_at.isoformat() if template.last_used_at else None,
                'document_number': doc.document_number
            })

        return results

    def get_template_categories(self) -> List[dict]:
        """Get all template categories with counts"""
        from sqlalchemy import func

        results = self.db.query(
            TemplateIndex.category,
            func.count(TemplateIndex.id).label('count')
        ).group_by(TemplateIndex.category).all()

        return [
            {'category': cat, 'count': count}
            for cat, count in results
        ]

    def update_template_schema(
        self,
        template_code: str,
        fields_schema: dict,
        validation_rules: Optional[dict] = None
    ) -> dict:
        """Update template field schema and validation rules"""
        template = self.db.query(TemplateIndex).filter(
            TemplateIndex.template_code == template_code
        ).first()

        if not template:
            raise ValueError(f"Template not found: {template_code}")

        template.fields_schema = fields_schema
        template.is_dynamic = True

        if validation_rules:
            template.validation_rules = validation_rules

        self.db.commit()

        return {
            'status': 'success',
            'message': 'Template schema updated',
            'template_code': template_code
        }

    def validate_template_data(
        self,
        template_code: str,
        data: dict
    ) -> dict:
        """
        Validate data against template schema

        Args:
            template_code: Template code
            data: Data to validate

        Returns:
            Validation result
        """
        template = self.db.query(TemplateIndex).filter(
            TemplateIndex.template_code == template_code
        ).first()

        if not template:
            raise ValueError(f"Template not found: {template_code}")

        if not template.is_dynamic or not template.fields_schema:
            return {
                'valid': True,
                'message': 'Template has no validation schema'
            }

        # Validate against schema
        errors = []
        schema = template.fields_schema

        # Check required fields
        required_fields = [f for f, props in schema.items() if props.get('required', False)]
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Required field missing: {field}")

        # Check field types
        for field, value in data.items():
            if field in schema:
                expected_type = schema[field].get('type')
                if expected_type and not self._check_type(value, expected_type):
                    errors.append(f"Invalid type for field {field}: expected {expected_type}")

        # Apply validation rules if present
        if template.validation_rules:
            for field, rules in template.validation_rules.items():
                if field in data:
                    value = data[field]
                    for rule_name, rule_value in rules.items():
                        if rule_name == 'min_length' and len(str(value)) < rule_value:
                            errors.append(f"{field}: minimum length is {rule_value}")
                        elif rule_name == 'max_length' and len(str(value)) > rule_value:
                            errors.append(f"{field}: maximum length is {rule_value}")
                        elif rule_name == 'pattern' and not self._match_pattern(str(value), rule_value):
                            errors.append(f"{field}: does not match required pattern")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'message': 'Validation passed' if len(errors) == 0 else 'Validation failed'
        }

    def _generate_template_code(self, document: Document) -> str:
        """Generate template code from document metadata"""
        # Format: TMPL-{CATEGORY}-{SEQUENCE}
        category_code = (document.category or 'GEN')[:3].upper()

        # Get count of templates in same category
        count = self.db.query(TemplateIndex).filter(
            TemplateIndex.category == document.category
        ).count()

        return f"TMPL-{category_code}-{count + 1:04d}"

    def _extract_keywords(self, document: Document) -> List[str]:
        """Extract keywords from document for search"""
        keywords = []

        # Add from title
        if document.title:
            keywords.extend(document.title.lower().split())

        # Add from description
        if document.description:
            keywords.extend(document.description.lower().split()[:10])

        # Add from tags
        if document.tags:
            keywords.extend(document.tags)

        # Add category
        if document.category:
            keywords.append(document.category.lower())

        # Remove duplicates and common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = list(set([k for k in keywords if k not in stop_words]))

        return keywords[:20]  # Limit to 20 keywords

    def _check_type(self, value, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict
        }

        expected = type_map.get(expected_type)
        if expected:
            return isinstance(value, expected)
        return True

    def _match_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches regex pattern"""
        import re
        try:
            return bool(re.match(pattern, value))
        except:
            return False

    def _get_document(self, document_id: int) -> Document:
        """Get document or raise error"""
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.is_deleted == False
        ).first()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        return document
