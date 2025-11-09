"""
Automatic document numbering service
Generates document numbers in format: QSF-YYYY-XXX
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.document import QMSDocument, DocumentType


class DocumentNumbering:
    """
    Handles automatic document number generation
    Format: QSF-YYYY-XXX
    Where:
    - QSF: Quality System Form/Document prefix
    - YYYY: Current year
    - XXX: Sequential 3-digit number (001-999)
    """

    PREFIX = "QSF"

    @classmethod
    def generate_document_number(cls, db: Session, doc_type: DocumentType = None) -> str:
        """
        Generate next available document number for the current year

        Args:
            db: Database session
            doc_type: Optional document type for type-specific numbering

        Returns:
            Document number in format QSF-YYYY-XXX
        """
        current_year = datetime.now().year

        # Get the highest document number for current year
        pattern = f"{cls.PREFIX}-{current_year}-%"

        max_doc = db.query(QMSDocument).filter(
            QMSDocument.doc_number.like(pattern)
        ).order_by(
            QMSDocument.doc_number.desc()
        ).first()

        if max_doc:
            # Extract the sequence number from the last document
            try:
                last_number = int(max_doc.doc_number.split("-")[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1

        # Format the document number
        doc_number = f"{cls.PREFIX}-{current_year}-{next_number:03d}"

        return doc_number

    @classmethod
    def validate_document_number(cls, doc_number: str) -> bool:
        """
        Validate document number format

        Args:
            doc_number: Document number to validate

        Returns:
            True if valid, False otherwise
        """
        if not doc_number:
            return False

        parts = doc_number.split("-")

        if len(parts) != 3:
            return False

        prefix, year, sequence = parts

        # Check prefix
        if prefix != cls.PREFIX:
            return False

        # Check year (4 digits)
        try:
            year_int = int(year)
            if year_int < 2000 or year_int > 2100:
                return False
        except ValueError:
            return False

        # Check sequence (3 digits)
        try:
            seq_int = int(sequence)
            if seq_int < 1 or seq_int > 999:
                return False
        except ValueError:
            return False

        return True

    @classmethod
    def parse_document_number(cls, doc_number: str) -> dict:
        """
        Parse document number into components

        Args:
            doc_number: Document number to parse

        Returns:
            Dictionary with prefix, year, and sequence
        """
        if not cls.validate_document_number(doc_number):
            raise ValueError(f"Invalid document number format: {doc_number}")

        prefix, year, sequence = doc_number.split("-")

        return {
            "prefix": prefix,
            "year": int(year),
            "sequence": int(sequence),
            "full_number": doc_number
        }

    @classmethod
    def get_next_revision_number(cls, db: Session, document_id: int) -> int:
        """
        Get the next revision number for a document

        Args:
            db: Database session
            document_id: Document ID

        Returns:
            Next revision number
        """
        from app.models.document import DocumentRevision

        max_revision = db.query(func.max(DocumentRevision.revision_number)).filter(
            DocumentRevision.document_id == document_id
        ).scalar()

        return (max_revision or 0) + 1
