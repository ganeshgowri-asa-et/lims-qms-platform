"""
Sample model for LIMS/QMS platform
"""
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import BaseModel


class Sample(Base, BaseModel):
    """Sample table for tracking test samples"""
    __tablename__ = "samples"

    # Auto-generated Sample number (SMP-YYYY-XXXXX)
    sample_number = Column(String(20), unique=True, nullable=False, index=True)

    # Test Request Reference
    test_request_id = Column(Integer, ForeignKey("test_requests.id"), nullable=False)

    # Sample Details
    sample_name = Column(String(255), nullable=False)
    sample_type = Column(String(100), nullable=False)  # solid, liquid, gas, etc.
    sample_description = Column(Text, nullable=True)

    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)  # mg, g, kg, ml, L, pieces, etc.

    # Sample Condition
    condition_on_receipt = Column(String(255), nullable=True)
    storage_condition = Column(String(255), nullable=True)
    expiry_date = Column(Date, nullable=True)

    # Batch/Lot Information
    batch_number = Column(String(100), nullable=True)
    lot_number = Column(String(100), nullable=True)
    manufacturing_date = Column(Date, nullable=True)

    # Tracking
    status = Column(String(50), nullable=False, default="pending")
    received_date = Column(Date, nullable=True)
    received_by = Column(String(255), nullable=True)
    testing_start_date = Column(Date, nullable=True)
    testing_end_date = Column(Date, nullable=True)

    # Barcode
    barcode_data = Column(Text, nullable=True)  # Base64 encoded barcode image

    # Location
    storage_location = Column(String(255), nullable=True)

    # Remarks
    remarks = Column(Text, nullable=True)

    # Relationships
    test_request = relationship("TestRequest", back_populates="samples")

    def __repr__(self):
        return f"<Sample {self.sample_number}: {self.sample_name}>"
