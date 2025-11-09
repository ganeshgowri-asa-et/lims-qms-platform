"""
Number Sequence model for auto-numbering
"""
from sqlalchemy import Column, String, Integer, Index
from app.database import Base
from app.models.base import BaseModel


class NumberSequence(Base, BaseModel):
    """Manages auto-increment sequences for document numbers"""
    __tablename__ = "number_sequences"

    prefix = Column(String(10), nullable=False)  # TRQ, SMP, QTE, etc.
    year = Column(Integer, nullable=False)
    current_sequence = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index('idx_prefix_year', 'prefix', 'year', unique=True),
    )

    def __repr__(self):
        return f"<NumberSequence {self.prefix}-{self.year}: {self.current_sequence}>"
