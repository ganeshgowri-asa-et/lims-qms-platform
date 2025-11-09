"""
Document Numbering Service
Handles automatic and manual document number generation
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.models.document import (
    DocumentNumberSequence,
    DocumentLevel,
    DocumentLevelEnum
)


class NumberingService:
    """Service for generating document numbers"""

    def __init__(self, db: Session):
        self.db = db

    def generate_document_number(
        self,
        level: DocumentLevelEnum,
        category: Optional[str] = None,
        manual_number: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None
    ) -> str:
        """
        Generate document number based on level and category

        Format examples:
        - L1-QM-2024-0001 (Level 1, Quality Manual, 2024, sequence)
        - L2-ISO17025-2024-0012 (Level 2, ISO 17025, 2024, sequence)
        - L4-FORM-CAL-2024-0045 (Level 4, Form, Calibration category, 2024, sequence)

        Args:
            level: Document level (1-5)
            category: Document category (optional)
            manual_number: Manual override (optional)
            prefix: Custom prefix (optional)
            suffix: Custom suffix (optional)

        Returns:
            Generated document number
        """
        # If manual number provided, validate and return
        if manual_number:
            if self._is_number_available(manual_number):
                return manual_number
            else:
                raise ValueError(f"Document number {manual_number} already exists")

        # Get level configuration
        level_config = self._get_level_config(level)

        # If auto-numbering is disabled, raise error
        if level_config and not level_config.auto_numbering:
            raise ValueError(f"Auto-numbering is disabled for {level.value}. Please provide manual number.")

        # Get or create sequence
        year = datetime.now().year
        sequence = self._get_or_create_sequence(level, category, year)

        # Increment sequence
        sequence.current_sequence += 1
        self.db.commit()

        # Build document number
        return self._build_document_number(
            level=level,
            category=category,
            year=year,
            sequence=sequence.current_sequence,
            prefix=prefix or sequence.prefix,
            suffix=suffix or sequence.suffix,
            format_template=level_config.numbering_format if level_config else None
        )

    def _get_level_config(self, level: DocumentLevelEnum) -> Optional[DocumentLevel]:
        """Get level configuration"""
        level_number = int(level.value.split()[1])  # Extract number from "Level 1"
        return self.db.query(DocumentLevel).filter(
            DocumentLevel.level_number == level_number
        ).first()

    def _get_or_create_sequence(
        self,
        level: DocumentLevelEnum,
        category: Optional[str],
        year: int
    ) -> DocumentNumberSequence:
        """Get or create sequence for level/category/year"""
        sequence = self.db.query(DocumentNumberSequence).filter(
            and_(
                DocumentNumberSequence.level == level,
                DocumentNumberSequence.category == category,
                DocumentNumberSequence.year == year
            )
        ).first()

        if not sequence:
            sequence = DocumentNumberSequence(
                level=level,
                category=category,
                year=year,
                current_sequence=0,
                prefix=self._default_prefix(level, category),
                format_template=self._default_format_template(level, category)
            )
            self.db.add(sequence)
            self.db.commit()
            self.db.refresh(sequence)

        return sequence

    def _build_document_number(
        self,
        level: DocumentLevelEnum,
        category: Optional[str],
        year: int,
        sequence: int,
        prefix: Optional[str],
        suffix: Optional[str],
        format_template: Optional[str]
    ) -> str:
        """Build document number from components"""
        level_number = int(level.value.split()[1])

        # If custom format template provided, use it
        if format_template:
            return self._apply_format_template(
                format_template,
                level_number,
                category,
                year,
                sequence,
                prefix,
                suffix
            )

        # Default format: L{level}-{category}-{year}-{seq:04d}
        parts = []

        # Add prefix
        if prefix:
            parts.append(prefix)

        # Add level
        parts.append(f"L{level_number}")

        # Add category if provided
        if category:
            parts.append(category.upper())

        # Add year
        parts.append(str(year))

        # Add sequence (padded to 4 digits)
        parts.append(f"{sequence:04d}")

        # Add suffix
        if suffix:
            parts.append(suffix)

        return "-".join(parts)

    def _apply_format_template(
        self,
        template: str,
        level: int,
        category: Optional[str],
        year: int,
        sequence: int,
        prefix: Optional[str],
        suffix: Optional[str]
    ) -> str:
        """
        Apply format template with placeholders

        Supported placeholders:
        - {level} - Level number
        - {category} - Category code
        - {year} - Full year (2024)
        - {yy} - Short year (24)
        - {seq} - Sequence number
        - {seq:04d} - Padded sequence (0001)
        - {prefix} - Custom prefix
        - {suffix} - Custom suffix
        - {month} - Current month (01-12)
        """
        replacements = {
            '{level}': str(level),
            '{category}': (category or '').upper(),
            '{year}': str(year),
            '{yy}': str(year)[2:],
            '{seq}': str(sequence),
            '{prefix}': prefix or '',
            '{suffix}': suffix or '',
            '{month}': f"{datetime.now().month:02d}"
        }

        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)

        # Handle formatted sequence (e.g., {seq:04d})
        if '{seq:' in result:
            import re
            pattern = r'\{seq:(\d+)d\}'
            match = re.search(pattern, result)
            if match:
                width = int(match.group(1))
                formatted_seq = f"{sequence:0{width}d}"
                result = re.sub(pattern, formatted_seq, result)

        return result

    def _default_prefix(self, level: DocumentLevelEnum, category: Optional[str]) -> str:
        """Generate default prefix based on level and category"""
        level_number = int(level.value.split()[1])
        if category:
            return f"L{level_number}-{category[:3].upper()}"
        return f"L{level_number}"

    def _default_format_template(self, level: DocumentLevelEnum, category: Optional[str]) -> str:
        """Generate default format template"""
        if category:
            return "L{level}-{category}-{year}-{seq:04d}"
        return "L{level}-{year}-{seq:04d}"

    def _is_number_available(self, document_number: str) -> bool:
        """Check if document number is available"""
        from backend.models.document import Document
        existing = self.db.query(Document).filter(
            Document.document_number == document_number
        ).first()
        return existing is None

    def validate_document_number(self, document_number: str) -> bool:
        """Validate document number format"""
        # Basic validation: should not be empty, should follow general pattern
        if not document_number or len(document_number) < 5:
            return False

        # Should contain at least one hyphen
        if '-' not in document_number:
            return False

        return True

    def reserve_number(
        self,
        level: DocumentLevelEnum,
        category: Optional[str] = None
    ) -> str:
        """
        Reserve a document number without creating a document
        Useful for pre-allocation
        """
        return self.generate_document_number(level, category)

    def get_next_number_preview(
        self,
        level: DocumentLevelEnum,
        category: Optional[str] = None
    ) -> str:
        """
        Preview the next document number without incrementing sequence
        """
        year = datetime.now().year
        sequence = self._get_or_create_sequence(level, category, year)
        level_config = self._get_level_config(level)

        return self._build_document_number(
            level=level,
            category=category,
            year=year,
            sequence=sequence.current_sequence + 1,
            prefix=sequence.prefix,
            suffix=sequence.suffix,
            format_template=level_config.numbering_format if level_config else None
        )

    def reset_sequence(
        self,
        level: DocumentLevelEnum,
        category: Optional[str] = None,
        year: Optional[int] = None
    ) -> bool:
        """Reset sequence counter (admin function)"""
        year = year or datetime.now().year
        sequence = self.db.query(DocumentNumberSequence).filter(
            and_(
                DocumentNumberSequence.level == level,
                DocumentNumberSequence.category == category,
                DocumentNumberSequence.year == year
            )
        ).first()

        if sequence:
            sequence.current_sequence = 0
            self.db.commit()
            return True
        return False

    def get_sequence_status(
        self,
        level: DocumentLevelEnum,
        category: Optional[str] = None,
        year: Optional[int] = None
    ) -> dict:
        """Get current sequence status"""
        year = year or datetime.now().year
        sequence = self._get_or_create_sequence(level, category, year)

        return {
            'level': level.value,
            'category': category,
            'year': year,
            'current_sequence': sequence.current_sequence,
            'next_number': self.get_next_number_preview(level, category),
            'prefix': sequence.prefix,
            'suffix': sequence.suffix,
            'format_template': sequence.format_template
        }
