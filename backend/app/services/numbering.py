"""
Auto-numbering service for generating document numbers
Format: PREFIX-YYYY-XXXXX (e.g., TRQ-2025-00001)
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.number_sequence import NumberSequence
from app.utils.constants import DocPrefix
from app.config import settings


class NumberingService:
    """Service for auto-generating document numbers"""

    @staticmethod
    def _get_next_sequence(db: Session, prefix: str) -> str:
        """
        Get next sequence number for a given prefix
        Format: PREFIX-YYYY-XXXXX

        Args:
            db: Database session
            prefix: Document prefix (TRQ, SMP, etc.)

        Returns:
            Formatted document number
        """
        current_year = datetime.now().year

        # Find or create sequence record for this prefix and year
        sequence = db.query(NumberSequence).filter(
            and_(
                NumberSequence.prefix == prefix,
                NumberSequence.year == current_year
            )
        ).first()

        if not sequence:
            # Create new sequence for this year
            sequence = NumberSequence(
                prefix=prefix,
                year=current_year,
                current_sequence=1,
                created_by="system"
            )
            db.add(sequence)
        else:
            # Increment existing sequence
            sequence.current_sequence += 1

        db.commit()
        db.refresh(sequence)

        # Format: PREFIX-YYYY-XXXXX (5 digits)
        padding = settings.SEQUENCE_PADDING
        doc_number = f"{prefix}-{current_year}-{sequence.current_sequence:0{padding}d}"

        return doc_number

    @staticmethod
    def generate_test_request_number(db: Session) -> str:
        """
        Generate Test Request number
        Format: TRQ-2025-00001

        Args:
            db: Database session

        Returns:
            Test request number
        """
        return NumberingService._get_next_sequence(db, DocPrefix.TEST_REQUEST)

    @staticmethod
    def generate_sample_number(db: Session) -> str:
        """
        Generate Sample number
        Format: SMP-2025-00001

        Args:
            db: Database session

        Returns:
            Sample number
        """
        return NumberingService._get_next_sequence(db, DocPrefix.SAMPLE)

    @staticmethod
    def generate_quote_number(db: Session) -> str:
        """
        Generate Quote number
        Format: QTE-2025-00001

        Args:
            db: Database session

        Returns:
            Quote number
        """
        return NumberingService._get_next_sequence(db, DocPrefix.QUOTE)

    @staticmethod
    def get_current_sequence(db: Session, prefix: str) -> int:
        """
        Get current sequence number for a prefix (without incrementing)

        Args:
            db: Database session
            prefix: Document prefix

        Returns:
            Current sequence number
        """
        current_year = datetime.now().year

        sequence = db.query(NumberSequence).filter(
            and_(
                NumberSequence.prefix == prefix,
                NumberSequence.year == current_year
            )
        ).first()

        return sequence.current_sequence if sequence else 0
